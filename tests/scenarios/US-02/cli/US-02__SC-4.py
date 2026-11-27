# scenario-id: US-02/SC-4
"""CLI scenario: app/database.py provides a central session factory."""
import json
import sys
from pathlib import Path

# Add workspace root to sys.path so 'app' package is importable
# File is at <workspace>/tests/scenarios/US-02/cli/US-02__SC-4.py → 4 parents up
_workspace = Path(__file__).resolve().parents[4]
if str(_workspace) not in sys.path:
    sys.path.insert(0, str(_workspace))

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
