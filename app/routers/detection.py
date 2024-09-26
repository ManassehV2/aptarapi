import logging
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from ..database import SessionLocal
from .. import crud, schemas
from celery.result import AsyncResult
from app.celery_config import celery_app
from celery.result import AsyncResult
import cv2


router = APIRouter(
    prefix="/detection",
    tags=["detection"],
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def is_camera_accessible(camera_url: str) -> bool:
    try:
        cap = cv2.VideoCapture(camera_url)
        
        if not cap.isOpened():
            logger.warning(f"Camera {camera_url} could not be opened.")
            return False
        
        ret, frame = cap.read()
        if ret:
            return True
        else:
            logger.warning(f"Camera {camera_url} could not retrieve a frame.")
            return False
    
    except Exception as e:
        logger.error(f"Failed to connect to camera {camera_url}: {e}")
        return False

    finally:
        if 'cap' in locals():
            cap.release()

@router.post("/start/")
async def start_detection(new_instance: schemas.CreateInstance, db: Session = Depends(get_db)):
    if crud.is_camera_available(db, new_instance.recording.camera_id):
            raise HTTPException(status_code=404, detail="Camera is in use")
        
    # Check if the IP camera is accessible using OpenCV
    selected_camera = crud.get_camera_by_id(db=db, camera_id=new_instance.recording.camera_id)
    if not is_camera_accessible(selected_camera.ipaddress):
        raise HTTPException(status_code=400, detail="Cannot connect to the camera. Please check the connection or IP.")
    
    try:
        recording = crud.create_recording(db, schemas.CreateRecording(
            name=new_instance.recording.name,
            zone_id=new_instance.recording.zone_id,
            assignee_id=new_instance.recording.assignee_id,
            detection_type=new_instance.recording.detection_type,
            camera_id=new_instance.recording.camera_id,
            status=new_instance.recording.status,
            confidence=new_instance.recording.confidence
        ))

        if new_instance.scenarios:
            for scenario in new_instance.scenarios:
                crud.create_recording_scenarios(db, scenario_id=scenario.id, recording_id=recording.id)
        
        selected_model = crud.get_detection_model_by_id(db, recording.detection_type_id)
        if not selected_model or not selected_model.task_name:
            raise HTTPException(status_code=400, detail="Invalid detection type or task not defined")
            

        try:
            task = celery_app.send_task(selected_model.task_name, args=[new_instance.recording.camera_id, selected_model.modelpath, recording.id],queue="main-queue")
            crud.update_recording_task_id(db, recording.id, task.id)
            return {"task_id": task.id, "recording_id": recording.id}
        except Exception as e:
             return {"message": str(e)}, 500        
    except Exception as e:
        return {"message": str(e)}, 500

@router.get("/task-status/{task_id}")
async def get_task_status(task_id: str):
    try:
        task_result = AsyncResult(task_id, app=celery_app)
        if task_result.state == "PENDING":
            return {"status": "Pending", "task_id": task_id}
        elif task_result.state == "SUCCESS":
            return {"status": "Completed", "result": task_result.result}
        elif task_result.state == "FAILURE":
            return {"status": "Failed", "error": str(task_result.info)}
        else:
            return {"status": task_result.state, "task_id": task_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching task status: {str(e)}")



@router.post("/stop/{recording_id}")
async def stop_detection(recording_id: int, db: Session = Depends(get_db)):
    recording = crud.get_recording(db, recording_id)
    if not recording:
        raise HTTPException(status_code=404, detail="Recording not found")
    
    task_result = AsyncResult(recording.task_id, app=celery_app)

    if task_result is None:
        raise HTTPException(status_code=404, detail="Task not found or already completed")
    
    task_result.revoke(terminate=True)

    crud.update_recording(db=db, recording_id=recording_id)
    return {"status": "Detection stopped", "recording_id": recording_id}


@router.get("/types/", response_model=list[schemas.ReadDetectionType])
async def get_detection_types(db: Session = Depends(get_db)):
    db_detections = crud.get_all_detection_types(db=db)
    if not db_detections:
        raise HTTPException(status_code=404, detail="Detection Type not found")
    return db_detections



