
import datetime
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.tasks import run_detection, redis_client
from ..database import SessionLocal
from .. import crud, schemas


router = APIRouter(
    prefix="/ppe",
    tags=["detection"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/detect/start/")
async def start_detection(camera_id: int, db: Session = Depends(get_db)):
    if crud.is_camera_available(db, camera_id):
        return {"message": "Camera is in use"}
    
    # Create a new recording entry in the database
    recording = crud.create_recording(db, schemas.CreateRecording(
        starttime=datetime.datetime.now(),
        camera_id=camera_id
    ))

    # Start the Celery task
    task = run_detection.delay(camera_id, './yolomodels/best_3.pt', recording.id)
    # Save the Celery task ID to the recording for later reference
    crud.update_recording_task_id(db, recording.id, task.id)

    return {"task_id": task.id, "recording_id": recording.id}

@router.post("/detect/stop/{recording_id}")
async def stop_detection(recording_id: int, db: Session = Depends(get_db)):
    # Find the corresponding recording
    recording = crud.get_recording(db, recording_id)
    if not recording:
        raise HTTPException(status_code=404, detail="Recording not found")

    # Signal the Celery task to stop
    redis_client.set(f"stop_{recording_id}", "1")

    # Update the recording end time
    crud.update_recording(db=db, recording_id=recording_id)

    return {"status": "Detection stopped", "recording_id": recording_id}

