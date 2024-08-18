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
from datetime import datetime, timezone
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
    debounce_time_seconds = 1 * 60  # 1 minute debounce time converted to seconds
    current_timestamp = datetime.now(timezone.utc)  # Get the current timestamp once

    for detection in detection_list:
        cache_key = (record_id, detection["class_name"])

        if should_skip_detection(cache_key, db, record_id, detection["class_name"], current_timestamp, debounce_time_seconds):
            continue

        save_detection(db, buffer, record_id, detection, current_timestamp, cache_key)


def should_skip_detection(cache_key, db, record_id, class_name, current_timestamp, debounce_time_seconds):
    last_timestamp = get_last_detection_timestamp(cache_key, db, record_id, class_name)

    if last_timestamp and (current_timestamp - last_timestamp).total_seconds() < debounce_time_seconds:
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


def save_detection(db, buffer, record_id, detection, current_timestamp, cache_key):
    detection_cache[cache_key] = current_timestamp

    db_detection = Incident(
        recording_id=record_id,
        class_name=detection["class_name"],
        confidence=detection["confidence"],
        bbox=str(detection["bbox"]),
        frame=buffer.tobytes(),
        timestamp=current_timestamp
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
        