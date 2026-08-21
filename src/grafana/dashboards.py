"""StudioPulse AI - Grafana Dashboard Queries"""

from typing import Any
from src.grafana.client import GrafanaClient
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


# Pre-defined PromQL queries for media rendering pipeline metrics
RENDER_PIPELINE_QUERIES = {
    "gpu_utilization": 'avg(nvidia_gpu_utilization{job="render-nodes"}) by (instance)',
    "gpu_memory": 'avg(nvidia_gpu_memory_used_bytes{job="render-nodes"}) / avg(nvidia_gpu_memory_total_bytes{job="render-nodes"}) * 100',
    "render_queue_depth": 'sum(render_queue_pending_jobs{pipeline="main"})',
    "render_job_duration": 'histogram_quantile(0.95, rate(render_job_duration_seconds_bucket[5m]))',
    "node_memory_usage": 'avg(container_memory_usage_bytes{namespace="render"}) by (pod) / avg(container_spec_memory_limit_bytes{namespace="render"}) by (pod) * 100',
    "failed_renders": 'sum(rate(render_job_failures_total[5m])) by (reason)',
    "disk_usage": 'max(node_filesystem_avail_bytes{mountpoint="/data"}) / max(node_filesystem_size_bytes{mountpoint="/data"}) * 100',
    "network_throughput": 'sum(rate(node_network_transmit_bytes_total{device="eth0"}[5m])) by (instance)',
}


class DashboardQuerier:
    """Queries Grafana dashboards for rendering pipeline metrics."""

    def __init__(self, grafana_client: GrafanaClient, datasource_uid: str = "prometheus"):
        self.grafana = grafana_client
        self.datasource_uid = datasource_uid

    async def get_pipeline_health(self) -> dict[str, Any]:
        """Get overall rendering pipeline health metrics.

        Returns:
            Dictionary with metric names and their current values
        """
        logger.info("Fetching pipeline health metrics")
        health_data = {}

        for metric_name, query in RENDER_PIPELINE_QUERIES.items():
            try:
                result = await self.grafana.query_datasource(
                    datasource_uid=self.datasource_uid,
                    query=query,
                    from_time="now-5m",
                    to_time="now",
                )
                health_data[metric_name] = self._extract_value(result)
            except Exception as e:
                logger.warning(
                    "Failed to query metric",
                    metric=metric_name,
                    error=str(e),
                )
                health_data[metric_name] = None

        return health_data

    async def get_correlated_metrics(
        self,
        category: str,
        time_range: str = "now-15m",
    ) -> dict[str, Any]:
        """Get metrics correlated to a specific alert category.

        Args:
            category: Alert category (gpu_saturation, memory_leak, etc.)
            time_range: How far back to look

        Returns:
            Correlated metrics data
        """
        correlation_map = {
            "gpu_saturation": ["gpu_utilization", "gpu_memory", "render_job_duration"],
            "memory_leak": ["node_memory_usage", "render_job_duration", "failed_renders"],
            "queue_backlog": ["render_queue_depth", "gpu_utilization", "render_job_duration"],
            "disk_full": ["disk_usage", "render_queue_depth", "failed_renders"],
            "render_failure": ["failed_renders", "gpu_memory", "node_memory_usage"],
            "node_down": ["gpu_utilization", "node_memory_usage", "network_throughput"],
        }

        queries_to_run = correlation_map.get(category, list(RENDER_PIPELINE_QUERIES.keys()))
        results = {}

        for metric_name in queries_to_run:
            query = RENDER_PIPELINE_QUERIES.get(metric_name)
            if not query:
                continue
            try:
                result = await self.grafana.query_datasource(
                    datasource_uid=self.datasource_uid,
                    query=query,
                    from_time=time_range,
                    to_time="now",
                )
                results[metric_name] = self._extract_value(result)
            except Exception as e:
                logger.warning("Metric query failed", metric=metric_name, error=str(e))

        return results

    def _extract_value(self, query_result: dict[str, Any]) -> Any:
        """Extract the metric value from a Grafana query response."""
        try:
            frames = query_result.get("results", {}).get("A", {}).get("frames", [])
            if frames:
                values = frames[0].get("data", {}).get("values", [])
                if len(values) >= 2 and values[1]:
                    return values[1][-1]  # Latest value
        except (KeyError, IndexError):
            pass
        return None
