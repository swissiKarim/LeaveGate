"""Pytest fixtures for LeaveGate tests – use in-memory SQLite."""
import subprocess
import sys
from pathlib import Path

import pytest


def _ensure_deps():
    """Install requirements if fastapi is not importable."""
    try:
        import fastapi  # noqa: F401
    except ImportError:
        req = Path(__file__).parent.parent / "requirements.txt"
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-q",
             "--break-system-packages", "-r", str(req)],
            check=True,
        )
        import importlib
        import site
        importlib.reload(site)


def pytest_configure(config):
    _ensure_deps()


# In-memory SQLite for tests
TEST_DATABASE_URL = "sqlite://"


@pytest.fixture(scope="session")
def engine():
    """Create a fresh in-memory SQLite engine for the test session."""
    from sqlalchemy import create_engine as _create_engine

    import app.models  # noqa: F401 – registers all ORM models on Base
    from app.database import Base

    _engine = _create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(bind=_engine)
    yield _engine
    Base.metadata.drop_all(bind=_engine)
    _engine.dispose()


@pytest.fixture()
def db_session(engine):
    """Yield a transactional DB session that is rolled back after each test."""
    from sqlalchemy.orm import sessionmaker

    connection = engine.connect()
    transaction = connection.begin()
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=connection)
    session = TestingSessionLocal()
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture()
def client(db_session):
    """FastAPI test client wired to the in-memory test DB session."""
    from fastapi.testclient import TestClient

    from app.database import get_db
    from app.main import app

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
