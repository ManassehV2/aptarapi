
from fastapi import APIRouter
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
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
def get_plants(db: Session = Depends(get_db)):
    db_plants = crud.get_all_plants(db)
    if db_plants is None:
        raise HTTPException(status_code=404, detail="Plants not found")
    return db_plants

@router.post("/", response_model=schemas.ReadPlant)
def create_plant(new_plant: schemas.CreatePlant, db: Session = Depends(get_db)):
    print(new_plant) 
    return crud.create_plant(db=db, new_plant=new_plant)

@router.get("/zones/{plant_id}", response_model=list[schemas.ReadZone])
def get_zone_by_plant_id(plant_id: int, db: Session = Depends(get_db)):
    db_zone = crud.get_zone_by_plant_id(db, plant_id=plant_id)
    if db_zone is None:
        raise HTTPException(status_code=404, detail="No Zone in a the given plant")
    return db_zone