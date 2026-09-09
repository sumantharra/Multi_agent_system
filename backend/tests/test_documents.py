from pathlib import Path

from fastapi.testclient import TestClient

from app.core.config import Settings

MINIMAL_PDF = (
    b"%PDF-1.4\n"
    b"1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n"
    b"2 0 obj<</Type/Pages/Count 0/Kids[]>>endobj\n"
    b"trailer<</Root 1 0 R>>\n"
    b"%%EOF\n"
)


def _create_hostel(client: TestClient, *, code: str = "doc-01") -> str:
    response = client.post(
        "/api/v1/hostels",
        json={
            "name": f"Hostel {code}",
            "code": code,
            "default_rate_per_liter": "45.50",
        },
    )
    assert response.status_code == 201
    return response.json()["id"]


def _upload(
    client: TestClient,
    hostel_id: str,
    *,
    filename: str = "invoice.pdf",
    content: bytes = MINIMAL_PDF,
    content_type: str = "application/pdf",
    force: bool = False,
    document_type: str = "invoice",
):
    return client.post(
        "/api/v1/documents/upload",
        data={
            "hostel_id": hostel_id,
            "document_type": document_type,
            "force": str(force).lower(),
        },
        files={"file": (filename, content, content_type)},
    )


def test_upload_pdf_is_queued_and_stored_on_disk(
    client: TestClient, settings: Settings
) -> None:
    hostel_id = _create_hostel(client)
    response = _upload(client, hostel_id)
    assert response.status_code == 201
    body = response.json()
    assert body["hostel_id"] == hostel_id
    assert body["processing_status"] == "queued"
    assert body["extraction_status"] == "not_started"
    assert body["mime_type"] == "application/pdf"
    assert body["document_type"] == "invoice"
    assert body["file_name"] == "invoice.pdf"
    assert body["content_hash"]

    stored = Path(settings.local_upload_dir) / body["storage_key"]
    assert stored.is_file()
    assert stored.read_bytes() == MINIMAL_PDF

    fetched = client.get(f"/api/v1/documents/{body['id']}")
    assert fetched.status_code == 200
    assert fetched.json()["id"] == body["id"]

    listed = client.get(
        "/api/v1/documents",
        params={"processing_status": "queued", "hostel_id": hostel_id},
    )
    assert listed.status_code == 200
    assert listed.json()["total"] == 1
    assert listed.json()["items"][0]["id"] == body["id"]


def test_reject_non_pdf(client: TestClient) -> None:
    hostel_id = _create_hostel(client, code="doc-02")
    response = _upload(
        client,
        hostel_id,
        filename="notes.txt",
        content=b"not a pdf",
        content_type="text/plain",
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_reject_oversized_pdf(client: TestClient, settings: Settings) -> None:
    settings.max_upload_bytes = 40
    hostel_id = _create_hostel(client, code="doc-03")
    response = _upload(client, hostel_id, content=MINIMAL_PDF + b"x" * 80)
    assert response.status_code == 422
    assert "too large" in response.json()["error"]["message"].lower()


def test_idempotent_reupload_same_hash_and_hostel(
    client: TestClient, settings: Settings
) -> None:
    hostel_id = _create_hostel(client, code="doc-04")
    first = _upload(client, hostel_id)
    second = _upload(client, hostel_id)
    assert first.status_code == 201
    assert second.status_code == 200
    assert second.json()["id"] == first.json()["id"]

    listed = client.get("/api/v1/documents", params={"hostel_id": hostel_id})
    assert listed.json()["total"] == 1

    files = list(Path(settings.local_upload_dir).rglob("*.pdf"))
    assert len(files) == 1


def test_force_reupload_keeps_one_row_and_requeues(
    client: TestClient, settings: Settings
) -> None:
    hostel_id = _create_hostel(client, code="doc-05")
    first = _upload(client, hostel_id)
    forced = _upload(client, hostel_id, force=True)
    assert forced.status_code == 200
    assert forced.json()["id"] == first.json()["id"]
    assert forced.json()["processing_status"] == "queued"
    assert (Path(settings.local_upload_dir) / forced.json()["storage_key"]).is_file()


def test_unknown_hostel_not_found(client: TestClient) -> None:
    response = _upload(client, "00000000-0000-0000-0000-000000000001")
    assert response.status_code == 404
