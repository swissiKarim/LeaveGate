# scenario-id: US-03/SC-4
"""SC-4: pytest covers 404 and 422 error format — exit_code must be 0."""
import json
import subprocess
import sys

result = subprocess.run(
    [sys.executable, "-m", "pytest", "tests/test_error_format.py", "--tb=short", "-q"],
    capture_output=True,
    text=True,
)

print(json.dumps({
    "exit_code": result.returncode,
    "stdout": result.stdout[-3000:],
    "stderr": result.stderr[-500:],
}))
