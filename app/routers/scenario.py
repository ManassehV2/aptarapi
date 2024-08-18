
from fastapi import APIRouter
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import SessionLocal

from .. import crud, schemas


router = APIRouter(
    prefix="/scenario",
    tags=["scenarios"],
)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=list[schemas.ReadScenario])
def get_scenarios(db: Session = Depends(get_db)):
    db_scenarios = crud.get_all_scenarios(db)
    if db_scenarios.count() == 0:
        raise HTTPException(status_code=404, detail="No Scenarios not found")
    return db_scenarios

@router.post("/", response_model=schemas.CreateScenario)
def create_scenario(new_scenario: schemas.CreateScenario, db: Session = Depends(get_db)): 
    return crud.create_scenario(db=db, new_scenario=new_scenario)
