from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import assignees, report, scenario
from .routers import zones, plants, cameras, detection
from . import models
from .database import engine, SessionLocal
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager

# Define the function to prepopulate the DetectionType table
def prepopulate_detection_types(db: Session):
    if db.query(models.DetectionType).count() == 0:
        detection_types = [
            models.DetectionType(name="PPE Detection", description="Detects PPE compliance", modelpath="./yolomodels/PPE_best_v1.pt", task_name="run_ppe_detection"),
            models.DetectionType(name="Pallet Detection", description="Detects pallets in the area", modelpath="./yolomodels/best_pallet.pt", task_name="run_pallet_detection"),
            models.DetectionType(name="Proximity Detection", description="Detects proximity between forklift and person", modelpath="./yolomodels/best_forklift.pt", task_name="run_proximity_detection"),
        ]
        db.add_all(detection_types)
        db.commit()
        print("Pre-populated detection types table with initial data.")
    else:
        print("Detection types table is already populated.")

# Initialize the database and prepopulate tables
def init_db():
    db = SessionLocal()
    try:
        prepopulate_detection_types(db)
    finally:
        db.close()

# Create tables if they don't exist
models.Base.metadata.create_all(bind=engine)

# Define the lifespan context manager for startup and shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup event: initialize the database
    init_db()
    yield
    # Shutdown event: nothing specific, but you could add cleanup code here

# Initialize the FastAPI application with lifespan context manager
app = FastAPI(
    title="Aptar Rest API",
    version="1.0.0",
    contact={
        "name": "Minase Mengistu, Mariama Serafim de Oliveira",
        "email": "minase.mengistu@abo.fi",
    },
    lifespan=lifespan,
)

# CORS configuration
origins = [
    "http://localhost:8000",
    "http://127.0.0.1:8000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the routers
app.include_router(zones.router)
app.include_router(plants.router)
app.include_router(cameras.router)
app.include_router(detection.router)
app.include_router(scenario.router)
app.include_router(assignees.router)
app.include_router(report.router)
