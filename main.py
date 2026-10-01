from pathlib import Path

from app.server import run_server


PROJECT_ROOT = Path(__file__).resolve().parent


if __name__ == "__main__":
    run_server(
        static_directory=PROJECT_ROOT / "static",
        data_file=PROJECT_ROOT / "data" / "timeline.json",
    )
