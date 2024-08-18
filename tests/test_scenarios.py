# test_scenarios.py

from app.models import Scenario, Zone
from app.routers import scenario
from tests.test_utils import setup_router_override, client, TestingSessionLocal

setup_router_override(scenario)

def test_get_scenarios_not_found():
    response = client.get("/scenario/")
    assert response.status_code == 404

def test_create_scenario():
    response = client.post(
        "/scenario/",
        json={"name": "new scenario for test", "description": "new scenario for test description"},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["name"] == "new scenario for test"
    assert data["description"] == "new scenario for test description"

def test_get_scenarios():
    session = TestingSessionLocal()
    testscenario1 = Scenario(name="test scenario", description="test zon des")
    testscenario2 = Scenario(name="test scenario 2", description="test zon des")
    session.add(testscenario1)
    session.add(testscenario2)
    session.commit()

    response = client.get(f"/scenario/")
    assert response.status_code == 200, response.text
    data = response.json()
    assert len(data) >= 2