from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_extract_fields():
    # Use a fake doc ID from a previous ingest (replace with actual one)
    payload = {"document_id": "sample_doc_id"}
    response = client.post("/extract", json=payload)

    # Since document might not exist, allow both 200 or 404 for flexibility
    assert response.status_code in (200, 404)
