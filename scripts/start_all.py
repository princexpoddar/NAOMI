"""
NAOMI Full-Stack Application Launcher.

Launches both:
1. FastAPI Backend (port 8080): Demand forecasting, profit optimization, counterfactual simulations.
2. Vite React Frontend (port 5180): Pitch Black & Crimson C-suite Decision Companion UI.

Usage:
    python scripts/start_all.py
"""

import os
import signal
import subprocess
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
FRONTEND_DIR = PROJECT_ROOT / "frontend"


def main():
    print("=" * 80)
    print("⚡ NAOMI: LAUNCHING PITCH BLACK & CRIMSON FULL-STACK DECISION COMPANION")
    print("=" * 80)

    # 1. Start FastAPI Backend
    print("[1/2] Starting FastAPI Backend on http://127.0.0.1:8080 ...")
    backend_cmd = [
        sys.executable,
        "-m",
        "uvicorn",
        "src.api.main:app",
        "--host",
        "127.0.0.1",
        "--port",
        "8080",
    ]
    backend_process = subprocess.Popen(
        backend_cmd,
        cwd=str(PROJECT_ROOT),
    )

    time.sleep(2)

    # 2. Start Vite React Frontend
    print("[2/2] Starting React Executive Frontend on http://localhost:5180 ...")
    npm_cmd = "npm.cmd" if os.name == "nt" else "npm"
    frontend_cmd = [npm_cmd, "run", "dev"]
    frontend_process = subprocess.Popen(
        frontend_cmd,
        cwd=str(FRONTEND_DIR),
    )

    print("\n" + "=" * 80)
    print("🚀 NAOMI IS RUNNING LIVE:")
    print("   👉 Executive Frontend: http://localhost:5180")
    print("   👉 REST API & Docs:    http://127.0.0.1:8080/docs")
    print("   👉 Health Check:       http://127.0.0.1:8080/health")
    print("=" * 80)
    print("Press CTRL+C to stop both servers...\n")

    def handle_exit(signum, frame):
        print("\nShutting down NAOMI full-stack servers...")
        try:
            frontend_process.terminate()
        except Exception:
            pass
        try:
            backend_process.terminate()
        except Exception:
            pass
        sys.exit(0)

    signal.signal(signal.SIGINT, handle_exit)
    signal.signal(signal.SIGTERM, handle_exit)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        handle_exit(None, None)


if __name__ == "__main__":
    main()
