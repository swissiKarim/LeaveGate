# scenario-id: US-02/SC-5
"""CLI scenario: pytest fixtures use in-memory SQLite database."""
import json
import subprocess
import sys
from pathlib import Path


def _workspace():
    return Path(__file__).resolve().parents[4]


result = subprocess.run(
    [sys.executable, "-m", "pytest", "tests/test_models.py", "-v", "--tb=short", "-q"],
    capture_output=True,
    check=False,
    cwd=str(_workspace()),
    text=True,
)

print(json.dumps({
    "exit_code": result.returncode,
    "stdout": result.stdout,
    "stderr": result.stderr,
}))
