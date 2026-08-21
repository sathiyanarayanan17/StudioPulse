"""StudioPulse AI - Configuration Loader"""

import os
from pathlib import Path
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class GoogleCloudConfig:
    project_id: str
    region: str
    vertex_ai_location: str


@dataclass
class GrafanaConfig:
    url: str
    api_key: str
    org_id: int


@dataclass
class AgentConfig:
    polling_interval: int
    max_retries: int
    log_level: str
    gemini_model: str


@dataclass
class AppConfig:
    google_cloud: GoogleCloudConfig
    grafana: GrafanaConfig
    agent: AgentConfig


def load_config() -> AppConfig:
    """Load configuration from environment variables."""
    return AppConfig(
        google_cloud=GoogleCloudConfig(
            project_id=os.getenv("GOOGLE_CLOUD_PROJECT", ""),
            region=os.getenv("GOOGLE_CLOUD_REGION", "us-central1"),
            vertex_ai_location=os.getenv("VERTEX_AI_LOCATION", "us-central1"),
        ),
        grafana=GrafanaConfig(
            url=os.getenv("GRAFANA_URL", ""),
            api_key=os.getenv("GRAFANA_API_KEY", ""),
            org_id=int(os.getenv("GRAFANA_ORG_ID", "1")),
        ),
        agent=AgentConfig(
            polling_interval=int(os.getenv("AGENT_POLLING_INTERVAL", "30")),
            max_retries=int(os.getenv("AGENT_MAX_RETRIES", "3")),
            log_level=os.getenv("AGENT_LOG_LEVEL", "INFO"),
            gemini_model=os.getenv("GEMINI_MODEL", "gemini-2.0-flash"),
        ),
    )
