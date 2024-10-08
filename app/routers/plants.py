
from fastapi import APIRouter
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from app.models import PlantStatus
from ..database import SessionLocal

from .. import crud, schemas


router = APIRouter(
    prefix="/plants",
    tags=["plants"],
)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=list[schemas.ReadPlant])
def get_plants(plant_status: schemas.PlantStatusEnum, db: Session = Depends(get_db)):
    
    return crud.get_all_plants(db, plant_status=plant_status)

@router.post("/", response_model=schemas.ReadPlant)
def create_plant(new_plant: schemas.CreatePlant, db: Session = Depends(get_db)):
    return crud.create_plant(db=db, new_plant=new_plant)

@router.get("/zones/{plant_id}", response_model=list[schemas.ReadZone])
def get_zone_by_plant_id(plant_id: int, db: Session = Depends(get_db)):
    db_zone = crud.get_zone_by_plant_id(db, plant_id=plant_id)
    if db_zone.count() == 0:
        raise HTTPException(status_code=404, detail="No Zone in a the given plant")
    return db_zone

@router.put("/{plant_id}", response_model=schemas.ReadPlant)
async def update_plant(plant_id: int, plant: schemas.UpdatePlant, db: Session = Depends(get_db)):
    db_plant = crud.update_plant(db=db, plant_id=plant_id, plant_to_update=plant)
    if not db_plant:
        raise HTTPException(status_code=404, detail="No Plant found with the given id")
    return db_plant

@router.delete("/{plant_id}", response_model=schemas.ReadPlant)
def inactivate_plant(plant_id: int, db: Session = Depends(get_db)):
    db_plant = crud.get_plant_by_id(db, plant_id)
    if not db_plant:
        raise HTTPException(status_code=404, detail="No Plant found with the given id")
    
    if db_plant.plantstatus == PlantStatus.inactive:
        raise HTTPException(status_code=400, detail="Plant is already inactive")

    updated_plant = crud.update_plant_status(db=db, plant_id=plant_id)
    
    return updated_plant