import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.app import app
from app.db import get_session

# 1. Setup In-Memory Database for Testing
engine = create_engine(
    "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
)


@pytest.fixture(name="session")
def session_fixture():
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    SQLModel.metadata.drop_all(engine)


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    yield TestClient(app)
    app.dependency_overrides.clear()


# --- Happy Path Tests ---


def test_create_creature(client: TestClient):
    payload = {
        "name": "Test Dragon",
        "mythology": "Norse",
        "creature_type": "Reptile",
        "danger_level": 9,
        "habitat": "Mountains",
    }
    response = client.post("/creatures/", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == payload["name"]
    assert "id" in data
    assert "api.dicebear.com" in data["image_url"]


def test_get_creatures(client: TestClient):
    payload = {
        "name": "Unicorn",
        "mythology": "Greek",
        "creature_type": "Equine",
        "danger_level": 1,
    }
    client.post("/creatures/", json=payload)

    response = client.get("/creatures/")
    assert response.status_code == 200
    data = response.json()
    names = [c["name"] for c in data]
    assert "Unicorn" in names


def test_update_creature(client: TestClient):
    create_res = client.post(
        "/creatures/",
        json={
            "name": "Base Creature",
            "mythology": "Test",
            "creature_type": "Test",
            "danger_level": 5,
        },
    )
    creature_id = create_res.json()["id"]

    payload = {
        "name": "Evolved Creature",
        "mythology": "Test",
        "creature_type": "God",
        "danger_level": 10,
    }
    response = client.put(f"/creatures/{creature_id}", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Evolved Creature"
    assert data["danger_level"] == 10


def test_delete_creature(client: TestClient):
    create_res = client.post(
        "/creatures/",
        json={
            "name": "To Delete",
            "mythology": "Test",
            "creature_type": "Test",
            "danger_level": 1,
        },
    )
    creature_id = create_res.json()["id"]

    response = client.delete(f"/creatures/{creature_id}")
    assert response.status_code == 200
    assert response.json() == {"detail": "creature deleted successfully"}

    get_res = client.get("/creatures/")
    current_ids = [c["id"] for c in get_res.json()]
    assert creature_id not in current_ids


# --- Negative Tests (404 Not Found) ---


def test_get_creature_not_found(client: TestClient):
    response = client.get("/creatures/99999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Creature not found"


def test_update_creature_not_found(client: TestClient):
    payload = {
        "name": "Ghost",
        "mythology": "None",
        "creature_type": "Spirit",
        "danger_level": 0,
    }
    response = client.put("/creatures/99999", json=payload)
    assert response.status_code == 404
    assert response.json()["detail"] == "Creature not found"


def test_delete_creature_not_found(client: TestClient):
    response = client.delete("/creatures/99999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Creature not found"


# --- Validation Tests (422 Unprocessable Entity) ---


def test_create_creature_missing_field(client: TestClient):
    # Missing 'name'
    payload = {
        "mythology": "Norse",
        "creature_type": "Reptile",
        "danger_level": 9,
    }
    response = client.post("/creatures/", json=payload)
    assert response.status_code == 422


def test_create_creature_invalid_type(client: TestClient):
    # 'danger_level' should be int, verify string fails if pydantic strict mode or if it can't coerce
    # Pydantic often coerces "10" to 10. Let's send "Very Dangerous" which can't be int.
    payload = {
        "name": "Bad Data",
        "mythology": "Norse",
        "creature_type": "Reptile",
        "danger_level": "High",  # Invalid
    }
    response = client.post("/creatures/", json=payload)
    assert response.status_code == 422


# --- State Persistence Verification ---


def test_create_then_list(client: TestClient):
    """Verify that a created item appears in the list immediately."""
    name = "Persistence Check"
    client.post(
        "/creatures/",
        json={
            "name": name,
            "mythology": "Test",
            "creature_type": "Test",
            "danger_level": 5,
        },
    )

    response = client.get("/creatures/")
    assert response.status_code == 200
    names = [c["name"] for c in response.json()]
    assert name in names


def test_update_then_read_reflects_change(client: TestClient):
    """Verify that an update is immediately visible in a get-one call."""
    # 1. Create
    res = client.post(
        "/creatures/",
        json={
            "name": "V1",
            "mythology": "Test",
            "creature_type": "Test",
            "danger_level": 1,
        },
    )
    cid = res.json()["id"]

    # 2. Update
    client.put(
        f"/creatures/{cid}",
        json={
            "name": "V2",
            "mythology": "Test",
            "creature_type": "Test",
            "danger_level": 2,
        },
    )

    # 3. Read
    res = client.get(f"/creatures/{cid}")
    assert res.status_code == 200
    assert res.json()["name"] == "V2"  # Should match V2
