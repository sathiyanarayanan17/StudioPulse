"""StudioPulse AI - Agent Orchestrator

The orchestrator coordinates the Monitor, Diagnose, and Remediate agents
into a cohesive autonomous pipeline.
"""

import asyncio
from typing import Any
from src.agents.monitor import MonitorAgent
from src.agents.diagnose import DiagnoseAgent
from src.agents.remediate import RemediateAgent
from src.grafana.alerts import ProcessedAlert
from src.grafana.client import GrafanaClient
from src.grafana.dashboards import DashboardQuerier
from src.cloud.vertex_ai import GeminiAgent
from src.cloud.compute import ComputeOperations
from src.cloud.monitoring import CloudMonitoringClient
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class Orchestrator:
    """Main orchestrator that coordinates all agents in the StudioPulse pipeline.

    Flow:
    1. Monitor Agent detects a firing alert
    2. Diagnose Agent analyzes and finds root cause
    3. Remediate Agent plans and executes the fix
    4. Results are logged and annotated in Grafana
    """

    def __init__(self):
        # Initialize shared clients
        self.grafana_client = GrafanaClient()
        self.gemini_agent = GeminiAgent()
        self.compute_ops = ComputeOperations()
        self.cloud_monitoring = CloudMonitoringClient()
        self.dashboard_querier = DashboardQuerier(self.grafana_client)

        # Initialize agents
        self.monitor_agent = MonitorAgent(
            grafana_client=self.grafana_client,
            on_alert=self._handle_alert,
        )
        self.diagnose_agent = DiagnoseAgent(
            dashboard_querier=self.dashboard_querier,
            gemini_agent=self.gemini_agent,
            cloud_monitoring=self.cloud_monitoring,
        )
        self.remediate_agent = RemediateAgent(
            gemini_agent=self.gemini_agent,
            compute_ops=self.compute_ops,
            grafana_client=self.grafana_client,
            dashboard_querier=self.dashboard_querier,
        )

        # Track active incidents
        self._active_incidents: dict[str, Any] = {}
        self._incident_history: list[dict[str, Any]] = []

    async def start(self):
        """Start the orchestrator and all agents."""
        logger.info("=" * 60)
        logger.info("🎬 StudioPulse AI - Starting Autonomous Pipeline")
        logger.info("=" * 60)
        logger.info(
            "Agents initialized",
            monitor="ready",
            diagnose="ready",
            remediate="ready",
        )

        try:
            await self.monitor_agent.start()
        except KeyboardInterrupt:
            await self.shutdown()
        except Exception as e:
            logger.error("Orchestrator error", error=str(e))
            await self.shutdown()

    async def shutdown(self):
        """Gracefully shut down all agents."""
        logger.info("Shutting down StudioPulse AI...")
        await self.monitor_agent.stop()
        await self.grafana_client.close()
        logger.info("Shutdown complete")

    async def _handle_alert(self, alert: ProcessedAlert):
        """Handle a new alert detected by the Monitor Agent.

        This is the main pipeline: detect → diagnose → remediate.

        Args:
            alert: The detected alert
        """
        logger.info(
            "🚨 Pipeline triggered",
            alert_id=alert.alert_id,
            title=alert.title,
            severity=alert.severity.value,
        )

        # Track as active incident
        self._active_incidents[alert.alert_id] = {
            "alert": alert,
            "status": "diagnosing",
        }

        try:
            # Phase 1: Diagnose
            logger.info("📋 Phase 1: Diagnosing...")
            diagnosis_result = await self.diagnose_agent.diagnose(alert)

            self._active_incidents[alert.alert_id]["status"] = "remediating"
            self._active_incidents[alert.alert_id]["diagnosis"] = diagnosis_result

            # Phase 2: Remediate
            logger.info("🔧 Phase 2: Remediating...")
            remediation_result = await self.remediate_agent.remediate(diagnosis_result)

            # Phase 3: Record outcome
            self._active_incidents[alert.alert_id]["status"] = remediation_result["status"]
            self._active_incidents[alert.alert_id]["result"] = remediation_result

            # Move to history
            self._incident_history.append(self._active_incidents.pop(alert.alert_id))

            status_emoji = "✅" if remediation_result["status"] == "resolved" else "⚠️"
            logger.info(
                f"{status_emoji} Pipeline complete",
                alert_id=alert.alert_id,
                status=remediation_result["status"],
                verification=remediation_result.get("verification", {}).get("summary"),
            )

        except Exception as e:
            logger.error(
                "Pipeline failed",
                alert_id=alert.alert_id,
                error=str(e),
            )
            self._active_incidents[alert.alert_id]["status"] = "error"
            self._active_incidents[alert.alert_id]["error"] = str(e)

    def get_status(self) -> dict[str, Any]:
        """Get current orchestrator status."""
        return {
            "active_incidents": len(self._active_incidents),
            "total_resolved": len([
                i for i in self._incident_history
                if i.get("status") == "resolved"
            ]),
            "total_incidents": len(self._incident_history),
            "incidents": self._active_incidents,
        }
