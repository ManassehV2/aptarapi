from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base
from app.main import app
from app.models import Zone, Camera, Plant
from app.routers import plants, zones, cameras

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
app.dependency_overrides[cameras.get_db] = override_get_db


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
        json={"title": "new zone for test", "description": "new zone for test description", "assignee_id": 1, "plant_id": 1, "assignee_id": 1},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["title"] == "new zone for test"
    assert data["description"] == "new zone for test description"

def test_get_zone_by_id():
    session = TestingSessionLocal()
    testzone = Zone(title="test zone", description="test zon des",plant_id=1, assignee_id=1)
    session.add(testzone)
    session.commit()
    session.refresh(testzone)

    response = client.get(f"/zones/{testzone.id}")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["title"] == "test zone"
    assert data["description"] == "test zon des"

def test_get_zone_by_id_not_found():
    testzone = 10000
    response = client.get(f"/zones/{testzone}")
    assert response.status_code == 404

def test_get_camera_by_id():
    session = TestingSessionLocal()
    testcamera = Camera(name="Test Cam", description="Test Cam Description", ipaddress="127.0.0.1", zone_id=1)
    session.add(testcamera)
    session.commit()
    session.refresh(testcamera)

    response = client.get(f"/cameras/{testcamera.id}")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["name"] == "Test Cam"
    assert data["description"] == "Test Cam Description"
    assert data["ipaddress"] == "127.0.0.1"

def test_get_camera_by_id_not_found():
    testcameraid = 1000
    response = client.get(f"/cameras/{testcameraid}")
    assert response.status_code == 404


def test_get_zone_by_plant_id_not_found():
    plantid = 1000
    response = client.get(f"/plants/zones/{plantid}")
    assert response.status_code == 404


def test_get_plants_not_found():
    response = client.get(
        "/plants/")
    assert response.status_code == 404

def test_get_plants():
    session = TestingSessionLocal()
    testplant = Plant(name="testplant", description="testplantdescription", address="testplant address")
    session.add(testplant)
    session.commit()
    session.refresh(testplant)
    response = client.get(
        "/plants/")
    
    assert response.status_code == 200


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