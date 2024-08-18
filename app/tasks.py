from collections import defaultdict
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
from datetime import datetime
from app.celery import celery_app


# Redis setup for signaling the stop command
redis_client = redis.Redis(host='localhost', port=6379, db=0)

# Initialize a cache to store the last detection timestamp for each class and recording
detection_cache = defaultdict(lambda: None)

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

def process_frame(cap):
    ret, frame = cap.read()
    if not ret:
        raise OSError("Failed to capture frame from webcam")
    frame = cv2.resize(frame, (640, 480))
    return frame

def handle_detections(model, frame, zoneconf, zonescenarios):
    results = model(frame)
    detections = results[0].boxes
    detection_list = []
    for det in detections:
        try:
            box = det.xyxy[0].tolist()
            conf = det.conf[0].item()
            cls = int(det.cls[0].item())
            label = f'{model.names[cls]} {conf:.2f}'
            pt1 = (int(box[0]), int(box[1]))
            pt2 = (int(box[2]), int(box[3]))
            cv2.rectangle(frame, pt1, pt2, (255, 0, 0), 2)
            cv2.putText(frame, label, (int(box[0]), int(box[1]) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
            if conf >= zoneconf and (model.names[cls] in zonescenarios):
                detection_list.append({
                    "class_name": model.names[cls],
                    "confidence": conf,
                    "bbox": [int(x) for x in box]
                })
        except Exception as e:
            print(f"Error processing detection: {e}")
            continue
    return frame, detection_list

def save_detections(db, detection_list, buffer, record_id):
    debounce_time_minutes = 10  # Set the debounce time to 10 minutes
    debounce_time_seconds = debounce_time_minutes * 60  # Convert minutes to seconds

    for detection in detection_list:
        current_timestamp = datetime.utcnow()  # Always assign the current timestamp
        cache_key = (record_id, detection["class_name"])

        # Check the cache first
        last_timestamp = detection_cache.get(cache_key)

        if last_timestamp:
            time_diff = (current_timestamp - last_timestamp).total_seconds()
            
            # Skip saving if the last detection was within the debounce time (10 minutes)
            if time_diff < debounce_time_seconds:
                print(f"Skipping detection for {detection['class_name']} as it occurred within the last 10 minutes (cached).")
                continue
        else:
            # If not found in cache, check the database
            last_detection = db.query(Incident).filter_by(
                recording_id=record_id,
                class_name=detection["class_name"]
            ).order_by(desc(Incident.timestamp)).first()

            if last_detection:
                last_timestamp = last_detection.timestamp
                time_diff = (current_timestamp - last_timestamp).total_seconds()

                # Update the cache with the latest timestamp
                detection_cache[cache_key] = last_timestamp

                if time_diff < debounce_time_seconds:
                    print(f"Skipping detection for {detection['class_name']} as it occurred within the last 10 minutes (DB).")
                    continue

        # Update the cache with the current timestamp for this class and recording_id
        detection_cache[cache_key] = current_timestamp

        # If no recent detection or beyond the debounce time, save the new detection
        db_detection = Incident(
            recording_id=record_id,
            class_name=detection["class_name"],
            confidence=detection["confidence"],
            bbox=str(detection["bbox"]),
            frame=buffer.tobytes(),
            timestamp=current_timestamp  # Use the current timestamp
        )
        try:
            db.add(db_detection)
            db.commit()
            print(f"Detection saved to DB: {db_detection}")
        except Exception as e:
            print(f"Error saving to DB: {e}")
            db.rollback()


@celery_app.task(bind=True)
def run_detection(self, camera_id, model_path, record_id):
    db = SessionLocal() 

    try:
        model = YOLO(model_path)
        cap = initialize_camera(crud.get_camera_by_id(db, camera_id).ipaddress)
        zoneconf = crud.get_zone_confidence_level(db, camera_id)
        zonescenarios = crud.get_zone_scenario(db=db, camera_id=camera_id)
        
        while True:
            start_time = time.time()

            frame = process_frame(cap)
            frame, detection_list = handle_detections(model, frame, zoneconf, zonescenarios)

            # Save detections to DB
            buffer = cv2.imencode('.jpg', frame)[1]
            save_detections(db, detection_list, buffer, record_id)

            # Check for a stop signal
            if redis_client.get(f"stop_{record_id}"):
                cap.release()
                break

            elapsed_time = time.time() - start_time
            time.sleep(max(0, 0.1 - elapsed_time))

    except Exception as e:
        cap.release()
        raise self.retry(exc=e, countdown=10)  # Retry task if it fails

    finally:
        db.close()
        