"""Tests for the Pipeline Simulator."""

import pytest
import asyncio
from unittest.mock import patch, AsyncMock
from src.simulator import PipelineSimulator, PipelineState, SimulatedMetrics, RenderJob


@pytest.fixture
def simulator():
    """Create a fresh simulator instance."""
    return PipelineSimulator()


class TestPipelineSimulatorInit:
    """Test simulator initialization."""

    def test_initializes_with_healthy_state(self, simulator):
        """Should start in healthy state."""
        assert simulator.metrics.pipeline_state == PipelineState.HEALTHY

    def test_initializes_with_no_alerts(self, simulator):
        """Should start with no active alerts."""
        assert len(simulator.active_alerts) == 0

    def test_initializes_with_render_jobs(self, simulator):
        """Should start with initial render jobs."""
        assert len(simulator._render_jobs) > 0

    def test_initializes_with_default_metrics(self, simulator):
        """Should start with default healthy metrics."""
        assert simulator.metrics.gpu_utilization == 45.0
        assert simulator.metrics.memory_utilization == 50.0
        assert simulator.metrics.healthy_nodes == 3
        assert simulator.metrics.node_count == 3

    def test_has_available_scenarios(self, simulator):
        """Should have predefined scenarios available."""
        assert len(PipelineSimulator.SCENARIOS) >= 5
        names = [s["name"] for s in PipelineSimulator.SCENARIOS]
        assert "gpu_saturation" in names
        assert "memory_leak" in names
        assert "queue_backlog" in names
        assert "disk_full" in names
        assert "node_failure" in names


class TestTriggerScenario:
    """Test scenario triggering."""

    @pytest.mark.asyncio
    async def test_trigger_specific_scenario(self, simulator):
        """Should apply correct metrics for a named scenario."""
        alert = await simulator.trigger_scenario("gpu_saturation")

        assert alert is not None
        assert alert.title == "GPU Utilization Critical - Render Nodes Saturated"
        assert alert.severity == "critical"
        assert alert.state == "firing"
        assert simulator.metrics.gpu_utilization == 97.5
        assert simulator.metrics.pipeline_state == PipelineState.CRITICAL

    @pytest.mark.asyncio
    async def test_trigger_random_scenario(self, simulator):
        """Should trigger a random scenario when no name given."""
        alert = await simulator.trigger_scenario(None)

        assert alert is not None
        assert alert.state == "firing"
        assert simulator.metrics.pipeline_state == PipelineState.CRITICAL

    @pytest.mark.asyncio
    async def test_trigger_memory_leak(self, simulator):
        """Should apply memory leak metrics correctly."""
        alert = await simulator.trigger_scenario("memory_leak")

        assert simulator.metrics.memory_utilization == 94.0
        assert simulator.metrics.gpu_memory_percent == 88.0
        assert simulator.metrics.failed_renders_per_min == 3.2
        assert "Memory Leak" in alert.title

    @pytest.mark.asyncio
    async def test_trigger_disk_full(self, simulator):
        """Should apply disk full metrics correctly."""
        alert = await simulator.trigger_scenario("disk_full")

        assert simulator.metrics.disk_usage_percent == 95.5
        assert simulator.metrics.failed_renders_per_min == 5.0

    @pytest.mark.asyncio
    async def test_trigger_node_failure(self, simulator):
        """Should reduce healthy nodes on node failure."""
        alert = await simulator.trigger_scenario("node_failure")

        assert simulator.metrics.healthy_nodes == 2
        assert simulator.metrics.node_count == 3

    @pytest.mark.asyncio
    async def test_trigger_adds_alert(self, simulator):
        """Should add an alert to active_alerts list."""
        assert len(simulator.active_alerts) == 0
        await simulator.trigger_scenario("gpu_saturation")
        assert len(simulator.active_alerts) == 1

    @pytest.mark.asyncio
    async def test_trigger_invalid_falls_back_to_random(self, simulator):
        """Should fall back to random when invalid scenario name given."""
        alert = await simulator.trigger_scenario("nonexistent_scenario")
        assert alert is not None
        assert simulator.metrics.pipeline_state == PipelineState.CRITICAL


class TestRemediation:
    """Test remediation actions."""

    @pytest.mark.asyncio
    async def test_scale_node_pool(self, simulator):
        """Should reduce GPU utilization when scaling."""
        await simulator.trigger_scenario("gpu_saturation")
        result = simulator.apply_remediation("scale_node_pool", {"target_size": 5})

        assert result["status"] == "success"
        assert simulator.metrics.node_count == 5
        assert simulator.metrics.healthy_nodes == 5
        assert simulator.metrics.gpu_utilization < 97.5
        assert simulator.metrics.pipeline_state == PipelineState.RECOVERING

    @pytest.mark.asyncio
    async def test_restart_workload(self, simulator):
        """Should reset memory metrics on restart."""
        await simulator.trigger_scenario("memory_leak")
        result = simulator.apply_remediation("restart_workload")

        assert result["status"] == "success"
        assert simulator.metrics.memory_utilization == 50.0
        assert simulator.metrics.gpu_memory_percent == 45.0
        assert simulator.metrics.failed_renders_per_min == 0.0

    @pytest.mark.asyncio
    async def test_resize_disk(self, simulator):
        """Should reduce disk usage on resize."""
        await simulator.trigger_scenario("disk_full")
        result = simulator.apply_remediation("resize_disk")

        assert result["status"] == "success"
        assert simulator.metrics.disk_usage_percent == 45.0

    @pytest.mark.asyncio
    async def test_drain_and_replace_node(self, simulator):
        """Should restore healthy nodes on drain and replace."""
        await simulator.trigger_scenario("node_failure")
        result = simulator.apply_remediation("drain_and_replace_node")

        assert result["status"] == "success"
        assert simulator.metrics.healthy_nodes == simulator.metrics.node_count

    @pytest.mark.asyncio
    async def test_remediation_clears_alerts(self, simulator):
        """Should clear firing alerts after remediation."""
        await simulator.trigger_scenario("gpu_saturation")
        assert len(simulator.active_alerts) == 1

        simulator.apply_remediation("scale_node_pool", {"target_size": 5})
        assert len(simulator.active_alerts) == 0

    @pytest.mark.asyncio
    async def test_remediation_returns_new_metrics(self, simulator):
        """Should return updated metrics in result."""
        await simulator.trigger_scenario("gpu_saturation")
        result = simulator.apply_remediation("scale_node_pool", {"target_size": 5})

        assert "new_metrics" in result
        assert result["new_metrics"]["node_count"] == 5


class TestGetMetrics:
    """Test metrics retrieval."""

    def test_get_current_metrics_returns_dict(self, simulator):
        """Should return metrics as a dictionary."""
        metrics = simulator.get_current_metrics()

        assert isinstance(metrics, dict)
        assert "gpu_utilization" in metrics
        assert "memory_utilization" in metrics
        assert "pipeline_state" in metrics
        assert "render_queue_depth" in metrics
        assert "node_count" in metrics

    def test_metrics_values_are_rounded(self, simulator):
        """Should return rounded float values."""
        simulator.metrics.gpu_utilization = 45.123456
        metrics = simulator.get_current_metrics()

        assert metrics["gpu_utilization"] == 45.1

    def test_pipeline_state_is_string(self, simulator):
        """Should return pipeline state as a string value."""
        metrics = simulator.get_current_metrics()
        assert metrics["pipeline_state"] == "healthy"


class TestGetAlerts:
    """Test alert retrieval in Grafana format."""

    def test_returns_empty_when_no_alerts(self, simulator):
        """Should return empty list when no alerts active."""
        alerts = simulator.get_alerts_as_grafana_format()
        assert alerts == []

    @pytest.mark.asyncio
    async def test_returns_alert_in_grafana_format(self, simulator):
        """Should format alerts with required Grafana fields."""
        await simulator.trigger_scenario("gpu_saturation")
        alerts = simulator.get_alerts_as_grafana_format()

        assert len(alerts) == 1
        alert = alerts[0]
        assert "uid" in alert
        assert "title" in alert
        assert "state" in alert
        assert "labels" in alert
        assert "annotations" in alert
        assert "value" in alert


class TestGetRenderJobs:
    """Test render job retrieval."""

    def test_returns_initial_jobs(self, simulator):
        """Should return initial render jobs."""
        jobs = simulator.get_render_jobs()
        assert len(jobs) > 0

    def test_job_has_required_fields(self, simulator):
        """Should include all required fields in job info."""
        jobs = simulator.get_render_jobs()
        job = jobs[0]

        assert "job_id" in job
        assert "name" in job
        assert "progress" in job
        assert "percent" in job
        assert "status" in job
        assert "resolution" in job
        assert "gpu_memory_mb" in job

    def test_job_percent_is_calculated(self, simulator):
        """Should calculate percent from frames."""
        jobs = simulator.get_render_jobs()
        for job in jobs:
            assert 0 <= job["percent"] <= 100


class TestSimulationTick:
    """Test the simulation tick loop."""

    @pytest.mark.asyncio
    async def test_tick_varies_healthy_metrics(self, simulator):
        """Should add natural variation in healthy state."""
        initial_gpu = simulator.metrics.gpu_utilization
        # Run several ticks
        for _ in range(10):
            await simulator._tick()

        # After 10 ticks, GPU should have varied (probabilistic but very likely)
        # We just verify it stays in bounds
        assert 30 <= simulator.metrics.gpu_utilization <= 70

    @pytest.mark.asyncio
    async def test_tick_recovers_from_critical(self, simulator):
        """Should gradually recover when in recovering state."""
        simulator.metrics.pipeline_state = PipelineState.RECOVERING
        simulator.metrics.gpu_utilization = 80.0
        simulator.metrics.memory_utilization = 75.0

        # Run ticks until recovery or max iterations
        for _ in range(50):
            await simulator._tick()
            if simulator.metrics.pipeline_state == PipelineState.HEALTHY:
                break

        assert simulator.metrics.pipeline_state == PipelineState.HEALTHY

    @pytest.mark.asyncio
    async def test_tick_advances_render_jobs(self, simulator):
        """Should advance rendering jobs."""
        # Ensure at least one job is rendering
        rendering_jobs = [j for j in simulator._render_jobs if j.status == "rendering"]
        assert len(rendering_jobs) > 0

        initial_frames = rendering_jobs[0].frames_completed
        for _ in range(5):
            await simulator._tick()

        assert rendering_jobs[0].frames_completed > initial_frames
