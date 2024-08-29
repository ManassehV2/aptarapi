from collections import defaultdict
import math
import os
import time
import cv2
import redis
from celery import Celery
from sqlalchemy import desc
from sqlalchemy.orm import Session
from ultralytics import YOLO

from app.database import SessionLocal
from app.models import Incident
from .celery import celery_app
from . import crud, schemas
from datetime import datetime, timezone
from app.celery import celery_app


# Redis setup for signaling the stop command
redis_client = redis.Redis(host='localhost', port=6379, db=0)

# Initialize a cache to store the last detection timestamp for each class and recording
detection_cache = defaultdict(lambda: None)

def compute_center(box):
    """Compute the center (x, y) of a bounding box."""
    center_x = (box[0] + box[2]) / 2
    center_y = (box[1] + box[3]) / 2
    return (center_x, center_y)

def compute_euclidean_distance(boxA, boxB):
    """Compute the Euclidean distance between the centers of two bounding boxes."""
    centerA = compute_center(boxA)
    centerB = compute_center(boxB)
    
    distance = math.sqrt((centerA[0] - centerB[0]) ** 2 + (centerA[1] - centerB[1]) ** 2)
    return distance

def check_proximity(person_box, forklift_box, threshold_distance=50):
    """Check if the Euclidean distance between the centers of a person and a forklift is less than a threshold."""
    distance = compute_euclidean_distance(person_box, forklift_box)
    return distance < threshold_distance

def handle_proximity_detections(model, frame, confidence, proximity_threshold=350):
    results = model(frame)
    detections = results[0].boxes
    person_boxes = []
    forklift_boxes = []
    detected_classes = {}

    for det in detections:
        try:
            box = det.xyxy[0].tolist()  # Get the bounding box coordinates
            conf = det.conf[0].item()
            cls = int(det.cls[0].item())
            class_name = model.names[cls]

            if conf >= confidence:
                detected_classes[class_name] = conf  # Store detected class with confidence

                # Draw bounding box on the frame for every detected object
                pt1 = (int(box[0]), int(box[1]))
                pt2 = (int(box[2]), int(box[3]))
                cv2.rectangle(frame, pt1, pt2, (255, 0, 0), 2)  # Draw rectangle
                label = f'{class_name} {conf:.2f}'
                cv2.putText(frame, label, (int(box[0]), int(box[1]) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)  # Draw label

                if class_name == 'person':
                    person_boxes.append(box)
                elif class_name == 'forklift':
                    forklift_boxes.append(box)

        except Exception as e:
            print(f"Error processing detection: {e}")
            continue

    # Check for proximity between persons and forklifts
    for person_box in person_boxes:
        for forklift_box in forklift_boxes:
            if check_proximity(person_box, forklift_box, proximity_threshold):
                print("Person detected near a forklift!")
                return frame, True, detected_classes

    return frame, False, detected_classes

def save_proximity_detection(db, buffer, record_id, detected_classes):
    current_timestamp = datetime.now(timezone.utc)  # Get the current timestamp once
    class_name = 'person_forklift_proximity'
    cache_key = f"{record_id}_{class_name}"

    if should_skip_detection(cache_key, db, record_id, class_name, current_timestamp, debounce_time_seconds=1*60):
        return

    detection_cache[cache_key] = current_timestamp

    db_detection = Incident(
        recording_id=record_id,
        class_name=class_name,
        confidence=0.0,  # Set confidence to 0 as it's a proximity event
        bbox='',  # Optionally save bounding box info
        frame=buffer.tobytes(),
        timestamp=current_timestamp
    )

    try:
        db.add(db_detection)
        db.commit()
        print(f"Proximity incident saved to DB: {db_detection}")
    except Exception as e:
        print(f"Error saving to DB: {e}")
        db.rollback()



def initialize_camera(ip_cam_url=None):
    cap = None
    # Try to open the IP camera first if the URL is provided
    if ip_cam_url is not None:
        cap = cv2.VideoCapture(ip_cam_url)
        if cap.isOpened():
            print(f"Connected to IP camera at {ip_cam_url}")
            return cap
        else:
            print(f"Failed to connect to IP camera at {ip_cam_url}. Falling back to the webcam.")
    
    # If IP camera connection fails or no URL is provided, try the webcam
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise RuntimeError("Could not open webcam or IP camera")
    
    print("Connected to the default webcam.")
    return cap

def initialize_camera2(ip_cam_url=None, video_file_path=None):
    cap = None
    
    # Try to open the IP camera first if the URL is provided
    if ip_cam_url is not None:
        cap = cv2.VideoCapture(ip_cam_url)
        if cap.isOpened():
            print(f"Connected to IP camera at {ip_cam_url}")
            return cap
        else:
            print(f"Failed to connect to IP camera at {ip_cam_url}.")
    
    # If IP camera connection fails, try to open the video file if the path is provided
    if video_file_path is not None:
        cap = cv2.VideoCapture(video_file_path)
        if cap.isOpened():
            print(f"Connected to video file at {video_file_path}")
            return cap
        else:
            print(f"Failed to open video file at {video_file_path}.")
    
    # If both IP camera and video file connection fail, try the webcam
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise RuntimeError("Could not open webcam, IP camera, or video file")
    
    print("Connected to the default webcam.")
    return cap


def process_frame(cap):
    ret, frame = cap.read()
    if not ret:
        raise OSError("Failed to capture frame from webcam")
    frame = cv2.resize(frame, (640, 480))
    return frame

def handle_detections(model, frame, zoneconf, zonescenarios):
    results = model(frame)
    detections = results[0].boxes
    detected_classes = {}
    person_detected = False

    for det in detections:
        try:
            box = det.xyxy[0].tolist()  # Get the bounding box coordinates
            conf = det.conf[0].item()
            cls = int(det.cls[0].item())
            class_name = model.names[cls]

            if conf >= zoneconf:
                detected_classes[class_name] = conf  # Store detected class with confidence
                
                # Draw bounding box on the frame for every detected object
                pt1 = (int(box[0]), int(box[1]))
                pt2 = (int(box[2]), int(box[3]))
                cv2.rectangle(frame, pt1, pt2, (255, 0, 0), 2)  # Draw rectangle
                label = f'{class_name} {conf:.2f}'
                cv2.putText(frame, label, (int(box[0]), int(box[1]) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)  # Draw label

                if class_name == 'person':
                    person_detected = True  # Mark that a person is detected

        except Exception as e:
            print(f"Error processing detection: {e}")
            continue

    if not person_detected:
        print("No person detected in the frame. Skipping safety equipment check.")
        return frame, [], detected_classes  # Return an empty list for missing classes, and detected classes

    # Determine missing classes
    missing_classes = set(zonescenarios) - set(detected_classes.keys())

    return frame, list(missing_classes), detected_classes


def save_detections(db, missing_classes, buffer, record_id, detected_classes):
    debounce_time_seconds = 1 * 60  # 1 minute debounce time converted to seconds
    current_timestamp = datetime.now(timezone.utc)  # Get the current timestamp once

    if missing_classes:
        cache_key = f"{record_id}_{','.join(missing_classes)}"  # Create a string key

        if should_skip_detection(cache_key, db, record_id, cache_key, current_timestamp, debounce_time_seconds):
            return

        save_detection(db, buffer, record_id, missing_classes, current_timestamp, cache_key, detected_classes)



def save_detection(db, buffer, record_id, missing_classes, current_timestamp, cache_key, detected_classes):
    detection_cache[cache_key] = current_timestamp

    missing_classes_str = ','.join(missing_classes)
    
    db_detection = Incident(
        recording_id=record_id,
        class_name=missing_classes_str,  # Save the missing class names as a comma-separated string
        confidence=0.0,  # Since it's missing, set confidence to 0
        bbox='',  # No bounding box since the item is missing
        frame=buffer.tobytes(),
        timestamp=current_timestamp
    )

    try:
        db.add(db_detection)
        db.commit()
        print(f"Missing detection saved to DB: {db_detection}")
    except Exception as e:
        print(f"Error saving to DB: {e}")
        db.rollback()

def should_skip_detection(cache_key, db, record_id, class_name, current_timestamp, debounce_time_seconds):
    last_timestamp = get_last_detection_timestamp(cache_key, db, record_id, class_name)

    if last_timestamp:
        # Ensure both timestamps are offset-aware
        if last_timestamp.tzinfo is None:
            last_timestamp = last_timestamp.replace(tzinfo=timezone.utc)
        
        if (current_timestamp - last_timestamp).total_seconds() < debounce_time_seconds:
            print(f"Skipping detection for {class_name} as it occurred within the last minute.")
            return True

    return False



def get_last_detection_timestamp(cache_key, db, record_id, class_name):
    # Check cache first
    last_timestamp = detection_cache.get(cache_key)

    if not last_timestamp:
        # If not in cache, check the database
        last_detection = db.query(Incident).filter_by(
            recording_id=record_id,
            class_name=class_name
        ).order_by(desc(Incident.timestamp)).first()

        if last_detection:
            last_timestamp = last_detection.timestamp
            detection_cache[cache_key] = last_timestamp  # Update cache with DB timestamp

    return last_timestamp


def handle_pallet_detections(model, frame, confidence):
    results = model(frame)
    detections = results[0].boxes
    bad_pallet_detected = False

    for det in detections:
        try:
            box = det.xyxy[0].tolist()  # Get the bounding box coordinates
            conf = det.conf[0].item()
            cls = int(det.cls[0].item())
            class_name = model.names[cls]

            if conf >= confidence and class_name == 'pallet_bad':
                bad_pallet_detected = True
                
                # Draw bounding box on the frame
                pt1 = (int(box[0]), int(box[1]))
                pt2 = (int(box[2]), int(box[3]))
                cv2.rectangle(frame, pt1, pt2, (0, 0, 255), 2)  # Red rectangle for bad pallet
                label = f'{class_name} {conf:.2f}'
                cv2.putText(frame, label, (int(box[0]), int(box[1]) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)  # Label in red

        except Exception as e:
            print(f"Error processing detection: {e}")
            continue

    return frame, bad_pallet_detected

def save_pallet_detection(db, buffer, record_id, class_name, confidence, current_timestamp):
    db_detection = Incident(
        recording_id=record_id,
        class_name=class_name,  # Save the detected class name
        confidence=confidence,  # Save the actual confidence level
        bbox='',  # Optionally save the bounding box coordinates if needed
        frame=buffer.tobytes(),
        timestamp=current_timestamp
    )

    try:
        db.add(db_detection)
        db.commit()
        print(f"{class_name} detection saved to DB with confidence {confidence:.2f}: {db_detection}")
    except Exception as e:
        print(f"Error saving to DB: {e}")
        db.rollback()

@celery_app.task(bind=True)
def run_ppe_detection(self, camera_id, model_path, record_id):
    db = SessionLocal() 

    try:
        model = YOLO(model_path)
        cap = initialize_camera(crud.get_camera_by_id(db, camera_id).ipaddress)
        confidence = (crud.get_recording(db=db, recording_id=record_id).confidence / 100) or crud.get_zone_confidence_level(db, camera_id)
        recordingscenarios = crud.get_zone_scenario(db=db, recording_id=record_id)
        
        while True:
            start_time = time.time()

            frame = process_frame(cap)
            frame, missing_classes, detected_classes = handle_detections(model, frame, confidence, recordingscenarios)

            # Save detections to DB
            buffer = cv2.imencode('.jpg', frame)[1]
            save_detections(db, missing_classes, buffer, record_id, detected_classes)

            elapsed_time = time.time() - start_time
            time.sleep(max(0, 0.1 - elapsed_time))

    except Exception as e:
        cap.release()
        raise self.retry(exc=e, countdown=10)  # Retry task if it fails

    finally:
        db.close()


@celery_app.task(bind=True)
def run_pallet_detection(self, camera_id, model_path, record_id):
    db = SessionLocal()  # Open a new session for the task

    try:
        model = YOLO(model_path)
        cap = initialize_camera2(crud.get_camera_by_id(db, camera_id).ipaddress, "./yolomodels/IMG_0454.MOV")
        confidence_threshold = (crud.get_recording(db=db, recording_id=record_id).confidence / 100) or crud.get_zone_confidence_level(db, camera_id)

        while True:
            start_time = time.time()

            frame = process_frame(cap) 
            results = model(frame)
            detections = results[0].boxes
            bad_pallet_detected = False
            detected_confidence = 0.0

            for det in detections:
                box = det.xyxy[0].tolist()  # Convert box coordinates to a list
                conf = det.conf[0].item()
                cls = int(det.cls[0].item())
                class_name = model.names[cls]

                if conf >= confidence_threshold and class_name == 'Pallets_bad':
                    bad_pallet_detected = True
                    detected_confidence = conf  # Store the confidence of the bad pallet detection

                    # Check debounce logic before saving the detection
                    current_timestamp = datetime.now(timezone.utc)
                    cache_key = f"{record_id}_{class_name}"

                    if should_skip_detection(cache_key, db, record_id, class_name, current_timestamp, debounce_time_seconds=60):
                        print(f"Skipping detection for {class_name} due to debounce.")
                        continue  # Skip saving this detection

                    # Draw bounding box on the frame
                    pt1 = (int(box[0]), int(box[1]))
                    pt2 = (int(box[2]), int(box[3]))  
                    cv2.rectangle(frame, pt1, pt2, (0, 0, 255), 2)  # Red rectangle for bad pallet
                    label = f'{class_name} {conf:.2f}'
                    cv2.putText(frame, label, (int(box[0]), int(box[1]) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)  # Label in red

                    # Save to DB if a bad pallet is detected
                    buffer = cv2.imencode('.jpg', frame)[1]
                    save_pallet_detection(db, buffer, record_id, class_name, detected_confidence, current_timestamp)

            elapsed_time = time.time() - start_time
            time.sleep(max(0, 0.1 - elapsed_time))

    except Exception as e:
        cap.release()
        raise self.retry(exc=e, countdown=10)  # Retry task if it fails

    finally:
        db.close()



@celery_app.task(bind=True)
def run_proximity_detection(self, camera_id, model_path, record_id):
    db = SessionLocal()

    try:
        model = YOLO(model_path)
        cap = initialize_camera2(crud.get_camera_by_id(db, camera_id).ipaddress, "./yolomodels/Forklift_move.mp4")
        confidence = (crud.get_recording(db=db, recording_id=record_id).confidence / 100) or crud.get_zone_confidence_level(db, camera_id)
        
        while True:
            start_time = time.time()

            frame = process_frame(cap)
            frame, proximity_detected, detected_classes = handle_proximity_detections(model, frame, confidence)

            if proximity_detected:
                buffer = cv2.imencode('.jpg', frame)[1]
                save_proximity_detection(db, buffer, record_id, detected_classes)

            elapsed_time = time.time() - start_time
            time.sleep(max(0, 0.1 - elapsed_time))

    except Exception as e:
        cap.release()
        raise self.retry(exc=e, countdown=10)  # Retry task if it fails

    finally:
        db.close()