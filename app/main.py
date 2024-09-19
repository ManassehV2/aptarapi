from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import assignees, report, scenario
from .routers import zones, plants, cameras, detection
from . import models
from .database import engine, SessionLocal
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager
from app.db_init import init_db 


@asynccontextmanager
async def lifespan(app: FastAPI):
    db = SessionLocal()
    try:
        init_db(db)
    finally:
        db.close()
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

# Ensure tables are created
#models.Base.metadata.create_all(bind=engine)
