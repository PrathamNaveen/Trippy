# test_validate_session.py
import pytest
from fastapi import HTTPException
from main import validate_session

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

def test_root():
    