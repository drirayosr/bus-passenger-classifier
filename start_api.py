"""
Start FastAPI Server
Quick script to start the API locally
"""

import warnings

warnings.filterwarnings("ignore")

import subprocess
import sys


def main():
    print("=" * 60)
    print("Starting Bus Passenger Classification API")
    print("=" * 60)
    print("\n[INFO] Starting uvicorn server...")
    print("[INFO] API will be available at: http://localhost:8000")
    print("[INFO] Interactive docs at: http://localhost:8000/docs")
    print("[INFO] Press Ctrl+C to stop\n")
    print("=" * 60)

    try:
        subprocess.run(
            [
                sys.executable,
                "-m",
                "uvicorn",
                "api.app:app",
                "--host",
                "0.0.0.0",
                "--port",
                "8000",
                "--reload",
            ]
        )
    except KeyboardInterrupt:
        print("\n\n[INFO] Shutting down...")
        print("[OK] API stopped")


if __name__ == "__main__":
    main()
