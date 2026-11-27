# scenario-id: US-02/SC-4
"""CLI scenario: app/database.py provides a central session factory."""
import json
import sys
from pathlib import Path


def _setup_path():
    """Add workspace root to sys.path so 'app' package is importable."""
    workspace = Path(__file__).resolve().parents[4]
    if str(workspace) not in sys.path:
        sys.path.insert(0, str(workspace))


def _run():
    _setup_path()
    from app.database import Base, SessionLocal, engine, get_db

    assert SessionLocal is not None
    assert get_db is not None
    assert Base is not None
    assert engine is not None
    return "ok"


try:
    result = _run()
    print(json.dumps({"stdout": result, "exit_code": 0}))
except AssertionError as e:
    print(json.dumps({"stdout": f"error: {e}", "exit_code": 1}))
    sys.exit(1)
