from fastapi import APIRouter
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from app.models import PlantStatus
from ..database import SessionLocal
from .. import crud, schemas

router = APIRouter(
    prefix="/zones",
    tags=["zones"],
)


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=list[schemas.ReadZone])
def get_zones(db: Session = Depends(get_db)):
    return crud.get_all_zone(db)

@router.get("/{zone_id}", response_model=schemas.ReadZone)
def get_zone_by_id(zone_id: int, db: Session = Depends(get_db)):
    db_zone = crud.get_zone_by_id(db, zone_id=zone_id)
    if db_zone is None:
        raise HTTPException(status_code=404, detail="Zone not found")
    return db_zone

@router.get("/cameras/{zone_id}", response_model=list[schemas.Camera])
def get_cameras_in_zone_by_id(zone_id: int, db: Session = Depends(get_db)):
    db_cameras = crud.get_cameras_in_zone_by_id(db, zone_id=zone_id)
    if db_cameras is None:
        raise HTTPException(status_code=404, detail="No cameras in the Zone")
    return db_cameras


@router.post("/", response_model=schemas.ReadZone)
def create_zone(new_zone: schemas.CreateZone, db: Session = Depends(get_db)):
    return crud.create_zone(db=db, new_zone=new_zone)

@router.put("/{zone_id}", response_model=schemas.ReadZone)
async def update_zone(zone_id: int, zone: schemas.UpdateZone, db: Session = Depends(get_db)):
    db_zone = crud.update_zone(db=db, zone_id=zone_id, zone_to_update=zone)
    if not db_zone:
        raise HTTPException(status_code=404, detail="No Zone found with the given id")
    return db_zone


@router.get("/instance/{instance_id}", response_model=schemas.ReadInstance)
def get_instance_detail(instance_id: int, db: Session = Depends(get_db)):
    db_instance = crud.get_instance_by_id(db=db, instance_id=instance_id)
    instance_scenarios = crud.get_all_record_scenarios(db=db, recording_id=db_instance.id)
    instance_incidents = crud.get_record_instances(db=db, instance_id=instance_id)

    details = schemas.ReadInstance(recording=db_instance, scenarios=instance_scenarios, instances=instance_incidents)
    if not details:
        raise HTTPException(status_code=404, detail="instance not found")
    return details

@router.get("/instances/{zone_id}", response_model=list[schemas.ReadInstance])
def get_all_zone_instances(zone_id: int, db: Session = Depends(get_db)):
    instanceslist = []
    zone_instances = crud.get_instance_by_zone_id(db=db, zone_id=zone_id)

    for instance in zone_instances:
        instance_scenarios = crud.get_all_record_scenarios(db=db, recording_id=instance.id)
        instanceslist.append(schemas.ReadInstance(recording=instance, scenarios=instance_scenarios))
    
    return instanceslist

@router.delete("/{zone_id}", response_model=schemas.ReadZone)
def inactivate_zone(zone_id: int, db: Session = Depends(get_db)):
    db_zone = crud.get_zone_by_id(db, zone_id=zone_id)
    if not db_zone:
        raise HTTPException(status_code=404, detail="No Zone found with the given id")
    
    if db_zone.zonestatus == PlantStatus.inactive:
        raise HTTPException(status_code=400, detail="Zone is already inactive")

    updated_zone = crud.update_zone_status(db=db, zone_id=zone_id)
    
    return updated_zone