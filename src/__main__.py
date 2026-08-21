"""Allow running StudioPulse AI as: python -m src"""
from src.demo import run_demo
import asyncio

if __name__ == "__main__":
    try:
        asyncio.run(run_demo())
    except KeyboardInterrupt:
        print("\n\n  🎬 Demo ended. That's a wrap!\n")
