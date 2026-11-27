# scenario-id: US-02/SC-3
"""CLI scenario: leavegate.db is created automatically on startup."""
import json
import os
import tempfile
from pathlib import Path

# Change to a temp dir so init_db() creates leavegate.db there
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
