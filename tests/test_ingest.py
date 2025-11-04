import io
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_ingest_pdf():
    # create fake pdf content
    fake_pdf = io.BytesIO(b"%PDF-1.4\n%fake pdf content")
    response = client.post(
        "/ingest",
        files={"file": ("sample.pdf", fake_pdf, "application/pdf")}
    )
    assert response.status_code == 200
    data = response.json()
    assert "document_ids" in data
    assert isinstance(data["document_ids"], list)
