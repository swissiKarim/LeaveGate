# scenario-id: US-05/SC-15
"""SC-15: pytest covers all state machine transitions and business rules."""
import json
import subprocess
import sys
from pathlib import Path

workspace = Path(__file__).resolve().parents[4]

result = subprocess.run(
    [sys.executable, "-m", "pytest", "tests/test_domain.py", "-v", "--tb=short", "-q"],
    cwd=str(workspace),
    capture_output=True,
    text=True,
)

print(json.dumps({
    "exit_code": result.returncode,
    "stdout": result.stdout[-3000:] if len(result.stdout) > 3000 else result.stdout,
    "stderr": result.stderr[-1000:] if len(result.stderr) > 1000 else result.stderr,
}))
