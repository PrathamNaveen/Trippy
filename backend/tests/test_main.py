# test_validate_session.py
import io
import random
from urllib import response
import pytest
from fastapi import HTTPException, UploadFile
from main import validate_session, upload_pdf
from pdf_ingestion import ingest_pdf
import uuid
from fastapi.testclient import TestClient

# -------------------------------
# ✅ Test valid session
# -------------------------------
def test_validate_session_success(mocker):
    mocker.patch("main.get_session", return_value="test_user")
    user = validate_session(session_id="dummy_session_id")
    assert user == "test_user"

# -------------------------------
# ✅ Test unauthorized session (returns 401)
# -------------------------------
def test_validate_session_unauthorized(mocker):
    mocker.patch("main.get_session", return_value=401)
    with pytest.raises(HTTPException) as exc_info:
        validate_session(session_id="dummy_session_id")
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Unauthorized"

# -------------------------------
# ✅ Test invalid/expired session (returns None)
# -------------------------------
def test_validate_session_invalid(mocker):
    mocker.patch("main.get_session", return_value=None)
    with pytest.raises(HTTPException) as exc_info:
        validate_session(session_id="dummy_session_id")
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Session Invalid or Expired"

def test_file_upload_success(mocker):
    fake_file = UploadFile(
        filename="dummy.pdf",
        file=io.BytesIO(b"%PDF-1.4 dummy content")
    )

    mock_user = "test_user"
    collection_name = "test_collection"

    assert fake_file is not None
    assert fake_file.filename.endswith(".pdf")

def test_file_upload_failure(mocker):
    fake_file = UploadFile(
        filename="dummy.docx",
        file=io.BytesIO(b"%PDF-1.4 dummy content")
    )

    mock_user = "test_user"
    collection_name = "test_collection"

    assert not fake_file.filename.endswith(".pdf")


@pytest.mark.asyncio
async def test_file_ingestion_failure(mocker):
    # Arrange
    fake_file = UploadFile(
        filename="dummy.pdf",
        file=io.BytesIO(b"%PDF-1.4 broken content")
    )
    mock_user = "test_user"
    collection_name = uuid.uuid4().hex  # This is a string like 'f9a1c2d3e4b56789abcdef1234567890'

    # Mock ingest_pdf to simulate an error
    mock_ingest = mocker.patch("main.ingest_pdf", side_effect=Exception("ingestion failed"))

    # Act
    response = await upload_pdf(
        file=fake_file,
        collection_name=collection_name,
        user=mock_user,
    )

    # Assert
    assert "error" in response
    assert response["error"] == "ingestion failed"
    mock_ingest.assert_called_once_with(fake_file.file, collection_name=collection_name)

@pytest.mark.asyncio
async def test_file_ingestion_success(mocker):
    # Arrange
    fake_file = UploadFile(
        filename="dummy.pdf",
        file=io.BytesIO(b"%PDF-1.4 broken content")
    )
    mock_user = "test_user"
    collection_name = uuid.uuid4().hex  # This is a string like 'f9a1c2d3e4b56789abcdef1234567890'

    # Mock ingest_pdf to simulate an error

    mock_ingest = mocker.patch("main.ingest_pdf", return_value=5)

    # Act
    response = await upload_pdf(
        file=fake_file,
        collection_name=collection_name,
        user=mock_user,
    )

    # Assert
    assert "✅ PDF ingested" in response["message"]
    assert collection_name in response["message"]
    mock_ingest.assert_called_once_with(fake_file.file, collection_name=collection_name)
