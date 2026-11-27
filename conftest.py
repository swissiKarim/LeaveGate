"""Root conftest: ensure runtime dependencies are installed before test collection."""
import subprocess
import sys
from pathlib import Path


def pytest_configure(config):
    """Install requirements if fastapi is not importable."""
    try:
        import fastapi  # noqa: F401
    except ImportError:
        req_file = Path(__file__).parent / "requirements.txt"
        if req_file.exists():
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "-q",
                 "--break-system-packages", "-r", str(req_file)],
                check=True,
            )
