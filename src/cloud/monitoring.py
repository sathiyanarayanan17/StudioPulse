"""StudioPulse AI - Google Cloud Monitoring Integration"""

from google.cloud import monitoring_v3
from google.protobuf import timestamp_pb2
from typing import Any
import time
from src.utils.config import load_config
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class CloudMonitoringClient:
    """Client for Google Cloud Monitoring (Stackdriver)."""

    def __init__(self):
        config = load_config()
        self.project_id = config.google_cloud.project_id
        self.project_name = f"projects/{self.project_id}"
        self.client = monitoring_v3.MetricServiceClient()
        self.alert_client = monitoring_v3.AlertPolicyServiceClient()

    def get_metric(
        self,
        metric_type: str,
        minutes_ago: int = 10,
        aggregation_minutes: int = 1,
    ) -> list[dict[str, Any]]:
        """Fetch a metric from Cloud Monitoring.

        Args:
            metric_type: Full metric type path
            minutes_ago: How far back to query
            aggregation_minutes: Aggregation window

        Returns:
            List of time series data points
        """
        now = time.time()
        interval = monitoring_v3.TimeInterval(
            end_time=timestamp_pb2.Timestamp(seconds=int(now)),
            start_time=timestamp_pb2.Timestamp(seconds=int(now - minutes_ago * 60)),
        )

        aggregation = monitoring_v3.Aggregation(
            alignment_period={"seconds": aggregation_minutes * 60},
            per_series_aligner=monitoring_v3.Aggregation.Aligner.ALIGN_MEAN,
        )

        results = self.client.list_time_series(
            request={
                "name": self.project_name,
                "filter": f'metric.type = "{metric_type}"',
                "interval": interval,
                "aggregation": aggregation,
                "view": monitoring_v3.ListTimeSeriesRequest.TimeSeriesView.FULL,
            }
        )

        data_points = []
        for series in results:
            for point in series.points:
                data_points.append({
                    "labels": dict(series.metric.labels),
                    "resource": dict(series.resource.labels),
                    "value": point.value.double_value or point.value.int64_value,
                    "timestamp": point.interval.end_time.timestamp(),
                })

        logger.info("Fetched Cloud Monitoring metric", metric=metric_type, points=len(data_points))
        return data_points

    def get_gke_metrics(self, cluster_name: str) -> dict[str, Any]:
        """Get key GKE cluster metrics for the rendering pipeline.

        Args:
            cluster_name: Name of the GKE cluster

        Returns:
            Dictionary of cluster health metrics
        """
        metrics = {}

        metric_types = {
            "cpu_utilization": "kubernetes.io/container/cpu/core_usage_time",
            "memory_utilization": "kubernetes.io/container/memory/used_bytes",
            "gpu_utilization": "kubernetes.io/container/accelerator/duty_cycle",
            "pod_restart_count": "kubernetes.io/container/restart_count",
        }

        for name, metric_type in metric_types.items():
            try:
                metrics[name] = self.get_metric(metric_type, minutes_ago=5)
            except Exception as e:
                logger.warning(f"Failed to fetch {name}", error=str(e))
                metrics[name] = []

        return metrics

    def write_custom_metric(
        self,
        metric_type: str,
        value: float,
        labels: dict[str, str] | None = None,
    ) -> None:
        """Write a custom metric for StudioPulse tracking.

        Args:
            metric_type: Custom metric type (e.g., custom.googleapis.com/studiopulse/incidents_resolved)
            value: Metric value
            labels: Optional metric labels
        """
        series = monitoring_v3.TimeSeries()
        series.metric.type = metric_type
        if labels:
            for key, val in labels.items():
                series.metric.labels[key] = val

        series.resource.type = "global"
        series.resource.labels["project_id"] = self.project_id

        now = time.time()
        point = monitoring_v3.Point(
            interval=monitoring_v3.TimeInterval(
                end_time=timestamp_pb2.Timestamp(seconds=int(now))
            ),
            value=monitoring_v3.TypedValue(double_value=value),
        )
        series.points = [point]

        self.client.create_time_series(
            request={"name": self.project_name, "time_series": [series]}
        )
        logger.info("Wrote custom metric", metric=metric_type, value=value)
