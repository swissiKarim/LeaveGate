# scenario-id: US-01/SC-5
"""SC-5: .gitignore excludes .venv, __pycache__ and *.db."""
import json

try:
    with open(".gitignore") as f:
        content = f.read()

    patterns = [".venv", "__pycache__", "*.db"]
    missing = [p for p in patterns if p not in content]

    exit_code = 0 if not missing else 1
except FileNotFoundError:
    missing = ["(file not found)"]
    exit_code = 1

print(json.dumps({
    "exit_code": exit_code,
    "missing_patterns": missing,
}))
