"""Tests for the Remediate Agent."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from src.agents.remediate import RemediateAgent
from src.grafana.alerts import ProcessedAlert, AlertSeverity, AlertCategory


@pytest.fixture
def mock_gemini():
    agent = AsyncMock()
    agent.plan_remediation = AsyncMock(return_value={
        "steps": [
            {
                "order": 1,
                "action": "scale_node_pool",
                "parameters": {
                    "cluster_name": "render-cluster",
                    "node_pool_name": "gpu-pool",
                    "target_size": 5,
                },
                "rollback": "Scale back to 3 nodes",
                "timeout_seconds": 120,
            }
        ],
        "estimated_resolution_time": "3m",
        "confidence": 0.85,
    })
    agent.verify_resolution = AsyncMock(return_value={
        "resolved": True,
        "confidence": 0.92,
        "remaining_issues": [],
        "summary": "GPU utilization normalized after scaling to 5 nodes",
    })
    return agent


@pytest.fixture
def mock_compute():
    ops = AsyncMock()
    ops.scale_node_pool = AsyncMock(return_value={
        "action": "scale_node_pool",
        "status": "initiated",
        "target_size": 5,
    })
    return ops


@pytest.fixture
def mock_grafana():
    client = AsyncMock()
    client.create_annotation = AsyncMock(return_value={"id": 123})
    return client


@pytest.fixture
def mock_dashboard_querier():
    querier = AsyncMock()
    querier.get_correlated_metrics = AsyncMock(return_value={
        "gpu_utilization": 65.0,
        "gpu_memory": 55.0,
    })
    return querier


@pytest.fixture
def sample_diagnosis_result():
    alert = ProcessedAlert(
        alert_id="alert-003",
        title="GPU Saturation Critical",
        severity=AlertSeverity.CRITICAL,
        category=AlertCategory.GPU_SATURATION,
        labels={"instance": "render-node-1"},
        annotations={},
        value=98.0,
        source_dashboard=None,
        raw_data={},
    )
    return {
        "alert": alert,
        "diagnosis": {
            "diagnosis": {
                "root_cause": "Insufficient GPU nodes for current workload",
                "confidence": 0.87,
            },
            "recommendations": [
                {"action": "scale_node_pool", "type": "scale", "priority": 1}
            ],
        },
        "metrics_snapshot": {"gpu_utilization": 98.0},
    }


class TestRemediateAgent:
    """Test suite for RemediateAgent."""

    @pytest.mark.asyncio
    async def test_successful_remediation(
        self,
        mock_gemini,
        mock_compute,
        mock_grafana,
        mock_dashboard_querier,
        sample_diagnosis_result,
    ):
        """Should successfully remediate and verify."""
        agent = RemediateAgent(
            gemini_agent=mock_gemini,
            compute_ops=mock_compute,
            grafana_client=mock_grafana,
            dashboard_querier=mock_dashboard_querier,
        )

        with patch("src.agents.remediate.asyncio.sleep", new_callable=AsyncMock):
            result = await agent.remediate(sample_diagnosis_result)

        assert result["status"] == "resolved"
        assert result["annotation_created"] is True
        mock_compute.scale_node_pool.assert_called_once()

    @pytest.mark.asyncio
    async def test_creates_grafana_annotation(
        self,
        mock_gemini,
        mock_compute,
        mock_grafana,
        mock_dashboard_querier,
        sample_diagnosis_result,
    ):
        """Should create an annotation in Grafana after remediation."""
        agent = RemediateAgent(
            gemini_agent=mock_gemini,
            compute_ops=mock_compute,
            grafana_client=mock_grafana,
            dashboard_querier=mock_dashboard_querier,
        )

        with patch("src.agents.remediate.asyncio.sleep", new_callable=AsyncMock):
            await agent.remediate(sample_diagnosis_result)

        mock_grafana.create_annotation.assert_called_once()
        call_kwargs = mock_grafana.create_annotation.call_args[1]
        assert "studiopulse" in call_kwargs["tags"]

    @pytest.mark.asyncio
    async def test_handles_planning_failure(
        self,
        mock_gemini,
        mock_compute,
        mock_grafana,
        mock_dashboard_querier,
        sample_diagnosis_result,
    ):
        """Should handle gracefully when planning fails."""
        mock_gemini.plan_remediation = AsyncMock(
            return_value={"error": "Failed to parse"}
        )

        agent = RemediateAgent(
            gemini_agent=mock_gemini,
            compute_ops=mock_compute,
            grafana_client=mock_grafana,
            dashboard_querier=mock_dashboard_querier,
        )

        result = await agent.remediate(sample_diagnosis_result)

        assert result["status"] == "failed"
        assert result["reason"] == "planning_failed"
