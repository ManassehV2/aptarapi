'''from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base
from app.main import app
from app.routers import zones

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

client = TestClient(app)


def test_create_zone():
    response = client.post(
        "/zones/",
        json={"title": "new zone for test", "description": "new zone for test description", "assignee_id": 1, "plant_id": 1},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["title"] == "new zone for test"
    assert data["description"] == "new zone for test description"
    
'''    