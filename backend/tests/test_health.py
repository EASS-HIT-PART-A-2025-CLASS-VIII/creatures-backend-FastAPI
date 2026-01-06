from fastapi.testclient import TestClient
from app.app import app

client = TestClient(app)


def test_docs_accessible():
    """Verify that the Swagger UI is reachable."""
    response = client.get("/docs")
    assert response.status_code == 200


def test_openapi_accessible():
    """Verify that the OpenAPI JSON schema is reachable."""
    response = client.get("/openapi.json")
    assert response.status_code == 200
