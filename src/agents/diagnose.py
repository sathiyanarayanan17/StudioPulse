"""StudioPulse AI - Diagnose Agent

This agent takes alerts from the monitor, gathers correlated metrics,
and uses Gemini to perform root cause analysis.
"""

from __future__ import annotations

from typing import Any
from src.grafana.alerts import ProcessedAlert
from src.grafana.dashboards import DashboardQuerier
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class DiagnoseAgent:
    """Agent responsible for root cause analysis of pipeline incidents.

    Correlates metrics from Grafana and Cloud Monitoring, then uses
    Gemini to diagnose the most likely root cause.
    """

    def __init__(
        self,
        dashboard_querier: DashboardQuerier,
        gemini_agent: Any,
        cloud_monitoring: Any,
    ):
        self.dashboard_querier = dashboard_querier
        self.gemini = gemini_agent
        self.cloud_monitoring = cloud_monitoring

    async def diagnose(self, alert: ProcessedAlert) -> dict[str, Any]:
        """Perform full diagnosis of an alert.

        Steps:
        1. Gather correlated metrics from Grafana
        2. Fetch additional context from Cloud Monitoring
        3. Use Gemini to analyze and diagnose

        Args:
            alert: Processed alert from the monitor agent

        Returns:
            Diagnosis result with root cause and recommendations
        """
        logger.info(
            "Starting diagnosis",
            alert_id=alert.alert_id,
            category=alert.category.value,
        )

        # Step 1: Get correlated metrics from Grafana
        correlated_metrics = await self.dashboard_querier.get_correlated_metrics(
            category=alert.category.value
        )

        # Step 2: Get GKE cluster metrics from Cloud Monitoring
        cloud_metrics = self.cloud_monitoring.get_gke_metrics(
            cluster_name="render-cluster"
        )

        # Step 3: Build context for Gemini analysis
        analysis_context = {
            "title": alert.title,
            "severity": alert.severity.value,
            "category": alert.category.value,
            "labels": alert.labels,
            "annotations": alert.annotations,
            "metrics": {
                "grafana_correlated": correlated_metrics,
                "cloud_monitoring": self._summarize_cloud_metrics(cloud_metrics),
            },
        }

        # Step 4: Use Gemini for root cause analysis
        diagnosis = await self.gemini.analyze_alert(analysis_context)

        logger.info(
            "Diagnosis complete",
            alert_id=alert.alert_id,
            root_cause=diagnosis.get("diagnosis", {}).get("root_cause", "unknown"),
            confidence=diagnosis.get("diagnosis", {}).get("confidence", 0),
        )

        return {
            "alert": alert,
            "diagnosis": diagnosis,
            "metrics_snapshot": correlated_metrics,
        }

    def _summarize_cloud_metrics(self, metrics: dict[str, Any]) -> dict[str, Any]:
        """Summarize Cloud Monitoring metrics for Gemini context."""
        summary = {}
        for metric_name, data_points in metrics.items():
            if data_points:
                values = [dp.get("value", 0) for dp in data_points if isinstance(dp, dict)]
                if values:
                    summary[metric_name] = {
                        "latest": values[-1] if values else None,
                        "avg": sum(values) / len(values) if values else None,
                        "max": max(values) if values else None,
                        "data_points": len(values),
                    }
        return summary
