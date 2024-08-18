# test_zones.py

from app.models import Zone
from app.routers import zones
from tests.test_utils import setup_router_override, client, TestingSessionLocal

setup_router_override(zones)

def test_get_zones():
    response = client.get("/zones/")
    assert response.status_code == 200, response.text
    data = response.json()
    assert len(data) == 0

def test_create_zone():
    response = client.post(
        "/zones/",
        json={"title": "new zone for test", "description": "new zone for test description", "assignee_id": 1, "plant_id": 1, "assignee_id": 1, "zoneconfidence": 0.75},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["title"] == "new zone for test"
    assert data["description"] == "new zone for test description"
    assert data["zoneconfidence"] == 0.75
    

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

def test_get_zone_by_plant_id_not_found():
    plantid = 1000
    response = client.get(f"/plants/zones/{plantid}")
    assert response.status_code == 404
