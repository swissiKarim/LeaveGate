# scenario-id: US-01/SC-4
"""SC-4: pytest suite passes green."""
import json
import subprocess
import sys

result = subprocess.run(
    [sys.executable, "-m", "pytest", "--tb=short", "-q"],
    capture_output=True,
    text=True,
)

print(json.dumps({
    "exit_code": result.returncode,
    "stdout": result.stdout[-2000:],
    "stderr": result.stderr[-500:],
}))
