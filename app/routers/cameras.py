
import asyncio
import cv2
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import SessionLocal

from .. import crud, schemas


router = APIRouter(
    prefix="",
    tags=["cameras"],
)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/cameras/{camera_id}", response_model=schemas.ReadCamera)
def get_camera_by_id(camera_id: int, db: Session = Depends(get_db)):

    db_camera = crud.get_camera_by_id(db, camera_id=camera_id)
    if db_camera is None:
        raise HTTPException(status_code=404, detail="No Camera Found")
    return db_camera


@router.websocket("/ws/camera/{camera_id}")
async def websocket_endpoint(websocket: WebSocket, camera_id: int, db: Session = Depends(get_db)):
    await websocket.accept()

    # Fetch the camera from the database
    camera = crud.get_camera_by_id(db=db, camera_id=camera_id)
    if not camera:
        await websocket.send_text(f"Camera with ID {camera_id} not found.")
        await websocket.close()
        return

    # Try to connect to the IP camera using its IP address
    cap = cv2.VideoCapture(camera.ipaddress)

    # If connection to IP camera fails, default to the first webcam (index 0)
    if not cap.isOpened():
        await websocket.send_text("Could not connect to the IP camera. Switching to default webcam.")
        cap = cv2.VideoCapture(0)  # Default to the first webcam

        if not cap.isOpened():
            await websocket.send_text("Could not connect to the default webcam either.")
            await websocket.close()
            return

    try:
        while True:
            ret, frame = cap.read()

            if not ret:
                await websocket.send_text("Failed to read frame from camera.")
                break

            # Encode the frame to send it via WebSocket
            _, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()

            try:
                await websocket.send_bytes(frame_bytes)
            except RuntimeError as e:
                # Handle the case where the WebSocket is closed during sending
                print("WebSocket closed while sending data:", e)
                break

            # Add a small delay to control the frame rate
            await asyncio.sleep(0.1)

    except WebSocketDisconnect:
        print("WebSocket disconnected.")
    finally:
        cap.release()
        # Ensure WebSocket is closed
        await websocket.close()

