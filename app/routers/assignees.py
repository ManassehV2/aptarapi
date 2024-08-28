
from fastapi import APIRouter
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import SessionLocal

from .. import crud, schemas


router = APIRouter(
    prefix="/assignees",
    tags=["assignees"],
)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/", response_model=list[schemas.ReadAssignee])
def get_all_assignees(db: Session = Depends(get_db)):
     db_assignees = crud.get_all_assignees(db=db)
     if db_assignees.count() == 0:
        raise HTTPException(status_code=404, detail="No Assignees found")
     return db_assignees