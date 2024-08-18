from asyncio import Queue
import datetime
from fastapi import logger
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from app import schemas

from . import models

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


def get_all_plants(db: Session):
    return db.query(models.Plant)
def get_all_scenarios(db: Session):
    return db.query(models.Scenario)

def get_all_zone(db: Session):
    return db.query(models.Zone)

def get_zone_by_id(db: Session, zone_id: int):
    return db.query(models.Zone).filter(models.Zone.id == zone_id).first()

def get_cameras_in_zone_by_id(db: Session, zone_id: int):
    return db.query(models.Camera).filter(models.Camera.zone_id == zone_id)

def get_camera_by_id(db: Session, camera_id: int):
    return db.query(models.Camera).get(camera_id)

def get_zone_by_plant_id(db: Session, plant_id: int):
    return db.query(models.Zone).filter(models.Zone.plant_id == plant_id)

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

def create_scenario(db: Session, new_scenario: schemas.CreateScenario):

    db_scenario = models.Scenario(name=new_scenario.name, 
                            description=new_scenario.description)
    
    db.add(db_scenario)
    db.commit()
    db.refresh(db_scenario)
    return db_scenario


def create_recording(db: Session, new_recording: schemas.CreateRecording):
    db_recording = models.Recording(starttime=new_recording.starttime, endtime=new_recording.endtime, camera_id=new_recording.camera_id)
    db.add(db_recording)
    db.commit()
    db.refresh(db_recording)
    return db_recording

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

def get_zone_confidence_level(db: Session, camera_id: int):
    db_camera = db.query(models.Camera).filter(models.Camera.id == camera_id).first()
    return db_camera.zone.zoneconfidence or db_camera.zone.plant.plantConfidence

def get_zone_scenario(db: Session, camera_id: int):

    #First get the zone of the camera
    db_camera = get_camera_by_id(db=db, camera_id=camera_id)

    scenario_names = (
    db.query(models.Scenario.name)
    .select_from(models.ZoneScenario)
    .join(models.Scenario, models.ZoneScenario.scenarioid == models.Scenario.id)
    .filter(models.ZoneScenario.zoneid == db_camera.zone_id)
    .all()
)

    return [name.lower() for (name,) in scenario_names]




