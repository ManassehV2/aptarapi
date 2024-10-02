# test_plants.py

from app import schemas
from app.models import Plant
from app.routers import plants
from tests.test_utils import setup_router_override, client, TestingSessionLocal

setup_router_override(plants)

def test_get_plants_not_found():
    response = client.get("/plants/?plant_status=active")
    assert response.status_code == 200, response.text
    data = response.json()

    assert len(data) == 0

def test_create_plant():
    response = client.post(
        "/plants/",
        json={"name": "new plant for test", "description": "new plant for test description", "address": "New plant address", "plantConfidence": 0.85},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["name"] == "new plant for test"
    assert data["description"] == "new plant for test description"
    assert data["address"] == "New plant address"
    assert data["plantConfidence"] == 0.85

def test_get_plants():
    session = TestingSessionLocal()
    testplant = Plant(name="testplant", description="testplantdescription", address="testplant address", plantConfidence=0.85)
    session.add(testplant)
    session.commit()
    session.refresh(testplant)
    response = client.get("/plants/?plant_status=inactive")
    assert response.status_code == 200

def test_update_plant_status_200():
    session = TestingSessionLocal()
    testplant = Plant(
        name="testplant", 
        description="testplantdescription", 
        address="testplant address", 
        plantConfidence=0.85, 
        plantstatus= schemas.PlantStatusEnum.active)
    
    session.add(testplant)
    session.commit()
    session.refresh(testplant)
    response = client.delete(f"/plants/{testplant.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "testplant"
    assert data["plantstatus"] == schemas.PlantStatusEnum.inactive

def test_update_plant_status_404():
    response = client.delete("/plants/1000000")
    assert response.status_code == 404

def test_update_plant_status_400():
    session = TestingSessionLocal()
    testplant = Plant(
        name="testplant", 
        description="testplantdescription", 
        address="testplant address", 
        plantConfidence=0.85, 
        plantstatus= schemas.PlantStatusEnum.inactive)
    
    session.add(testplant)
    session.commit()
    session.refresh(testplant)
    response = client.delete(f"/plants/{testplant.id}")
    assert response.status_code == 400