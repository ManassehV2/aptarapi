
from fastapi import APIRouter
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import SessionLocal

from .. import crud, schemas


router = APIRouter(
    prefix="/cameras",
    tags=["cameras"],
)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/{camera_id}", response_model=schemas.ReadCamera)
def get_camera_by_id(camera_id: int, db: Session = Depends(get_db)):

    db_camera = crud.get_camera_by_id(db, camera_id=camera_id)
    if db_camera is None:
        raise HTTPException(status_code=404, detail="No Camera Found")
    return db_camera