"""StudioPulse AI - Main Entry Point

Autonomous AI agent that monitors, diagnoses, and self-heals
media rendering pipelines using Gemini and Grafana in real-time.
"""

import asyncio
import sys
from src.agents.orchestrator import Orchestrator
from src.utils.config import load_config
from src.utils.logger import setup_logger

logger = setup_logger("studiopulse")


def print_banner():
    """Print the StudioPulse AI startup banner."""
    banner = """
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║   🎬  S T U D I O P U L S E   A I                      ║
║                                                          ║
║   Autonomous Media Pipeline Self-Healing Agent           ║
║   Powered by Google Gemini + Grafana Labs                ║
║                                                          ║
║   Monitor → Diagnose → Remediate → Verify                ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
"""
    print(banner)


async def main():
    """Main application entry point."""
    print_banner()

    # Validate configuration
    config = load_config()

    if not config.google_cloud.project_id:
        logger.error("GOOGLE_CLOUD_PROJECT is not set. Please configure .env")
        sys.exit(1)

    if not config.grafana.url or not config.grafana.api_key:
        logger.error("Grafana credentials are not set. Please configure .env")
        sys.exit(1)

    logger.info(
        "Configuration loaded",
        project=config.google_cloud.project_id,
        region=config.google_cloud.region,
        grafana_url=config.grafana.url,
        model=config.agent.gemini_model,
        polling_interval=config.agent.polling_interval,
    )

    # Start the orchestrator
    orchestrator = Orchestrator()
    await orchestrator.start()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🎬 StudioPulse AI shutting down... Cut! That's a wrap!")
