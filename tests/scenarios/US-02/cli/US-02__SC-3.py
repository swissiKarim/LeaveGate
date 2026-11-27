# scenario-id: US-02/SC-3
"""CLI scenario: leavegate.db is created automatically on startup."""
import json
import sys
from pathlib import Path


def _setup_path():
    """Add workspace root to sys.path so 'app' package is importable."""
    workspace = Path(__file__).resolve().parents[4]
    if str(workspace) not in sys.path:
        sys.path.insert(0, str(workspace))
    return workspace


def _run():
    workspace = _setup_path()
    from app.database import DATABASE_URL, engine, init_db

    db_file = Path(DATABASE_URL.replace("sqlite:///", ""))
    if not db_file.is_absolute():
        db_file = workspace / db_file
    if db_file.exists():
        db_file.unlink()
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
