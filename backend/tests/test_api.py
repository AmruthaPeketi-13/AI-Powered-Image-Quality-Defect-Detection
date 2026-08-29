"""
API integration tests using FastAPI TestClient.
Run: cd backend && pytest tests/ -v
"""

import io
import os

import numpy as np
import pytest
from fastapi.testclient import TestClient
from PIL import Image

# Patch model_is_ready to True + mock predict before importing app
import unittest.mock as mock

# Create a minimal mock so tests don't require trained model on disk
_mock_predict = mock.patch(
    "app.core.model.model_is_ready", return_value=True
)
_mock_infer = mock.patch(
    "app.core.model.predict",
    return_value=(
        [{"issue": "blur", "confidence": 0.85, "severity": "medium"}],
        {"blur": {"laplacian_variance": 0.72}},
    ),
)


@pytest.fixture(scope="module")
def client():
    _mock_predict.start()
    _mock_infer.start()
    from app.main import app
    # Start with a clean table so history tests are deterministic.
    from app.db.database import engine
    from app.db.models import AnalysisResult
    from sqlalchemy import delete
    with engine.begin() as conn:
        conn.execute(delete(AnalysisResult))
    with TestClient(app) as c:
        yield c
    with engine.begin() as conn:
        conn.execute(delete(AnalysisResult))
    _mock_predict.stop()
    _mock_infer.stop()


def _make_jpeg_bytes(width=100, height=100) -> bytes:
    """Create a minimal valid JPEG in memory."""
    img = Image.fromarray(np.random.randint(0, 255, (height, width, 3), dtype=np.uint8))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


# ── /health ───────────────────────────────────────────────────────────────────

def test_health_returns_ok(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


# ── /analyze — happy path ────────────────────────────────────────────────────

def test_analyze_valid_image(client):
    jpeg = _make_jpeg_bytes()
    resp = client.post(
        "/analyze",
        files={"file": ("test.jpg", jpeg, "image/jpeg")},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "quality_score" in data
    assert "quality_label" in data
    assert isinstance(data["issues"], list)
    assert "features" in data
    assert "heatmap" in data


def test_analyze_returns_correct_schema(client):
    jpeg = _make_jpeg_bytes()
    resp = client.post("/analyze", files={"file": ("img.jpg", jpeg, "image/jpeg")})
    data = resp.json()
    assert 0 <= data["quality_score"] <= 100
    assert data["quality_label"] in ("ACCEPTABLE", "DEGRADED", "DEFECTIVE")


# ── /analyze — error cases ───────────────────────────────────────────────────

def test_analyze_unsupported_format_returns_415(client):
    resp = client.post(
        "/analyze",
        files={"file": ("doc.pdf", b"%PDF-fake", "application/pdf")},
    )
    assert resp.status_code == 415


def test_analyze_empty_file_returns_400(client):
    resp = client.post(
        "/analyze",
        files={"file": ("empty.jpg", b"", "image/jpeg")},
    )
    assert resp.status_code == 400


def test_analyze_corrupt_image_returns_400(client):
    resp = client.post(
        "/analyze",
        files={"file": ("corrupt.jpg", b"notanimage123", "image/jpeg")},
    )
    assert resp.status_code == 400


# ── /results ─────────────────────────────────────────────────────────────────

def test_results_list(client):
    resp = client.get("/results")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_results_not_found(client):
    resp = client.get("/results/nonexistent-id-999")
    assert resp.status_code == 404
