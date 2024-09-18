
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

    camera = crud.get_camera_by_id(db=db, camera_id=camera_id)
    if not camera:
        await websocket.send_text(f"Camera with ID {camera_id} not found.")
        await websocket.close()
        return

    cap = cv2.VideoCapture(camera.ipaddress)

    if not cap.isOpened():
        await websocket.send_text(f"Could not connect to the IP camera at {camera.ipaddress}.")
        await websocket.close()
        return

    try:
        while True:
            ret, frame = await asyncio.to_thread(cap.read)

            if not ret:
                await websocket.send_text("Failed to read frame from camera.")
                break

            _, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()

            try:
                await websocket.send_bytes(frame_bytes)
            except RuntimeError as e:
                print("WebSocket closed while sending data:", e)
                break

            await asyncio.sleep(0.1)

    except WebSocketDisconnect:
        print("WebSocket disconnected.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        cap.release()
        await websocket.close()