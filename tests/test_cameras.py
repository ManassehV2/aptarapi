# test_cameras.py

from app.models import Camera
from app.routers import cameras
from tests.test_utils import TestingSessionLocal, setup_router_override, client


setup_router_override(cameras)

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
