from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import assignees, scenario
from .routers import zones, plants, cameras, detection

from . import models
from .database import  engine

#models.Base.metadata.create_all(bind=engine)


app = FastAPI(
    title = "Aptar Rest API",
    version="1.0.0",
    contact={
        "name": "Minase Mengistu, Mariama Serafim de Oliveira",
        "email": "minase.mengistu@abo.fi",
    },
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


app.include_router(zones.router)
app.include_router(plants.router)
app.include_router(cameras.router)
app.include_router(detection.router)
app.include_router(scenario.router)
app.include_router(assignees.router)
