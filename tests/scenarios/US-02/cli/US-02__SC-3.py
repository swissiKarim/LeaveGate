# scenario-id: US-02/SC-3
"""CLI scenario: leavegate.db is created automatically on startup."""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

# Workspace root: resolve relative to this file (4 parents up) or use CWD as fallback
workspace = Path(__file__).parents[4].resolve()
if not (workspace / "app").is_dir():
    workspace = Path.cwd()

env = os.environ.copy()
# Prepend workspace to PYTHONPATH so subprocess finds the app package
env["PYTHONPATH"] = str(workspace) + os.pathsep + env.get("PYTHONPATH", "")

with tempfile.TemporaryDirectory() as tmpdir:
    script = (
        f"import os; os.chdir({tmpdir!r}); "
        "from app.database import init_db; init_db(); "
        "import pathlib; "
        f"db = pathlib.Path({tmpdir!r}) / 'leavegate.db'; "
        "assert db.exists(), f'DB not found: ' + str(db)"
    )
    result = subprocess.run(
        [sys.executable, "-c", script],
        capture_output=True,
        check=False,
        env=env,
        text=True,
    )

print(json.dumps({
    "exit_code": result.returncode,
    "stdout": result.stdout,
    "stderr": result.stderr,
}))
