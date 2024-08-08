
from fastapi import APIRouter
from ..database import SessionLocal



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
