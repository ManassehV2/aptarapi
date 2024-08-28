
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.tasks import run_detection, redis_client
from ..database import SessionLocal
from .. import crud, schemas


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
    task = run_detection.delay(new_instance.recording.camera_id, selected_model.modelpath, recording.id)
    # Save the Celery task ID to the recording for later reference
    crud.update_recording_task_id(db, recording.id, task.id)

    return {"task_id": task.id, "recording_id": recording.id}


@router.post("/stop/{recording_id}")
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


@router.get("/types/", response_model=list[schemas.ReadDetectionType])
async def get_detection_types(db: Session = Depends(get_db)):
    db_detections = crud.get_all_detection_types(db=db)
    if not db_detections:
        raise HTTPException(status_code=404, detail="Detection Type not found")
    return db_detections



