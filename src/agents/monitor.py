"""StudioPulse AI - Monitor Agent

This agent continuously watches Grafana for firing alerts
and feeds them into the diagnosis pipeline.
"""

from __future__ import annotations

import asyncio
from typing import Callable, Awaitable, Any
from src.grafana.alerts import AlertProcessor, ProcessedAlert
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class MonitorAgent:
    """Agent responsible for detecting anomalies and alerts from Grafana.

    Continuously polls Grafana for firing alerts and passes them
    to the orchestrator for diagnosis and remediation.
    """

    def __init__(
        self,
        grafana_client: Any,
        on_alert: Callable[[ProcessedAlert], Awaitable[None]],
        polling_interval: int = 10,
    ):
        """Initialize the Monitor Agent.

        Args:
            grafana_client: Grafana API client (real or simulated)
            on_alert: Callback when a new alert is detected
            polling_interval: Seconds between alert checks
        """
        self.alert_processor = AlertProcessor(grafana_client)
        self.on_alert = on_alert
        self.polling_interval = polling_interval
        self._running = False
        self._seen_alerts: set[str] = set()

    async def start(self):
        """Start the monitoring loop."""
        self._running = True
        logger.info(
            "👁️ Monitor Agent started",
            polling_interval=self.polling_interval,
        )

        while self._running:
            try:
                await self._check_alerts()
            except Exception as e:
                logger.error("Error in monitoring loop", error=str(e))

            await asyncio.sleep(self.polling_interval)

    async def stop(self):
        """Stop the monitoring loop."""
        self._running = False
        logger.info("Monitor Agent stopped")

    async def _check_alerts(self):
        """Check for new firing alerts."""
        alerts = await self.alert_processor.fetch_and_process_alerts()

        for alert in alerts:
            if alert.alert_id not in self._seen_alerts:
                self._seen_alerts.add(alert.alert_id)
                logger.info(
                    "🚨 New alert detected",
                    alert_id=alert.alert_id,
                    title=alert.title,
                    severity=alert.severity.value,
                    category=alert.category.value,
                )
                await self.on_alert(alert)

        # Clean up resolved alerts from seen set
        current_ids = {a.alert_id for a in alerts}
        resolved = self._seen_alerts - current_ids
        if resolved:
            logger.info("Alerts resolved", count=len(resolved))
            self._seen_alerts -= resolved
