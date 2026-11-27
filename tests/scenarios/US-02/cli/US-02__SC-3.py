# scenario-id: US-02/SC-3
"""CLI scenario: leavegate.db is created automatically on startup."""
import json
import sys
from pathlib import Path

# Add workspace root to sys.path so 'app' package is importable
_workspace = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(_workspace))

from app.database import DATABASE_URL, engine, init_db  # must come after sys.path setup


def _run():
    # Derive the actual DB file path from DATABASE_URL
    # DATABASE_URL is like "sqlite:////abs/path/leavegate.db"
    db_file = Path(DATABASE_URL.replace("sqlite:///", ""))
    # Remove stale DB so we verify fresh creation
    if db_file.exists():
        db_file.unlink()
    # Dispose pool so SQLite re-opens the file on next connect
    engine.dispose()
    init_db()
    return db_file.exists()


exists = _run()
exit_code = 0 if exists else 1
print(json.dumps({
    "exit_code": exit_code,
    "stdout": f"leavegate.db exists: {exists}",
    "stderr": "",
}))
