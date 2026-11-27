# scenario-id: US-02/SC-5
"""CLI scenario: pytest fixtures use in-memory SQLite database."""
import json
import subprocess
import sys

result = subprocess.run(
    [sys.executable, "-m", "pytest", "tests/test_models.py", "-v", "--tb=short", "-q"],
    capture_output=True,
    check=False,
    text=True,
)

print(json.dumps({
    "exit_code": result.returncode,
    "stdout": result.stdout,
    "stderr": result.stderr,
}))
