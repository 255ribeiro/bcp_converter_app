from pathlib import Path
import sys


# Ensure local src package imports resolve in CI and local builds.
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from bcp_converter.app import run


if __name__ == "__main__":
    run()