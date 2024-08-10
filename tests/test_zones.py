from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base
from app.main import app
from app.routers import plants, zones

SQLALCHEMY_DATABASE_URL = "sqlite://"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[zones.get_db] = override_get_db
app.dependency_overrides[plants.get_db] = override_get_db


client = TestClient(app)

def test_get_zones():
    response = client.get(
        "/zones/")
    assert response.status_code == 200, response.text
    data = response.json()
    assert len(data) == 0


def test_create_zone():
    response = client.post(
        "/zones/",
        json={"title": "new zone for test", "description": "new zone for test description", "assignee_id": 1, "plant_id": 1},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["title"] == "new zone for test"
    assert data["description"] == "new zone for test description"


def test_get_plants():
    response = client.get(
        "/plants/")
    assert response.status_code == 200, response.text
    data = response.json()
    assert len(data) == 0

def test_create_plant():
    response = client.post(
        "/plants/",
        json={"name": "new plant for test", "description": "new zone for test description", "address": "New plant address"},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["name"] == "new plant for test"
    assert data["description"] == "new zone for test description"
    assert data["address"] == "New plant address"