
from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session
from app import crud
from ..database import SessionLocal


router = APIRouter(
    prefix="/reports",
    tags=["reports"],
)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/incident_data")
def get_incident_data(
    plant_id: int,
    zone_id: int = None,
    days: int = 7,
    detection_type_id: int = 1,
    db: Session = Depends(get_db)
):
   return crud.get_report_data(db=db, plant_id=plant_id,zone_id=zone_id,days=days,detection_type_id=detection_type_id)
