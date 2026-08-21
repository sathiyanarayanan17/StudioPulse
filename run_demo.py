"""
StudioPulse AI - Quick Start Demo

Just run: python run_demo.py
Dashboard: http://localhost:8080
"""
import asyncio
import os
import sys

# Ensure UTF-8 output on Windows
if sys.platform == "win32":
    os.environ["PYTHONIOENCODING"] = "utf-8"
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, OSError):
        pass

from src.demo import run_demo

if __name__ == "__main__":
    try:
        asyncio.run(run_demo())
    except KeyboardInterrupt:
        print("\n\n  🎬 Demo ended. That's a wrap!\n")
