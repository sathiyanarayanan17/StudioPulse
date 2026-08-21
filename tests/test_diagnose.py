"""Tests for the Diagnose Agent."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from src.agents.diagnose import DiagnoseAgent
from src.grafana.alerts import ProcessedAlert, AlertSeverity, AlertCategory


@pytest.fixture
def mock_dashboard_querier():
    querier = AsyncMock()
    querier.get_correlated_metrics = AsyncMock(return_value={
        "gpu_utilization": 96.5,
        "gpu_memory": 88.2,
        "render_job_duration": 450.0,
    })
    return querier


@pytest.fixture
def mock_gemini_agent():
    agent = AsyncMock()
    agent.analyze_alert = AsyncMock(return_value={
        "diagnosis": {
            "root_cause": "GPU memory saturation due to oversized frame buffers",
            "confidence": 0.87,
            "contributing_factors": [
                "High-resolution 8K render jobs",
                "Insufficient GPU memory per node",
            ],
        },
        "recommendations": [
            {
                "action": "Scale GPU node pool",
                "type": "scale",
                "priority": 1,
                "risk": "low",
                "expected_impact": "Distribute load across more GPUs",
            }
        ],
        "requires_human": False,
        "explanation": "GPU memory exhaustion from concurrent 8K renders",
    })
    return agent


@pytest.fixture
def mock_cloud_monitoring():
    monitoring = MagicMock()
    monitoring.get_gke_metrics = MagicMock(return_value={
        "cpu_utilization": [{"value": 75.0}],
        "memory_utilization": [{"value": 82.0}],
        "gpu_utilization": [{"value": 96.5}],
    })
    return monitoring


@pytest.fixture
def sample_alert():
    return ProcessedAlert(
        alert_id="alert-002",
        title="GPU Memory Critical",
        severity=AlertSeverity.CRITICAL,
        category=AlertCategory.GPU_SATURATION,
        labels={"instance": "render-node-2"},
        annotations={"description": "GPU memory > 90%"},
        value=92.0,
        source_dashboard="gpu-dashboard",
        raw_data={},
    )


class TestDiagnoseAgent:
    """Test suite for DiagnoseAgent."""

    @pytest.mark.asyncio
    async def test_diagnose_returns_structured_result(
        self,
        mock_dashboard_querier,
        mock_gemini_agent,
        mock_cloud_monitoring,
        sample_alert,
    ):
        """Should return diagnosis with alert, diagnosis, and metrics."""
        agent = DiagnoseAgent(
            dashboard_querier=mock_dashboard_querier,
            gemini_agent=mock_gemini_agent,
            cloud_monitoring=mock_cloud_monitoring,
        )

        result = await agent.diagnose(sample_alert)

        assert "alert" in result
        assert "diagnosis" in result
        assert "metrics_snapshot" in result
        assert result["alert"] == sample_alert

    @pytest.mark.asyncio
    async def test_diagnose_queries_correlated_metrics(
        self,
        mock_dashboard_querier,
        mock_gemini_agent,
        mock_cloud_monitoring,
        sample_alert,
    ):
        """Should query metrics correlated to the alert category."""
        agent = DiagnoseAgent(
            dashboard_querier=mock_dashboard_querier,
            gemini_agent=mock_gemini_agent,
            cloud_monitoring=mock_cloud_monitoring,
        )

        await agent.diagnose(sample_alert)

        mock_dashboard_querier.get_correlated_metrics.assert_called_once_with(
            category="gpu_saturation"
        )

    @pytest.mark.asyncio
    async def test_diagnose_calls_gemini_analysis(
        self,
        mock_dashboard_querier,
        mock_gemini_agent,
        mock_cloud_monitoring,
        sample_alert,
    ):
        """Should send alert context to Gemini for analysis."""
        agent = DiagnoseAgent(
            dashboard_querier=mock_dashboard_querier,
            gemini_agent=mock_gemini_agent,
            cloud_monitoring=mock_cloud_monitoring,
        )

        await agent.diagnose(sample_alert)

        mock_gemini_agent.analyze_alert.assert_called_once()
        call_args = mock_gemini_agent.analyze_alert.call_args[0][0]
        assert call_args["category"] == "gpu_saturation"
        assert call_args["severity"] == "critical"
