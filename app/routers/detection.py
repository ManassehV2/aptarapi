from asyncio import Queue
import asyncio
import base64
import datetime
import logging
import time
import cv2
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi import Depends
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from ultralytics import YOLO

from app.models import Incident

from ..database import SessionLocal

from .. import crud, schemas


router = APIRouter()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def initialize_webcam():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise RuntimeError("Could not open webcam")
    return cap

def process_frame(cap):
    ret, frame = cap.read()
    if not ret:
        raise OSError("Failed to capture frame from webcam")
    frame = cv2.resize(frame, (640, 480))
    return frame

def handle_detections(model, frame):
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
            if conf >= 0.85:
                detection_list.append({
                    "class_name": model.names[cls],
                    "confidence": conf,
                    "bbox": [int(x) for x in box]
                })
        except Exception as e:
            logger.error(f"Error processing detection: {e}")
            continue
    return frame, detection_list

def encode_frame(frame):
    _, buffer = cv2.imencode('.jpg', frame)
    jpg_as_text = base64.b64encode(buffer).decode('utf-8')
    return jpg_as_text, buffer

async def save_detections(db, detection_list, buffer, record_id):
    for detection in detection_list:
        db_detection = Incident(
            recording_id=record_id,
            class_name=detection["class_name"],
            confidence=detection["confidence"],
            bbox=str(detection["bbox"]),
            frame=buffer.tobytes()
        )
        try:
            db.add(db_detection)
            db.commit()
            logger.info(f"Detection saved to DB: {db_detection}")
        except Exception as e:
            logger.error(f"Error saving to DB: {e}")
            db.rollback()

async def save_detections_to_db(queue: Queue, db: AsyncSession):
    while True:
        db_detection = await queue.get()
        try:
            db.add(db_detection)
            await db.commit()
            await db.refresh(db_detection)
        except Exception as e:
            logger.error(f"Database error: {e}")
        finally:
            queue.task_done()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.websocket("/ppe/detect")
async def websocket_endpoint(websocket: WebSocket, db: Session = Depends(get_db)):
    model = YOLO('./yolomodels/best_3.pt')
    await websocket.accept()

    try:
        form_data = await websocket.receive_json()
        logger.info(f"Received form data: {form_data}")

        #create the corresponding record for the incidents
        result = crud.create_recording(db, schemas.CreateRecording(
            starttime=datetime.datetime.now(),
            endtime=datetime.datetime.now(),
            camera_id=int(form_data.get("camera")) 
            ))
            
        try:
            cap = await initialize_webcam()
        except Exception as e:
            await websocket.send_json({"error": str(e)})
            await websocket.close()
            return
        
        while True:
            start_time = time.time()
            
            try:
                frame = process_frame(cap)
            except Exception as e:
                logger.error(str(e))
                break
            
            frame, detection_list = handle_detections(model, frame)
            jpg_as_text, buffer = encode_frame(frame)
            
            await save_detections(db, detection_list, buffer, record_id=result.id)
            await websocket.send_json({"frame": jpg_as_text, "detections": detection_list})
            
            elapsed_time = time.time() - start_time
            await asyncio.sleep(max(0, 0.1 - elapsed_time))
    
    except WebSocketDisconnect:
        logger.info("Client disconnected")
        crud.update_recording(db=db, recording_id=result.id)
    except Exception as e:
        logger.error(f"Exception occurred: {e}")
        await websocket.send_json({"error": str(e)})
    finally:
        cap.release()
        await websocket.close()