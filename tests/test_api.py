"""Tests for the API Server."""

import pytest
import json
from unittest.mock import AsyncMock, MagicMock, patch
from aiohttp import web
from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop

from src.api import APIServer
from src.simulator import PipelineSimulator


@pytest.fixture
def simulator():
    """Create a fresh simulator instance."""
    return PipelineSimulator()


@pytest.fixture
def api_server(simulator):
    """Create an API server instance with simulator."""
    return APIServer(simulator=simulator, orchestrator=None)


@pytest.fixture
def app(api_server):
    """Get the aiohttp app for testing."""
    return api_server.app


class TestHealthEndpoint:
    """Test the /api/health endpoint."""

    @pytest.mark.asyncio
    async def test_health_returns_200(self, aiohttp_client, app):
        """Should return 200 status."""
        client = await aiohttp_client(app)
        resp = await client.get("/api/health")
        assert resp.status == 200

    @pytest.mark.asyncio
    async def test_health_returns_json(self, aiohttp_client, app):
        """Should return valid JSON with status field."""
        client = await aiohttp_client(app)
        resp = await client.get("/api/health")
        data = await resp.json()

        assert data["status"] == "healthy"
        assert data["service"] == "studiopulse-ai"
        assert "version" in data


class TestMetricsEndpoint:
    """Test the /api/metrics endpoint."""

    @pytest.mark.asyncio
    async def test_metrics_returns_200(self, aiohttp_client, app):
        """Should return 200 status."""
        client = await aiohttp_client(app)
        resp = await client.get("/api/metrics")
        assert resp.status == 200

    @pytest.mark.asyncio
    async def test_metrics_contains_gpu_data(self, aiohttp_client, app):
        """Should return GPU utilization data."""
        client = await aiohttp_client(app)
        resp = await client.get("/api/metrics")
        data = await resp.json()

        assert "gpu_utilization" in data
        assert "gpu_memory_percent" in data
        assert "pipeline_state" in data
        assert isinstance(data["gpu_utilization"], (int, float))

    @pytest.mark.asyncio
    async def test_metrics_contains_pipeline_state(self, aiohttp_client, app):
        """Should return pipeline state as string."""
        client = await aiohttp_client(app)
        resp = await client.get("/api/metrics")
        data = await resp.json()

        assert data["pipeline_state"] in ["healthy", "degraded", "critical", "recovering"]

    @pytest.mark.asyncio
    async def test_metrics_contains_render_data(self, aiohttp_client, app):
        """Should return render queue and job data."""
        client = await aiohttp_client(app)
        resp = await client.get("/api/metrics")
        data = await resp.json()

        assert "render_queue_depth" in data
        assert "active_render_jobs" in data
        assert "avg_frame_time_seconds" in data


class TestAlertsEndpoint:
    """Test the /api/alerts endpoint."""

    @pytest.mark.asyncio
    async def test_alerts_returns_200(self, aiohttp_client, app):
        """Should return 200 status."""
        client = await aiohttp_client(app)
        resp = await client.get("/api/alerts")
        assert resp.status == 200

    @pytest.mark.asyncio
    async def test_alerts_empty_initially(self, aiohttp_client, app):
        """Should return empty alerts list initially."""
        client = await aiohttp_client(app)
        resp = await client.get("/api/alerts")
        data = await resp.json()

        assert "alerts" in data
        assert "count" in data
        assert data["count"] == 0
        assert data["alerts"] == []

    @pytest.mark.asyncio
    async def test_alerts_after_trigger(self, aiohttp_client, app, simulator):
        """Should return alerts after scenario is triggered."""
        await simulator.trigger_scenario("gpu_saturation")

        client = await aiohttp_client(app)
        resp = await client.get("/api/alerts")
        data = await resp.json()

        assert data["count"] == 1
        assert len(data["alerts"]) == 1
        assert "title" in data["alerts"][0]


class TestJobsEndpoint:
    """Test the /api/jobs endpoint."""

    @pytest.mark.asyncio
    async def test_jobs_returns_200(self, aiohttp_client, app):
        """Should return 200 status."""
        client = await aiohttp_client(app)
        resp = await client.get("/api/jobs")
        assert resp.status == 200

    @pytest.mark.asyncio
    async def test_jobs_returns_render_jobs(self, aiohttp_client, app):
        """Should return list of render jobs."""
        client = await aiohttp_client(app)
        resp = await client.get("/api/jobs")
        data = await resp.json()

        assert "jobs" in data
        assert len(data["jobs"]) > 0

    @pytest.mark.asyncio
    async def test_job_has_required_fields(self, aiohttp_client, app):
        """Should include required fields in each job."""
        client = await aiohttp_client(app)
        resp = await client.get("/api/jobs")
        data = await resp.json()

        job = data["jobs"][0]
        assert "job_id" in job
        assert "name" in job
        assert "status" in job
        assert "percent" in job


class TestIncidentsEndpoint:
    """Test the /api/incidents endpoint."""

    @pytest.mark.asyncio
    async def test_incidents_returns_200(self, aiohttp_client, app):
        """Should return 200 status."""
        client = await aiohttp_client(app)
        resp = await client.get("/api/incidents")
        assert resp.status == 200

    @pytest.mark.asyncio
    async def test_incidents_empty_initially(self, aiohttp_client, app):
        """Should return empty incident list initially."""
        client = await aiohttp_client(app)
        resp = await client.get("/api/incidents")
        data = await resp.json()

        assert "incidents" in data
        assert data["incidents"] == []

    @pytest.mark.asyncio
    async def test_incidents_after_log(self, aiohttp_client, app, api_server):
        """Should contain logged incidents."""
        api_server.log_incident({
            "alert_id": "test-001",
            "title": "Test incident",
            "status": "resolved",
        })

        client = await aiohttp_client(app)
        resp = await client.get("/api/incidents")
        data = await resp.json()

        assert len(data["incidents"]) == 1
        assert data["incidents"][0]["alert_id"] == "test-001"


class TestTriggerEndpoint:
    """Test the /api/trigger endpoint."""

    @pytest.mark.asyncio
    async def test_trigger_returns_200(self, aiohttp_client, app):
        """Should return 200 on successful trigger."""
        client = await aiohttp_client(app)
        resp = await client.post(
            "/api/trigger",
            json={"scenario": "gpu_saturation"},
        )
        assert resp.status == 200

    @pytest.mark.asyncio
    async def test_trigger_returns_alert_info(self, aiohttp_client, app):
        """Should return triggered alert info."""
        client = await aiohttp_client(app)
        resp = await client.post(
            "/api/trigger",
            json={"scenario": "memory_leak"},
        )
        data = await resp.json()

        assert data["status"] == "triggered"
        assert "alert" in data
        assert "uid" in data["alert"]
        assert "title" in data["alert"]

    @pytest.mark.asyncio
    async def test_trigger_random_scenario(self, aiohttp_client, app):
        """Should work without specifying a scenario."""
        client = await aiohttp_client(app)
        resp = await client.post("/api/trigger", json={})
        data = await resp.json()

        assert data["status"] == "triggered"

    @pytest.mark.asyncio
    async def test_trigger_without_body(self, aiohttp_client, app):
        """Should work even without a request body."""
        client = await aiohttp_client(app)
        resp = await client.post("/api/trigger")
        assert resp.status == 200

    @pytest.mark.asyncio
    async def test_trigger_adds_to_incident_log(self, aiohttp_client, app):
        """Should add triggered scenario to incident log."""
        client = await aiohttp_client(app)
        await client.post(
            "/api/trigger",
            json={"scenario": "disk_full"},
        )

        resp = await client.get("/api/incidents")
        data = await resp.json()
        assert len(data["incidents"]) >= 1


class TestStatusEndpoint:
    """Test the /api/status endpoint."""

    @pytest.mark.asyncio
    async def test_status_returns_200(self, aiohttp_client, app):
        """Should return 200 status."""
        client = await aiohttp_client(app)
        resp = await client.get("/api/status")
        assert resp.status == 200

    @pytest.mark.asyncio
    async def test_status_no_orchestrator(self, aiohttp_client, app):
        """Should return message when no orchestrator connected."""
        client = await aiohttp_client(app)
        resp = await client.get("/api/status")
        data = await resp.json()

        assert "message" in data

    @pytest.mark.asyncio
    async def test_status_with_orchestrator(self, aiohttp_client, simulator):
        """Should return orchestrator status when connected."""
        mock_orchestrator = MagicMock()
        mock_orchestrator.get_status.return_value = {
            "mode": "demo",
            "active_incidents": 0,
            "total_resolved": 5,
        }
        server = APIServer(simulator=simulator, orchestrator=mock_orchestrator)
        client = await aiohttp_client(server.app)

        resp = await client.get("/api/status")
        data = await resp.json()

        assert data["mode"] == "demo"
        assert data["total_resolved"] == 5


class TestAPIServerLogIncident:
    """Test the log_incident method."""

    def test_log_incident_adds_to_list(self, api_server):
        """Should add incident to internal log."""
        api_server.log_incident({
            "alert_id": "test-123",
            "title": "Test Alert",
            "status": "detected",
        })

        assert len(api_server._incident_log) == 1
        assert api_server._incident_log[0]["alert_id"] == "test-123"

    def test_log_multiple_incidents(self, api_server):
        """Should accumulate multiple incidents."""
        for i in range(5):
            api_server.log_incident({"alert_id": f"test-{i}", "title": f"Alert {i}"})

        assert len(api_server._incident_log) == 5
