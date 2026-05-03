from datetime import datetime
from pathlib import Path
import sys
import tempfile
import traceback


# Ensure local src package imports resolve in CI and local builds.
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from bcp_converter.app import run


def _write_crash_log(exc: BaseException) -> Path:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    details = "\n".join(
        [
            "BCP Converter startup failure",
            f"Timestamp: {timestamp}",
            f"Python: {sys.version}",
            f"Executable: {sys.executable}",
            "",
            "Traceback:",
            "".join(traceback.format_exception(type(exc), exc, exc.__traceback__)),
        ]
    )

    candidate_dirs = []
    executable_path = Path(sys.executable)
    candidate_dirs.append(executable_path.parent)
    candidate_dirs.append(Path(tempfile.gettempdir()))

    for directory in candidate_dirs:
        try:
            directory.mkdir(parents=True, exist_ok=True)
            log_path = directory / "bcp-converter-crash.log"
            log_path.write_text(details, encoding="utf-8")
            return log_path
        except Exception:
            continue

    raise RuntimeError("Unable to create crash log in known locations")


if __name__ == "__main__":
    try:
        run()
    except Exception as exc:
        try:
            path = _write_crash_log(exc)
            print(f"Application failed to start. Crash log: {path}")
        except Exception:
            print("Application failed to start and crash log creation failed.")
            print("".join(traceback.format_exception(type(exc), exc, exc.__traceback__)))
        raise