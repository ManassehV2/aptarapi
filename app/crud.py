from asyncio import Queue
import datetime
from fastapi import logger
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from app import schemas
from sqlalchemy.exc import NoResultFound

from . import models

def get_all_plants(db: Session, plant_status: schemas.PlantStatusEnum):
    return db.query(models.Plant).filter(models.Plant.plantstatus == plant_status.value)

def get_all_detection_types(db: Session):
    return db.query(models.DetectionType)

def get_all_scenarios(db: Session):
    return db.query(models.Scenario)

def get_instance_by_id(db: Session, instance_id: int):
    return db.query(models.Recording).get(instance_id)

def get_instance_by_zone_id(db: Session, zone_id: int):
    return db.query(models.Recording).filter(models.Recording.zone_id == zone_id)

def get_all_zone(db: Session):
    return db.query(models.Zone)

def get_zone_by_id(db: Session, zone_id: int):
    return db.query(models.Zone).filter(models.Zone.id == zone_id).first()

def get_cameras_in_zone_by_id(db: Session, zone_id: int):
    return db.query(models.Camera).filter(models.Camera.zone_id == zone_id)

def get_camera_by_id(db: Session, camera_id: int):
    return db.query(models.Camera).get(camera_id)

def get_zone_by_plant_id(db: Session, plant_id: int,  zone_status: schemas.PlantStatusEnum):
    return db.query(models.Zone).filter(models.Zone.plant_id == plant_id, models.Zone.zonestatus == zone_status.value)

def create_zone(db: Session, new_zone: schemas.CreateZone):
    zonecameras = []
    if len(new_zone.cameras) > 0:
        for cam in new_zone.cameras:
            zonecameras.append(models.Camera(name=cam.name, description=cam.description, ipaddress=cam.ipaddress))
    
    db_zone = models.Zone(title=new_zone.title, 
                          description=new_zone.description, 
                          plant_id=new_zone.plant_id,
                          zoneconfidence=new_zone.zoneconfidence, 
                          assignee_id=new_zone.assignee_id,
                          cameras=zonecameras 
                          )
    db.add(db_zone)
    db.commit()
    db.refresh(db_zone)

    return db_zone

def create_plant(db: Session, new_plant: schemas.CreatePlant):
    db_plant = models.Plant(name=new_plant.name, 
                            description=new_plant.description, 
                            address=new_plant.address,
                            plantConfidence=new_plant.plantConfidence)
    
    db.add(db_plant)
    db.commit()
    db.refresh(db_plant)
    return db_plant

def update_plant(db: Session, plant_id: int, plant_to_update: schemas.UpdatePlant):
    #get the plant
    db_plant = db.query(models.Plant).get(plant_id)
    if db_plant:
        db_plant.plantConfidence = plant_to_update.plantConfidence
        db_plant.plantstatus = schemas.PlantStatusEnum.active
        db.commit()
        db.refresh(db_plant)
        return db_plant
    else:
        return None
    

def update_zone(db: Session, zone_id: int, zone_to_update: schemas.UpdateZone):
    #get the zone
    db_zone = db.query(models.Zone).get(zone_id)
    if db_zone:
        db_zone.zoneconfidence = zone_to_update.plantConfidence
        db_zone.zonestatus = schemas.PlantStatusEnum.active
        db.commit()
        db.refresh(db_zone)
        return db_zone
    else:
        return None

def create_scenario(db: Session, new_scenario: schemas.CreateScenario):

    db_scenario = models.Scenario(name=new_scenario.name, 
                            description=new_scenario.description)
    
    db.add(db_scenario)
    db.commit()
    db.refresh(db_scenario)
    return db_scenario


def create_recording(db: Session, new_recording: schemas.CreateRecording):
    
    db_recording = models.Recording(starttime=datetime.datetime.now(),
                                    name=new_recording.name,
                                    zone_id=new_recording.zone_id,
                                    status=new_recording.status,
                                    assignee_id=new_recording.assignee_id,
                                    detection_type_id=new_recording.detection_type,
                                    camera_id=new_recording.camera_id,
                                    confidence=new_recording.confidence)
    db.add(db_recording)
    db.commit()
    db.refresh(db_recording)
    return db_recording

def create_recording_scenarios(db: Session, recording_id: int, scenario_id: int):
    db_recording_scenario = models.RecordingScenario(recording_id=recording_id, scenario_id=scenario_id)
    db.add(db_recording_scenario)
    db.commit()
    db.refresh(db_recording_scenario)
    return db_recording_scenario

def update_recording(db: Session, recording_id: int):
    db_recording = db.query(models.Recording).filter(models.Recording.id == recording_id).first()
    db_recording.endtime = datetime.datetime.now()
    db_recording.status = False
    db.commit()
    db.refresh(db_recording)

def update_recording_task_id(db, recording_id: int, task_id: str):

    db_recording = db.query(models.Recording).filter(models.Recording.id == recording_id).first()
    db_recording.task_id = task_id
    db.commit()
    db.refresh(db_recording)


def get_recording(db: Session, recording_id: int):
    return db.query(models.Recording).filter(models.Recording.id == recording_id).first()

def is_camera_available(db: Session, camera_id: int) -> bool:
    return db.query(
        db.query(models.Recording)
        .filter_by(camera_id=camera_id, status=True)
        .exists()
    ).scalar()

def is_camera_exists(db: Session, camera_id: int):
    try:
        # Query the Camera model to check if the camera_id exists
        return db.query(models.Camera).filter(models.Camera.id == camera_id).one_or_none() is not None
    except NoResultFound:
        return False




def get_zone_confidence_level(db: Session, camera_id: int):
    db_camera = db.query(models.Camera).filter(models.Camera.id == camera_id).first()
    return db_camera.zone.zoneconfidence or db_camera.zone.plant.plantConfidence or 0.75

def get_zone_scenario(db: Session, recording_id: int):

    scenario_names = (
    db.query(models.Scenario.name)
    .select_from(models.RecordingScenario)
    .join(models.Scenario, models.RecordingScenario.scenario_id == models.Scenario.id)
    .filter(models.RecordingScenario.recording_id == recording_id)
    .all()
)

    return [name.lower() for (name,) in scenario_names]

def get_all_record_scenarios(db: Session, recording_id: int):
    scenarios = (
        db.query(models.Scenario)
        .join(models.RecordingScenario, models.Scenario.id == models.RecordingScenario.scenario_id)
        .filter(models.RecordingScenario.recording_id == recording_id)
        .all()
    )
    
    return scenarios 

def get_all_assignees(db: Session):
    return db.query(models.Assignee)


def get_detection_model_by_id(db: Session, detection_type_id: int):
    return db.query(models.DetectionType).get(detection_type_id)

