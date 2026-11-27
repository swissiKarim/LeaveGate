# scenario-id: US-02/SC-3
"""CLI scenario: leavegate.db is created automatically on startup."""
import json
import os
import sys
import tempfile
from pathlib import Path

# Add workspace root to sys.path so 'app' package is importable
# File is at <workspace>/tests/scenarios/US-02/cli/US-02__SC-3.py → 4 parents up
_workspace = Path(__file__).resolve().parents[4]
if str(_workspace) not in sys.path:
    sys.path.insert(0, str(_workspace))

with tempfile.TemporaryDirectory() as tmpdir:
    original_cwd = os.getcwd()
    os.chdir(tmpdir)
    try:
        from app.database import init_db
        init_db()
        db_path = Path(tmpdir) / "leavegate.db"
        exists = db_path.exists()
    finally:
        os.chdir(original_cwd)

exit_code = 0 if exists else 1
print(json.dumps({
    "exit_code": exit_code,
    "stdout": f"leavegate.db exists: {exists}",
    "stderr": "",
}))
