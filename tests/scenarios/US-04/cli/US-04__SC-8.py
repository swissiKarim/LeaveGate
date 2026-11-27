# scenario-id: US-04/SC-8
"""SC-8: pytest covers all four employee endpoints including 404; exit_code must be 0."""
import json
import subprocess
import sys

result = subprocess.run(
    [sys.executable, "-m", "pytest", "tests/test_employees.py", "--tb=short", "-q"],
    capture_output=True,
    text=True,
)

print(json.dumps({
    "exit_code": result.returncode,
    "stdout": result.stdout[-3000:],
    "stderr": result.stderr[-500:],
}))
