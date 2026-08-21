"""StudioPulse AI - Simulated Grafana Client

Drop-in replacement for the real Grafana client that uses
the PipelineSimulator for demo purposes.
"""

from typing import Any
from src.simulator import PipelineSimulator
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class SimulatedGrafanaClient:
    """Simulated Grafana API client backed by the pipeline simulator.

    This allows the full agent pipeline to run in demo mode
    without needing real Grafana credentials.
    """

    def __init__(self, simulator: PipelineSimulator):
        self.simulator = simulator
        self._annotations: list[dict[str, Any]] = []

    async def get_alerts(self, state: str = "firing") -> list[dict[str, Any]]:
        """Get simulated alerts."""
        alerts = self.simulator.get_alerts_as_grafana_format()
        if state:
            alerts = [a for a in alerts if a.get("state") == state]
        return alerts

    async def query_datasource(
        self,
        datasource_uid: str,
        query: str,
        from_time: str = "now-1h",
        to_time: str = "now",
    ) -> dict[str, Any]:
        """Return simulated metric data."""
        metrics = self.simulator.get_current_metrics()

        # Map PromQL-like queries to simulated data
        metric_value = None
        if "gpu_utilization" in query or "gpu" in query.lower():
            metric_value = metrics["gpu_utilization"]
        elif "memory" in query.lower():
            metric_value = metrics["memory_utilization"]
        elif "queue" in query.lower():
            metric_value = float(metrics["render_queue_depth"])
        elif "disk" in query.lower():
            metric_value = metrics["disk_usage_percent"]
        elif "network" in query.lower():
            metric_value = metrics["network_throughput_mbps"]
        elif "fail" in query.lower():
            metric_value = metrics["failed_renders_per_min"]
        else:
            metric_value = 50.0

        return {
            "results": {
                "A": {
                    "frames": [
                        {
                            "data": {
                                "values": [
                                    [1692000000],  # timestamp
                                    [metric_value],  # value
                                ]
                            }
                        }
                    ]
                }
            }
        }

    async def get_dashboard(self, uid: str) -> dict[str, Any]:
        """Return a simulated dashboard."""
        return {
            "dashboard": {
                "uid": uid,
                "title": "Render Pipeline Overview",
                "panels": [
                    {"title": "GPU Utilization", "type": "graph"},
                    {"title": "Render Queue", "type": "stat"},
                    {"title": "Job Status", "type": "table"},
                ],
            }
        }

    async def get_annotations(
        self,
        from_time: int,
        to_time: int,
        dashboard_id: int | None = None,
    ) -> list[dict[str, Any]]:
        """Get simulated annotations."""
        return self._annotations

    async def create_annotation(
        self,
        text: str,
        tags: list[str] | None = None,
        dashboard_id: int | None = None,
    ) -> dict[str, Any]:
        """Create a simulated annotation."""
        annotation = {
            "id": len(self._annotations) + 1,
            "text": text,
            "tags": tags or [],
            "dashboardId": dashboard_id,
        }
        self._annotations.append(annotation)
        logger.info("📝 Annotation created", text=text[:80])
        return annotation

    async def close(self):
        """No-op for simulated client."""
        pass
