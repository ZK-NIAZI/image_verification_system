# ─────────────────────────────────────────────────────────────
# tests/test_api.py
# AI Image Verification System — API Tests
#
# Uses FastAPI's TestClient (no server needed).
# Run:  python -m pytest tests/test_api.py -v
# ─────────────────────────────────────────────────────────────

import os
import sys
import pytest
from fastapi.testclient import TestClient

# Ensure project root is on the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import app

client = TestClient(app)

ASSETS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets"
)


# ── Helper ────────────────────────────────────────────────────────
def _upload(filename, verbose=True):
    """Upload a file from the assets directory to POST /verify."""
    filepath = os.path.join(ASSETS_DIR, filename)
    params = {"verbose": "true"} if verbose else {}
    with open(filepath, "rb") as f:
        return client.post("/verify", files={"file": (filename, f, "image/jpeg")}, params=params)


# ── Health Check ──────────────────────────────────────────────
class TestHealthEndpoint:
    def test_health_returns_200(self):
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_has_required_fields(self):
        data = client.get("/health").json()
        assert "status" in data
        assert "model_loaded" in data
        assert "version" in data

    def test_health_model_loaded(self):
        data = client.get("/health").json()
        assert data["model_loaded"] is True
        assert data["status"] == "healthy"


# ── Valid Image ───────────────────────────────────────────────
class TestValidImage:
    def test_valid_face_returns_200(self):
        response = _upload("one_face.jpg")
        assert response.status_code == 200

    def test_valid_face_is_valid(self):
        data = _upload("one_face.jpg").json()
        assert data["success"] is True
        assert data["result"]["valid"] is True
        assert data["result"]["reason"] == "SUCCESS"


# ── Pipeline Failures (still HTTP 200) ────────────────────────
class TestPipelineFailures:
    def test_blurry_image(self):
        data = _upload("blurry_image.jpg").json()
        assert data["success"] is True
        assert data["result"]["valid"] is False
        assert data["result"]["reason"] == "TOO_BLURRY"

    def test_dark_image(self):
        data = _upload("dark_image.jpg").json()
        assert data["success"] is True
        assert data["result"]["valid"] is False
        assert data["result"]["reason"] == "TOO_DARK"

    def test_bright_image(self):
        data = _upload("bright_image.jpg").json()
        assert data["success"] is True
        assert data["result"]["valid"] is False
        assert data["result"]["reason"] == "TOO_BRIGHT"

    def test_no_face_image(self):
        """
        no_face.jpg might fail on lighting or clarity first depending
        on the image. We just check that valid is False.
        """
        data = _upload("no_face.jpg").json()
        assert data["success"] is True
        assert data["result"]["valid"] is False

    def test_multiple_faces(self):
        """
        two_faces.jpg might fail on lighting or clarity first depending
        on the image. We just check that valid is False.
        """
        data = _upload("two_faces.jpg").json()
        assert data["success"] is True
        assert data["result"]["valid"] is False


# ── Request Validation Errors ─────────────────────────────────
class TestRequestValidation:
    def test_invalid_file_type(self):
        """Uploading a .txt file should return 400."""
        content = b"this is not an image"
        response = client.post(
            "/verify",
            files={"file": ("document.txt", content, "text/plain")},
        )
        assert response.status_code == 400
        data = response.json()
        assert data["success"] is False
        assert data["error"]["code"] == "INVALID_FILE_TYPE"

    def test_empty_file(self):
        """Uploading an empty file should return 400."""
        response = client.post(
            "/verify",
            files={"file": ("empty.jpg", b"", "image/jpeg")},
        )
        assert response.status_code == 400
        data = response.json()
        assert data["success"] is False
        assert data["error"]["code"] == "EMPTY_FILE"

    def test_no_file_uploaded(self):
        """Posting without a file should return 422 (FastAPI validation)."""
        response = client.post("/verify")
        assert response.status_code == 422


# ── Response Structure ────────────────────────────────────────
class TestResponseStructure:
    def test_success_response_has_timestamp(self):
        data = _upload("one_face.jpg").json()
        assert "timestamp" in data

    def test_success_response_has_result_fields(self):
        data = _upload("one_face.jpg").json()
        result = data["result"]
        assert "valid" in result
        assert "reason" in result
        assert "message" in result
        assert "details" in result


# ── Minimal (default) Response ─────────────────────────────────────
class TestMinimalResponse:
    def test_default_response_is_minimal(self):
        """Without ?verbose=true the response should not include 'result' or 'timestamp'."""
        data = _upload("one_face.jpg", verbose=False).json()
        assert data["success"] is True
        assert data["valid"] is True
        assert data["reason"] == "SUCCESS"
        assert "message" in data
        # These should NOT be present in the minimal response
        assert "result" not in data
        assert "timestamp" not in data
        assert "inference_time_ms" not in data

    def test_verbose_via_query_param(self):
        """?verbose=true should return the full response."""
        data = _upload("one_face.jpg", verbose=True).json()
        assert "result" in data
        assert "timestamp" in data
        assert "inference_time_ms" in data

    def test_verbose_via_header(self):
        """X-Verbose: true header should also return the full response."""
        filepath = os.path.join(ASSETS_DIR, "one_face.jpg")
        with open(filepath, "rb") as f:
            response = client.post(
                "/verify",
                files={"file": ("one_face.jpg", f, "image/jpeg")},
                headers={"X-Verbose": "true"},
            )
        data = response.json()
        assert "result" in data
        assert "timestamp" in data

    def test_minimal_failure_response(self):
        """Failed validation should also be minimal by default."""
        data = _upload("dark_image.jpg", verbose=False).json()
        assert data["success"] is True
        assert data["valid"] is False
        assert data["reason"] == "TOO_DARK"
        assert "message" in data
        assert "result" not in data
