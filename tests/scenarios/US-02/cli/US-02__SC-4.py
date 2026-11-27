# scenario-id: US-02/SC-4
"""CLI scenario: app/database.py provides a central session factory."""
import json
import sys
from pathlib import Path

# Ensure workspace root is on sys.path regardless of CWD
workspace = Path(__file__).parents[4].resolve()
if not (workspace / "app").is_dir():
    workspace = Path.cwd()
if str(workspace) not in sys.path:
    sys.path.insert(0, str(workspace))

try:
    from app.database import Base, SessionLocal, engine, get_db

    assert SessionLocal is not None
    assert get_db is not None
    assert Base is not None
    assert engine is not None
    print(json.dumps({"stdout": "ok", "exit_code": 0}))
except AssertionError as e:
    print(json.dumps({"stdout": f"error: {e}", "exit_code": 1}))
    sys.exit(1)
