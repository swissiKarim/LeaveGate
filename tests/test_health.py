"""Tests for the health endpoint and app bootstrap."""
import importlib
import subprocess
import sys


def _ensure_deps():
    """Install requirements if fastapi is not available."""
    try:
        import fastapi  # noqa: F401
    except ImportError:
        import pathlib
        req = pathlib.Path(__file__).parent.parent / "requirements.txt"
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-q",
             "--break-system-packages", "-r", str(req)],
            check=True,
        )
        importlib.invalidate_caches()


def _get_client():
    _ensure_deps()
    from fastapi.testclient import TestClient

    from app.main import app
    return TestClient(app)


def test_health_returns_200():
    client = _get_client()
    response = client.get("/health")
    assert response.status_code == 200


def test_health_returns_ok_json():
    client = _get_client()
    response = client.get("/health")
    assert response.json() == {"status": "ok"}


def test_docs_returns_200():
    client = _get_client()
    response = client.get("/docs")
    assert response.status_code == 200


def test_app_instance_exported():
    _ensure_deps()
    from fastapi import FastAPI

    from app.main import app as exported_app
    assert isinstance(exported_app, FastAPI)
