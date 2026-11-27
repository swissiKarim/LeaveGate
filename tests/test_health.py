"""Tests for the health endpoint and app bootstrap."""
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_returns_200():
    response = client.get("/health")
    assert response.status_code == 200


def test_health_returns_ok_json():
    response = client.get("/health")
    assert response.json() == {"status": "ok"}


def test_docs_returns_200():
    response = client.get("/docs")
    assert response.status_code == 200


def test_app_instance_exported():
    from app.main import app as exported_app
    from fastapi import FastAPI
    assert isinstance(exported_app, FastAPI)
