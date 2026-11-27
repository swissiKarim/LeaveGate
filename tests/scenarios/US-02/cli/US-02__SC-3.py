# scenario-id: US-02/SC-3
"""CLI scenario: leavegate.db is created automatically on startup."""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

workspace = Path(__file__).parents[4]  # /workspace

with tempfile.TemporaryDirectory() as tmpdir:
    result = subprocess.run(
        [
            sys.executable, "-c",
            (
                "import sys; sys.path.insert(0, r'" + str(workspace) + "'); "
                "import os; os.chdir(r'" + tmpdir + "'); "
                "from app.database import init_db; init_db(); "
                "import pathlib; "
                "db = pathlib.Path(r'" + tmpdir + "') / 'leavegate.db'; "
                "assert db.exists(), f'DB not found: {db}'"
            ),
        ],
        capture_output=True,
        check=False,
        text=True,
    )

print(json.dumps({
    "exit_code": result.returncode,
    "stdout": result.stdout,
    "stderr": result.stderr,
}))
