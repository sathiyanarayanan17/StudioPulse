"""StudioPulse AI - Demo Mode Entry Point

This runs the complete system in simulation mode with:
- Pipeline simulator generating realistic metrics
- Simulated Grafana & Compute (no real credentials needed)
- Web dashboard at http://localhost:8080
- Full agent pipeline (Monitor → Diagnose → Remediate)

Run with: python -m src.demo
"""

import asyncio
import sys
from src.simulator import PipelineSimulator
from src.simulator.grafana_sim import SimulatedGrafanaClient
from src.simulator.compute_sim import SimulatedComputeOperations
from src.agents.orchestrator import Orchestrator
from src.agents.monitor import MonitorAgent
from src.agents.diagnose import DiagnoseAgent
from src.agents.remediate import RemediateAgent
from src.grafana.alerts import AlertProcessor
from src.grafana.dashboards import DashboardQuerier
from src.cloud.vertex_ai import GeminiAgent
from src.api import APIServer
from src.utils.logger import setup_logger

logger = setup_logger("studiopulse-demo")


def print_demo_banner():
    """Print the demo mode banner."""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   🎬  S T U D I O P U L S E   A I  -  D E M O  M O D E    ║
║                                                              ║
║   ✅ No cloud credentials needed                            ║
║   ✅ Simulated rendering pipeline                           ║
║   ✅ Full agent pipeline active                             ║
║   ✅ Web dashboard at http://localhost:8080                  ║
║                                                              ║
║   Trigger scenarios from the dashboard or API:              ║
║   POST http://localhost:8080/api/trigger                     ║
║   {"scenario": "gpu_saturation"}                            ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
"""
    print(banner)


class DemoOrchestrator:
    """Orchestrator configured for demo mode with simulated backends."""

    def __init__(self, simulator: PipelineSimulator):
        self.simulator = simulator
        self.grafana_client = SimulatedGrafanaClient(simulator)
        self.compute_ops = SimulatedComputeOperations(simulator)
        self.dashboard_querier = DashboardQuerier.__new__(DashboardQuerier)
        self.dashboard_querier.grafana = self.grafana_client
        self.dashboard_querier.datasource_uid = "prometheus-sim"

        # Use Gemini if credentials are available, otherwise use mock
        try:
            self.gemini_agent = GeminiAgent()
            logger.info("Using real Gemini API for analysis")
        except Exception:
            self.gemini_agent = MockGeminiAgent()
            logger.info("Using mock Gemini agent (no credentials found)")

        # Set up agents
        self.monitor_agent = MonitorAgent(
            grafana_client=self.grafana_client,
            on_alert=self._handle_alert,
        )
        self.diagnose_agent = DiagnoseAgent(
            dashboard_querier=self.dashboard_querier,
            gemini_agent=self.gemini_agent,
            cloud_monitoring=MockCloudMonitoring(),
        )
        self.remediate_agent = RemediateAgent(
            gemini_agent=self.gemini_agent,
            compute_ops=self.compute_ops,
            grafana_client=self.grafana_client,
            dashboard_querier=self.dashboard_querier,
        )

        self._active_incidents = {}
        self._incident_history = []

    async def start(self):
        """Start monitoring in demo mode."""
        logger.info("Demo orchestrator started, monitoring for alerts...")
        await self.monitor_agent.start()

    async def _handle_alert(self, alert):
        """Handle alert in demo mode."""
        logger.info(f"🚨 Alert detected: {alert.title}")

        try:
            # Diagnose
            logger.info("📋 Diagnosing root cause...")
            diagnosis = await self.diagnose_agent.diagnose(alert)

            # Remediate
            logger.info("🔧 Executing remediation...")
            result = await self.remediate_agent.remediate(diagnosis)

            status = "✅ Resolved" if result["status"] == "resolved" else "⚠️ Needs attention"
            logger.info(f"{status}: {alert.title}")

        except Exception as e:
            logger.error(f"Pipeline error: {e}")

    def get_status(self):
        return {
            "mode": "demo",
            "active_incidents": len(self._active_incidents),
            "total_resolved": len(self._incident_history),
        }


class MockGeminiAgent:
    """Mock Gemini agent for when no credentials are available."""

    async def analyze_alert(self, alert_context):
        """Return a realistic mock diagnosis."""
        category = alert_context.get("category", "unknown")

        diagnoses = {
            "gpu_saturation": {
                "root_cause": "Concurrent 8K render jobs exceeding GPU pool capacity. 12 active jobs consuming 97% GPU across 3 nodes.",
                "confidence": 0.92,
                "contributing_factors": ["High-resolution 8K batch submitted", "No autoscaling policy active"],
            },
            "memory_leak": {
                "root_cause": "Render worker pod memory leak - growing 2GB/hour due to unfreed frame buffers in compositor stage.",
                "confidence": 0.85,
                "contributing_factors": ["render-worker v2.3.1 known memory leak", "No memory limit enforcement"],
            },
            "queue_backlog": {
                "root_cause": "Queue depth at 215 jobs while processing capacity limited to 8 concurrent renders.",
                "confidence": 0.95,
                "contributing_factors": ["Bulk job submission from production team", "GPU pool at minimum size"],
            },
            "disk_full": {
                "root_cause": "Render output volume at 95% - EXR frame outputs filling /data/renders faster than archival process.",
                "confidence": 0.88,
                "contributing_factors": ["Archival pipeline paused for maintenance", "8K outputs 4x larger than 4K"],
            },
            "node_failure": {
                "root_cause": "GPU node render-node-gpu-3 failed health check - NVIDIA driver crash detected.",
                "confidence": 0.91,
                "contributing_factors": ["Known driver issue with workload type", "Node running for 72 hours without restart"],
            },
        }

        diag = diagnoses.get(category, {
            "root_cause": "Anomalous behavior detected in rendering pipeline",
            "confidence": 0.75,
            "contributing_factors": ["Multiple correlated metric deviations"],
        })

        return {
            "diagnosis": diag,
            "recommendations": [
                {
                    "action": "scale_node_pool" if "gpu" in category or "queue" in category else "restart_workload",
                    "type": "scale",
                    "priority": 1,
                    "risk": "low",
                    "expected_impact": "Distribute load and reduce saturation within 2 minutes",
                }
            ],
            "requires_human": False,
            "explanation": diag["root_cause"],
        }

    async def plan_remediation(self, diagnosis, available_actions):
        """Return a realistic mock remediation plan."""
        root_cause = diagnosis.get("diagnosis", {}).get("root_cause", "")

        if "gpu" in root_cause.lower() or "capacity" in root_cause.lower():
            action = "scale_node_pool"
            params = {"cluster_name": "render-cluster", "node_pool_name": "gpu-pool", "target_size": 5}
        elif "memory" in root_cause.lower():
            action = "restart_workload"
            params = {"cluster_name": "render-cluster", "namespace": "render", "deployment_name": "render-worker"}
        elif "disk" in root_cause.lower():
            action = "resize_disk"
            params = {"instance_name": "render-node-1", "disk_name": "render-data", "new_size_gb": 1000}
        elif "node" in root_cause.lower() or "health" in root_cause.lower():
            action = "drain_and_replace_node"
            params = {"cluster_name": "render-cluster", "node_name": "render-node-gpu-3"}
        else:
            action = "restart_workload"
            params = {"cluster_name": "render-cluster", "namespace": "render", "deployment_name": "render-worker"}

        return {
            "steps": [
                {
                    "order": 1,
                    "action": action,
                    "parameters": params,
                    "rollback": f"Revert {action}",
                    "timeout_seconds": 120,
                }
            ],
            "estimated_resolution_time": "2m",
            "confidence": 0.88,
        }

    async def verify_resolution(self, original_alert, post_fix_metrics):
        """Return a mock verification."""
        return {
            "resolved": True,
            "confidence": 0.93,
            "remaining_issues": [],
            "summary": "Metrics returned to normal range. Pipeline operating within healthy thresholds.",
        }


class MockCloudMonitoring:
    """Mock Cloud Monitoring client for demo mode."""

    def get_metric(self, metric_type, minutes_ago=10, aggregation_minutes=1):
        return [{"value": 50.0, "timestamp": 1692000000}]

    def get_gke_metrics(self, cluster_name):
        return {
            "cpu_utilization": [{"value": 55.0}],
            "memory_utilization": [{"value": 60.0}],
            "gpu_utilization": [{"value": 45.0}],
            "pod_restart_count": [{"value": 0}],
        }

    def write_custom_metric(self, metric_type, value, labels=None):
        pass


async def run_demo():
    """Run the complete demo."""
    print_demo_banner()

    # Initialize simulator
    simulator = PipelineSimulator()

    # Initialize demo orchestrator
    orchestrator = DemoOrchestrator(simulator)

    # Initialize API server
    api_server = APIServer(simulator=simulator, orchestrator=orchestrator)

    # Start everything concurrently
    logger.info("Starting all components...")

    api_runner = await api_server.start(host="0.0.0.0", port=8080)

    # Run simulator + orchestrator
    await asyncio.gather(
        simulator.start(),
        orchestrator.start(),
    )


if __name__ == "__main__":
    try:
        asyncio.run(run_demo())
    except KeyboardInterrupt:
        print("\n🎬 Demo ended. That's a wrap!")
