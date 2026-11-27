"""Central database session factory for LeaveGate."""
import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# Use DATABASE_URL env var if set, otherwise default to leavegate.db in the
# directory from which the process was started (or the app package parent).
_default_db_path = Path(os.environ.get("APP_ROOT", Path(__file__).parent.parent)) / "leavegate.db"
DATABASE_URL = os.environ.get("DATABASE_URL", f"sqlite:///{_default_db_path}")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    """FastAPI dependency: yields a database session and closes it afterwards."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Create all tables (no-op if they already exist)."""
    # Import models so their metadata is registered on Base before create_all
    import app.models  # noqa: F401

    Base.metadata.create_all(bind=engine)
