from fastapi import APIRouter
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
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
    db_zones = crud.get_all_zone(db)
    if db_zones is None:
        raise HTTPException(status_code=404, detail="Zone not found")
    return db_zones

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

