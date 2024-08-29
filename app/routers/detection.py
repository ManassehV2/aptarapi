
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.tasks import run_ppe_detection, run_pallet_detection, run_proximity_detection
from ..database import SessionLocal
from .. import crud, schemas
from celery.result import AsyncResult
from ..celery import celery_app


router = APIRouter(
    prefix="/detection",
    tags=["detection"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/start/")
async def start_detection(new_instance: schemas.CreateInstance, db: Session = Depends(get_db)):
    if crud.is_camera_available(db, new_instance.recording.camera_id):
        return {"message": "Camera is in use"}
    
    # Create a new recording entry in the database
    recording = crud.create_recording(db, schemas.CreateRecording(
        name=new_instance.recording.name,
        zone_id=new_instance.recording.zone_id,
        assignee_id=new_instance.recording.assignee_id,
        detection_type=new_instance.recording.detection_type,
        camera_id=new_instance.recording.camera_id,
        status=new_instance.recording.status,
        confidence=new_instance.recording.confidence
    ))

    #create recording scenarios if its PPE
    if new_instance.scenarios:
        for scenario in new_instance.scenarios:
            crud.create_recording_scenarios(db, scenario_id=scenario.id, recording_id=recording.id)
    
    #get selected model path
    selected_model = crud.get_detection_model_by_id(db, recording.detection_type_id)

    # Start the Celery task
    if selected_model.id == 1:
        task = run_ppe_detection.delay(new_instance.recording.camera_id, selected_model.modelpath, recording.id)
    elif selected_model.id == 2:
        task = run_pallet_detection.delay(new_instance.recording.camera_id, selected_model.modelpath, recording.id)
    else:
        task = run_proximity_detection.delay(new_instance.recording.camera_id, selected_model.modelpath, recording.id)

    # Save the Celery task ID to the recording for later reference
    crud.update_recording_task_id(db, recording.id, task.id)

    return {"task_id": task.id, "recording_id": recording.id}


@router.post("/stop/{recording_id}")
async def stop_detection(recording_id: int, db: Session = Depends(get_db)):
    # Find the corresponding recording
    recording = crud.get_recording(db, recording_id)
    if not recording:
        raise HTTPException(status_code=404, detail="Recording not found")
    
    # Get the task result using the task ID
    task_result = AsyncResult(recording.task_id, app=celery_app)

    if task_result is None or task_result.state in ['SUCCESS', 'FAILURE', 'REVOKED']:
        # If the task is already completed or does not exist
        raise HTTPException(status_code=404, detail="Task not found or already completed")
    
    # Revoke the task, terminate=True will kill the task if it's still running
    task_result.revoke(terminate=True)

    # Update the recording end time
    crud.update_recording(db=db, recording_id=recording_id)
    return {"status": "Detection stopped", "recording_id": recording_id}


@router.get("/types/", response_model=list[schemas.ReadDetectionType])
async def get_detection_types(db: Session = Depends(get_db)):
    db_detections = crud.get_all_detection_types(db=db)
    if not db_detections:
        raise HTTPException(status_code=404, detail="Detection Type not found")
    return db_detections



