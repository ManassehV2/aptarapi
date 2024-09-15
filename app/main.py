from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import assignees, report, scenario
from .routers import zones, plants, cameras, detection
from . import models
from .database import engine, SessionLocal
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager


def prepopulate_plants(db: Session):
    if db.query(models.Plant).count() == 0:
        plants = [
            models.Plant(name="Aptar Annecy", description="France Manufacturing", address="19 Avenue des Vieux Moulins 74000 Annecy,France", plantConfidence=0.75),
            models.Plant(name="Aptar Berazategui", description="Argentina Manufacturing", address="Colectora Autovía 2 El Pato, Argentina", plantConfidence=0.75),
            models.Plant(name="Aptar Chieti", description="Italy Manufacturing", address="66020 San Giovanni Teatino, Chieti, Italy", plantConfidence=0.75),
            models.Plant(name="Aptar Congers", description="NY Manufacturing", address="250 North Route 303 10920 Congers, NY", plantConfidence=0.75),
            models.Plant(name="Aptar Dortmund", description="Germany Manufacturing", address="44319 Dortmund, NRW, Germany", plantConfidence=0.75),
            models.Plant(name="Aptar Jundiai", description="Brazil Manufacturing", address="151 Rua Gil Teixeira Lino SP Brazil", plantConfidence=0.75),
            models.Plant(name="Aptar Leeds", description="United Kingdom Manufacturing", address="LS27 0SS Morley, England, United Kingdom", plantConfidence=0.75),
            models.Plant(name="Aptar Madrid", description="Spain Manufacturing", address="28806 Alcalá de Henares, MD, Spain", plantConfidence=0.75),
            models.Plant(name="Aptar Pescara", description="Italy Manufacturing", address="65024, Manoppello Scalo,Pescara, Italy", plantConfidence=0.75),
            models.Plant(name="Aptar Weihai", description="China Manufacturing", address="Weihai, Shandong 264204, China", plantConfidence=0.75),

        ]
        db.add_all(plants)
        db.commit()
        print("Pre-populated plants table with initial data.")
    else:
        print("Plants table is already populated.")


def prepopulate_detection_types(db: Session):
    if db.query(models.DetectionType).count() == 0:
        detection_types = [
            models.DetectionType(name="PPE Detection", description="Detects PPE compliance", modelpath="./yolomodels/best_ppe.pt", task_name="run_ppe_detection"),
            models.DetectionType(name="Pallet Detection", description="Detects pallets in the area", modelpath="./yolomodels/best_pallet.pt", task_name="run_pallet_detection"),
            models.DetectionType(name="Proximity Detection", description="Detects proximity between forklift and person", modelpath="./yolomodels/forklift_best.pt", task_name="run_proximity_detection"),
        ]
        db.add_all(detection_types)
        db.commit()
        print("Pre-populated detection types table with initial data.")
    else:
        print("Detection types table is already populated.")

def init_db():
    db = SessionLocal()
    try:
        prepopulate_detection_types(db)
        prepopulate_plants(db)
    finally:
        db.close()


models.Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(
    title="Aptar Rest API",
    version="1.0.0",
    contact={
        "name": "Minase Mengistu, Mariama Serafim de Oliveira",
        "email": "minase.mengistu@abo.fi",
    },
    lifespan=lifespan,
)

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
