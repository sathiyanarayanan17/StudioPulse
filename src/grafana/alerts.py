"""StudioPulse AI - Grafana Alert Processing"""

from dataclasses import dataclass
from enum import Enum
from typing import Any
from src.grafana.client import GrafanaClient
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class AlertSeverity(str, Enum):
    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"


class AlertCategory(str, Enum):
    GPU_SATURATION = "gpu_saturation"
    MEMORY_LEAK = "memory_leak"
    QUEUE_BACKLOG = "queue_backlog"
    DISK_FULL = "disk_full"
    NODE_DOWN = "node_down"
    RENDER_FAILURE = "render_failure"
    NETWORK_ISSUE = "network_issue"
    UNKNOWN = "unknown"


@dataclass
class ProcessedAlert:
    """Structured alert after processing from Grafana."""
    alert_id: str
    title: str
    severity: AlertSeverity
    category: AlertCategory
    labels: dict[str, str]
    annotations: dict[str, str]
    value: float | None
    source_dashboard: str | None
    raw_data: dict[str, Any]


class AlertProcessor:
    """Processes and categorizes Grafana alerts for the agent pipeline."""

    # Mapping of alert label patterns to categories
    CATEGORY_PATTERNS = {
        "gpu": AlertCategory.GPU_SATURATION,
        "memory": AlertCategory.MEMORY_LEAK,
        "queue": AlertCategory.QUEUE_BACKLOG,
        "disk": AlertCategory.DISK_FULL,
        "node": AlertCategory.NODE_DOWN,
        "render": AlertCategory.RENDER_FAILURE,
        "network": AlertCategory.NETWORK_ISSUE,
    }

    def __init__(self, grafana_client: GrafanaClient):
        self.grafana = grafana_client

    async def fetch_and_process_alerts(self) -> list[ProcessedAlert]:
        """Fetch firing alerts from Grafana and process them.

        Returns:
            List of processed, categorized alerts
        """
        raw_alerts = await self.grafana.get_alerts(state="firing")
        processed = []

        for alert in raw_alerts:
            processed_alert = self._process_alert(alert)
            processed.append(processed_alert)
            logger.info(
                "Processed alert",
                alert_id=processed_alert.alert_id,
                category=processed_alert.category.value,
                severity=processed_alert.severity.value,
            )

        # Sort by severity (critical first)
        severity_order = {
            AlertSeverity.CRITICAL: 0,
            AlertSeverity.WARNING: 1,
            AlertSeverity.INFO: 2,
        }
        processed.sort(key=lambda a: severity_order.get(a.severity, 99))

        return processed

    def _process_alert(self, raw_alert: dict[str, Any]) -> ProcessedAlert:
        """Process a single raw alert into structured format."""
        labels = raw_alert.get("labels", {})
        annotations = raw_alert.get("annotations", {})

        return ProcessedAlert(
            alert_id=raw_alert.get("uid", "unknown"),
            title=raw_alert.get("title", "Untitled Alert"),
            severity=self._determine_severity(labels),
            category=self._categorize_alert(raw_alert),
            labels=labels,
            annotations=annotations,
            value=raw_alert.get("value"),
            source_dashboard=labels.get("dashboard_uid"),
            raw_data=raw_alert,
        )

    def _determine_severity(self, labels: dict[str, str]) -> AlertSeverity:
        """Determine alert severity from labels."""
        severity_str = labels.get("severity", "warning").lower()
        try:
            return AlertSeverity(severity_str)
        except ValueError:
            return AlertSeverity.WARNING

    def _categorize_alert(self, alert: dict[str, Any]) -> AlertCategory:
        """Categorize alert based on title, labels, and annotations."""
        searchable_text = " ".join([
            alert.get("title", ""),
            str(alert.get("labels", {})),
            str(alert.get("annotations", {})),
        ]).lower()

        for pattern, category in self.CATEGORY_PATTERNS.items():
            if pattern in searchable_text:
                return category

        return AlertCategory.UNKNOWN
