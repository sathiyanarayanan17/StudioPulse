"""Tests for the Monitor Agent."""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from src.agents.monitor import MonitorAgent
from src.grafana.alerts import ProcessedAlert, AlertSeverity, AlertCategory


@pytest.fixture
def mock_grafana_client():
    client = AsyncMock()
    client.get_alerts = AsyncMock(return_value=[])
    return client


@pytest.fixture
def mock_callback():
    return AsyncMock()


@pytest.fixture
def monitor_agent(mock_grafana_client, mock_callback):
    with patch("src.agents.monitor.load_config") as mock_config:
        mock_config.return_value = MagicMock(
            agent=MagicMock(polling_interval=1)
        )
        agent = MonitorAgent(
            grafana_client=mock_grafana_client,
            on_alert=mock_callback,
        )
    return agent


@pytest.fixture
def sample_alert():
    return ProcessedAlert(
        alert_id="alert-001",
        title="GPU Utilization > 95%",
        severity=AlertSeverity.CRITICAL,
        category=AlertCategory.GPU_SATURATION,
        labels={"instance": "render-node-1", "severity": "critical"},
        annotations={"description": "GPU saturation detected"},
        value=97.5,
        source_dashboard="render-pipeline",
        raw_data={},
    )


class TestMonitorAgent:
    """Test suite for MonitorAgent."""

    @pytest.mark.asyncio
    async def test_detects_new_alert(self, monitor_agent, mock_callback, sample_alert):
        """Should call on_alert when a new alert is detected."""
        with patch.object(
            monitor_agent.alert_processor,
            "fetch_and_process_alerts",
            return_value=[sample_alert],
        ):
            await monitor_agent._check_alerts()

        mock_callback.assert_called_once_with(sample_alert)

    @pytest.mark.asyncio
    async def test_does_not_duplicate_alerts(self, monitor_agent, mock_callback, sample_alert):
        """Should not trigger callback for already-seen alerts."""
        with patch.object(
            monitor_agent.alert_processor,
            "fetch_and_process_alerts",
            return_value=[sample_alert],
        ):
            await monitor_agent._check_alerts()
            await monitor_agent._check_alerts()

        # Should only be called once
        mock_callback.assert_called_once()

    @pytest.mark.asyncio
    async def test_cleans_resolved_alerts(self, monitor_agent, mock_callback, sample_alert):
        """Should clear seen alerts when they resolve."""
        with patch.object(
            monitor_agent.alert_processor,
            "fetch_and_process_alerts",
            return_value=[sample_alert],
        ):
            await monitor_agent._check_alerts()

        # Alert resolves
        with patch.object(
            monitor_agent.alert_processor,
            "fetch_and_process_alerts",
            return_value=[],
        ):
            await monitor_agent._check_alerts()

        assert sample_alert.alert_id not in monitor_agent._seen_alerts

    @pytest.mark.asyncio
    async def test_stop_sets_running_false(self, monitor_agent):
        """Should set _running to False on stop."""
        await monitor_agent.stop()
        assert monitor_agent._running is False
