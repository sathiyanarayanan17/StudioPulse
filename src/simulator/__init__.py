"""StudioPulse AI - Demo Simulator

Simulates a media rendering pipeline with realistic incidents
so the agent can be demonstrated without real infrastructure.
"""

import asyncio
import random
import time
from typing import Any
from dataclasses import dataclass, field
from enum import Enum
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class PipelineState(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    CRITICAL = "critical"
    RECOVERING = "recovering"


@dataclass
class RenderJob:
    job_id: str
    name: str
    frames_total: int
    frames_completed: int = 0
    status: str = "queued"
    gpu_memory_mb: int = 4096
    resolution: str = "4K"
    started_at: float = 0.0


@dataclass
class SimulatedMetrics:
    """Current state of the simulated pipeline."""
    gpu_utilization: float = 45.0
    gpu_memory_percent: float = 40.0
    cpu_utilization: float = 30.0
    memory_utilization: float = 50.0
    disk_usage_percent: float = 55.0
    render_queue_depth: int = 5
    active_render_jobs: int = 3
    failed_renders_per_min: float = 0.0
    avg_frame_time_seconds: float = 12.0
    network_throughput_mbps: float = 450.0
    node_count: int = 3
    healthy_nodes: int = 3
    pipeline_state: PipelineState = PipelineState.HEALTHY


@dataclass
class SimulatedAlert:
    """A simulated Grafana alert."""
    uid: str
    title: str
    state: str = "firing"
    severity: str = "critical"
    labels: dict = field(default_factory=dict)
    annotations: dict = field(default_factory=dict)
    value: float = 0.0


class PipelineSimulator:
    """Simulates a VFX/Media rendering pipeline with realistic failure scenarios.

    Generates metrics, alerts, and responds to remediation actions
    to demonstrate StudioPulse AI's capabilities.
    """

    SCENARIOS = [
        {
            "name": "gpu_saturation",
            "title": "GPU Utilization Critical - Render Nodes Saturated",
            "description": "Multiple 8K render jobs overwhelming GPU pool",
            "metrics_override": {
                "gpu_utilization": 97.5,
                "gpu_memory_percent": 92.0,
                "avg_frame_time_seconds": 85.0,
                "render_queue_depth": 45,
                "active_render_jobs": 12,
            },
        },
        {
            "name": "memory_leak",
            "title": "Memory Leak Detected - Render Worker Pods",
            "description": "render-worker pods consuming increasing memory over time",
            "metrics_override": {
                "memory_utilization": 94.0,
                "gpu_memory_percent": 88.0,
                "failed_renders_per_min": 3.2,
                "avg_frame_time_seconds": 45.0,
            },
        },
        {
            "name": "queue_backlog",
            "title": "Render Queue Backlog - 200+ Jobs Pending",
            "description": "Queue growing faster than processing capacity",
            "metrics_override": {
                "render_queue_depth": 215,
                "gpu_utilization": 99.0,
                "active_render_jobs": 8,
                "avg_frame_time_seconds": 120.0,
            },
        },
        {
            "name": "disk_full",
            "title": "Disk Space Critical - Render Output Volume",
            "description": "Output volume /data/renders at 95% capacity",
            "metrics_override": {
                "disk_usage_percent": 95.5,
                "failed_renders_per_min": 5.0,
                "render_queue_depth": 30,
            },
        },
        {
            "name": "node_failure",
            "title": "GPU Node Unresponsive - render-node-gpu-3",
            "description": "Node failed health check, pods being evicted",
            "metrics_override": {
                "healthy_nodes": 2,
                "gpu_utilization": 85.0,
                "render_queue_depth": 35,
                "failed_renders_per_min": 2.0,
            },
        },
    ]

    def __init__(self):
        self.metrics = SimulatedMetrics()
        self.active_alerts: list[SimulatedAlert] = []
        self.incident_history: list[dict[str, Any]] = []
        self._running = False
        self._current_scenario: dict | None = None
        self._render_jobs: list[RenderJob] = self._create_initial_jobs()

    def _create_initial_jobs(self) -> list[RenderJob]:
        """Create initial render jobs for the simulation."""
        jobs = [
            RenderJob("job-001", "EPIC_BATTLE_SEQ_042", 2400, 1850, "rendering", 8192, "8K"),
            RenderJob("job-002", "SUNSET_SCENE_015", 600, 600, "completed", 4096, "4K"),
            RenderJob("job-003", "VFX_EXPLOSION_007", 1200, 340, "rendering", 12288, "8K"),
            RenderJob("job-004", "UNDERWATER_SEQ_023", 900, 0, "queued", 6144, "4K"),
            RenderJob("job-005", "SPACESHIP_LANDING_001", 3600, 120, "rendering", 16384, "8K"),
        ]
        return jobs

    async def start(self):
        """Start the simulation loop."""
        self._running = True
        logger.info("🎬 Pipeline Simulator started")
        while self._running:
            await self._tick()
            await asyncio.sleep(2)

    async def stop(self):
        """Stop the simulation."""
        self._running = False

    async def trigger_scenario(self, scenario_name: str | None = None) -> SimulatedAlert:
        """Trigger a failure scenario.

        Args:
            scenario_name: Specific scenario, or None for random

        Returns:
            The generated alert
        """
        if scenario_name:
            scenario = next(
                (s for s in self.SCENARIOS if s["name"] == scenario_name),
                random.choice(self.SCENARIOS),
            )
        else:
            scenario = random.choice(self.SCENARIOS)

        self._current_scenario = scenario

        # Apply metrics override
        for key, value in scenario["metrics_override"].items():
            setattr(self.metrics, key, value)

        self.metrics.pipeline_state = PipelineState.CRITICAL

        # Create alert
        alert = SimulatedAlert(
            uid=f"alert-{int(time.time())}",
            title=scenario["title"],
            state="firing",
            severity="critical",
            labels={
                "alertname": scenario["name"],
                "severity": "critical",
                "namespace": "render",
                "cluster": "render-cluster",
            },
            annotations={
                "description": scenario["description"],
                "runbook_url": f"https://wiki.studio.internal/runbook/{scenario['name']}",
            },
            value=list(scenario["metrics_override"].values())[0],
        )
        self.active_alerts.append(alert)

        logger.info(
            "🚨 Scenario triggered",
            scenario=scenario["name"],
            alert_title=alert.title,
        )
        return alert

    def apply_remediation(self, action: str, params: dict[str, Any] = None) -> dict[str, Any]:
        """Apply a remediation action to the simulated pipeline.

        Args:
            action: The remediation action name
            params: Action parameters

        Returns:
            Result of the action
        """
        params = params or {}
        logger.info("Applying remediation", action=action, params=params)

        if action == "scale_node_pool":
            target = params.get("target_size", 5)
            self.metrics.node_count = target
            self.metrics.healthy_nodes = target
            self.metrics.gpu_utilization = max(40, self.metrics.gpu_utilization - 30)
            self.metrics.render_queue_depth = max(5, self.metrics.render_queue_depth - 40)
            self.metrics.avg_frame_time_seconds = max(12, self.metrics.avg_frame_time_seconds - 50)

        elif action == "restart_workload":
            self.metrics.memory_utilization = 50.0
            self.metrics.gpu_memory_percent = 45.0
            self.metrics.failed_renders_per_min = 0.0

        elif action == "resize_disk":
            self.metrics.disk_usage_percent = 45.0

        elif action == "drain_and_replace_node":
            self.metrics.healthy_nodes = self.metrics.node_count
            self.metrics.failed_renders_per_min = max(0, self.metrics.failed_renders_per_min - 2)

        # Transition to recovering
        self.metrics.pipeline_state = PipelineState.RECOVERING

        # Clear alerts after remediation
        self.active_alerts = [a for a in self.active_alerts if a.state != "firing"]

        return {
            "action": action,
            "status": "success",
            "new_metrics": self.get_current_metrics(),
        }

    def get_current_metrics(self) -> dict[str, Any]:
        """Get current simulated metrics as a dictionary."""
        return {
            "gpu_utilization": round(self.metrics.gpu_utilization, 1),
            "gpu_memory_percent": round(self.metrics.gpu_memory_percent, 1),
            "cpu_utilization": round(self.metrics.cpu_utilization, 1),
            "memory_utilization": round(self.metrics.memory_utilization, 1),
            "disk_usage_percent": round(self.metrics.disk_usage_percent, 1),
            "render_queue_depth": self.metrics.render_queue_depth,
            "active_render_jobs": self.metrics.active_render_jobs,
            "failed_renders_per_min": round(self.metrics.failed_renders_per_min, 1),
            "avg_frame_time_seconds": round(self.metrics.avg_frame_time_seconds, 1),
            "network_throughput_mbps": round(self.metrics.network_throughput_mbps, 1),
            "node_count": self.metrics.node_count,
            "healthy_nodes": self.metrics.healthy_nodes,
            "pipeline_state": self.metrics.pipeline_state.value,
        }

    def get_alerts_as_grafana_format(self) -> list[dict[str, Any]]:
        """Return active alerts in Grafana API format."""
        return [
            {
                "uid": alert.uid,
                "title": alert.title,
                "state": alert.state,
                "labels": alert.labels,
                "annotations": alert.annotations,
                "value": alert.value,
            }
            for alert in self.active_alerts
        ]

    def get_render_jobs(self) -> list[dict[str, Any]]:
        """Get current render job status."""
        return [
            {
                "job_id": job.job_id,
                "name": job.name,
                "progress": f"{job.frames_completed}/{job.frames_total}",
                "percent": round(job.frames_completed / job.frames_total * 100, 1),
                "status": job.status,
                "resolution": job.resolution,
                "gpu_memory_mb": job.gpu_memory_mb,
            }
            for job in self._render_jobs
        ]

    async def _tick(self):
        """Advance the simulation by one tick."""
        # Add natural variation to metrics
        if self.metrics.pipeline_state == PipelineState.HEALTHY:
            self.metrics.gpu_utilization += random.uniform(-2, 2)
            self.metrics.gpu_utilization = max(30, min(70, self.metrics.gpu_utilization))
            self.metrics.render_queue_depth += random.randint(-1, 1)
            self.metrics.render_queue_depth = max(2, self.metrics.render_queue_depth)

        elif self.metrics.pipeline_state == PipelineState.RECOVERING:
            # Gradually return to healthy
            self.metrics.gpu_utilization = max(
                45, self.metrics.gpu_utilization - random.uniform(1, 3)
            )
            self.metrics.memory_utilization = max(
                50, self.metrics.memory_utilization - random.uniform(1, 2)
            )
            if self.metrics.gpu_utilization < 60 and self.metrics.memory_utilization < 65:
                self.metrics.pipeline_state = PipelineState.HEALTHY
                logger.info("✅ Pipeline recovered to healthy state")

        # Advance render jobs
        for job in self._render_jobs:
            if job.status == "rendering":
                frames_per_tick = max(1, int(random.uniform(2, 8)))
                job.frames_completed = min(
                    job.frames_total, job.frames_completed + frames_per_tick
                )
                if job.frames_completed >= job.frames_total:
                    job.status = "completed"
