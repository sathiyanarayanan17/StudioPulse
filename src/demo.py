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
import time
from src.simulator import PipelineSimulator
from src.simulator.grafana_sim import SimulatedGrafanaClient
from src.simulator.compute_sim import SimulatedComputeOperations
from src.agents.monitor import MonitorAgent
from src.agents.diagnose import DiagnoseAgent
from src.agents.remediate import RemediateAgent
from src.grafana.dashboards import DashboardQuerier
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
║   Available scenarios:                                       ║
║     gpu_saturation | memory_leak | queue_backlog            ║
║     disk_full | node_failure                                ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
"""
    print(banner)


class MockGeminiAgent:
    """Mock Gemini agent that returns realistic AI responses for demo."""

    async def analyze_alert(self, alert_context):
        """Return a realistic mock diagnosis based on alert category."""
        category = alert_context.get("category", "unknown")

        diagnoses = {
            "gpu_saturation": {
                "diagnosis": {
                    "root_cause": "Concurrent 8K render jobs exceeding GPU pool capacity. 12 active jobs consuming 97% GPU across 3 nodes.",
                    "confidence": 0.92,
                    "contributing_factors": [
                        "High-resolution 8K batch submitted by production team",
                        "No GPU autoscaling policy active",
                        "Node pool at minimum size (3 nodes)",
                    ],
                },
                "recommendations": [
                    {
                        "action": "Scale GPU node pool from 3 to 5 nodes",
                        "type": "scale",
                        "priority": 1,
                        "risk": "low",
                        "expected_impact": "Reduce GPU utilization to ~60% within 2 minutes",
                    }
                ],
                "requires_human": False,
                "explanation": "GPU pool saturated by concurrent 8K render batch. Scaling will distribute load.",
            },
            "memory_leak": {
                "diagnosis": {
                    "root_cause": "Render worker pod memory leak - growing 2GB/hour due to unfreed frame buffers in compositor stage.",
                    "confidence": 0.85,
                    "contributing_factors": [
                        "render-worker v2.3.1 known memory leak in compositor",
                        "No memory limit enforcement on pods",
                        "Pods running for 72+ hours without restart",
                    ],
                },
                "recommendations": [
                    {
                        "action": "Rolling restart of render-worker deployment",
                        "type": "restart",
                        "priority": 1,
                        "risk": "low",
                        "expected_impact": "Free leaked memory, restore to baseline 50% usage",
                    }
                ],
                "requires_human": False,
                "explanation": "Memory leak in compositor stage. Rolling restart will free memory without job loss.",
            },
            "queue_backlog": {
                "diagnosis": {
                    "root_cause": "Queue depth at 215 jobs while processing capacity limited to 8 concurrent renders on 3 GPU nodes.",
                    "confidence": 0.95,
                    "contributing_factors": [
                        "Bulk job submission from production team (200+ jobs)",
                        "GPU pool at minimum size of 3 nodes",
                        "Average frame time increased due to 8K resolution",
                    ],
                },
                "recommendations": [
                    {
                        "action": "Scale GPU node pool to 6 nodes",
                        "type": "scale",
                        "priority": 1,
                        "risk": "low",
                        "expected_impact": "Double throughput, clear backlog in ~15 minutes",
                    }
                ],
                "requires_human": False,
                "explanation": "Queue overwhelmed by bulk submission. Scaling nodes will increase throughput.",
            },
            "disk_full": {
                "diagnosis": {
                    "root_cause": "Render output volume at 95% - EXR frame outputs filling /data/renders faster than archival process.",
                    "confidence": 0.88,
                    "contributing_factors": [
                        "Archival pipeline paused for scheduled maintenance",
                        "8K EXR outputs are 4x larger than standard 4K",
                        "Volume provisioned for 4K workload capacity",
                    ],
                },
                "recommendations": [
                    {
                        "action": "Resize render-data disk from 500GB to 1TB",
                        "type": "resize",
                        "priority": 1,
                        "risk": "low",
                        "expected_impact": "Immediately double available space, prevent render failures",
                    }
                ],
                "requires_human": False,
                "explanation": "Disk filling from 8K outputs faster than archival. Online resize will provide immediate relief.",
            },
            "node_failure": {
                "diagnosis": {
                    "root_cause": "GPU node render-node-gpu-3 failed health check - NVIDIA driver crash detected in kernel logs.",
                    "confidence": 0.91,
                    "contributing_factors": [
                        "Known NVIDIA driver bug with mixed precision workloads",
                        "Node running continuously for 72 hours",
                        "No automatic node recycling policy",
                    ],
                },
                "recommendations": [
                    {
                        "action": "Drain failed node and let autoscaler provision replacement",
                        "type": "drain",
                        "priority": 1,
                        "risk": "low",
                        "expected_impact": "Evict pods safely, replacement node online in ~3 minutes",
                    }
                ],
                "requires_human": False,
                "explanation": "GPU driver crash on node-3. Drain and replace is safest recovery path.",
            },
        }

        result = diagnoses.get(category, {
            "diagnosis": {
                "root_cause": "Anomalous behavior detected in rendering pipeline metrics",
                "confidence": 0.75,
                "contributing_factors": ["Multiple correlated metric deviations detected"],
            },
            "recommendations": [
                {
                    "action": "Restart affected workloads",
                    "type": "restart",
                    "priority": 1,
                    "risk": "low",
                    "expected_impact": "Reset to known good state",
                }
            ],
            "requires_human": False,
            "explanation": "General anomaly detected. Restarting affected components.",
        })

        # Simulate AI thinking time
        await asyncio.sleep(2)
        return result

    async def plan_remediation(self, diagnosis, available_actions):
        """Return a realistic mock remediation plan."""
        root_cause = str(diagnosis.get("diagnosis", {}).get("root_cause", ""))

        if "gpu" in root_cause.lower() or "capacity" in root_cause.lower() or "queue" in root_cause.lower():
            action = "scale_node_pool"
            params = {"cluster_name": "render-cluster", "node_pool_name": "gpu-pool", "target_size": 5}
        elif "memory" in root_cause.lower() or "leak" in root_cause.lower():
            action = "restart_workload"
            params = {"cluster_name": "render-cluster", "namespace": "render", "deployment_name": "render-worker"}
        elif "disk" in root_cause.lower() or "volume" in root_cause.lower():
            action = "resize_disk"
            params = {"instance_name": "render-node-1", "disk_name": "render-data", "new_size_gb": 1000}
        elif "node" in root_cause.lower() or "health" in root_cause.lower() or "driver" in root_cause.lower():
            action = "drain_and_replace_node"
            params = {"cluster_name": "render-cluster", "node_name": "render-node-gpu-3"}
        else:
            action = "restart_workload"
            params = {"cluster_name": "render-cluster", "namespace": "render", "deployment_name": "render-worker"}

        # Simulate AI thinking time
        await asyncio.sleep(1)

        return {
            "steps": [
                {
                    "order": 1,
                    "action": action,
                    "parameters": params,
                    "rollback": f"Revert {action} to previous state",
                    "timeout_seconds": 120,
                }
            ],
            "estimated_resolution_time": "2m",
            "confidence": 0.88,
        }

    async def verify_resolution(self, original_alert, post_fix_metrics):
        """Return a mock verification result."""
        await asyncio.sleep(1)
        return {
            "resolved": True,
            "confidence": 0.93,
            "remaining_issues": [],
            "summary": "All metrics returned to healthy thresholds. Pipeline operating normally. No further action required.",
        }


class MockCloudMonitoring:
    """Mock Cloud Monitoring client for demo mode."""

    def get_metric(self, metric_type, minutes_ago=10, aggregation_minutes=1):
        return [{"value": 50.0, "timestamp": time.time()}]

    def get_gke_metrics(self, cluster_name):
        return {
            "cpu_utilization": [{"value": 55.0}],
            "memory_utilization": [{"value": 60.0}],
            "gpu_utilization": [{"value": 45.0}],
            "pod_restart_count": [{"value": 0}],
        }

    def write_custom_metric(self, metric_type, value, labels=None):
        pass


class DemoOrchestrator:
    """Orchestrator configured for demo mode with simulated backends."""

    def __init__(self, simulator: PipelineSimulator):
        self.simulator = simulator
        self.grafana_client = SimulatedGrafanaClient(simulator)
        self.compute_ops = SimulatedComputeOperations(simulator)

        # Create DashboardQuerier with simulated grafana client
        self.dashboard_querier = DashboardQuerier.__new__(DashboardQuerier)
        self.dashboard_querier.grafana = self.grafana_client
        self.dashboard_querier.datasource_uid = "prometheus-sim"

        # Use mock Gemini (no credentials needed)
        self.gemini_agent = MockGeminiAgent()

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

        self._active_incidents: dict = {}
        self._incident_history: list = []
        self.api_server = None  # Will be set externally

    async def start(self):
        """Start monitoring in demo mode."""
        logger.info("🤖 Demo orchestrator started, monitoring for alerts...")
        await self.monitor_agent.start()

    async def stop(self):
        """Stop the orchestrator."""
        await self.monitor_agent.stop()
        await self.grafana_client.close()

    async def _handle_alert(self, alert):
        """Handle alert - full pipeline: detect → diagnose → remediate."""
        logger.info(
            "🚨 Pipeline triggered",
            alert_id=alert.alert_id,
            title=alert.title,
            severity=alert.severity.value,
        )

        incident = {
            "alert_id": alert.alert_id,
            "title": alert.title,
            "status": "diagnosing",
            "timestamp": time.time(),
        }
        self._active_incidents[alert.alert_id] = incident

        # Notify API server
        if self.api_server:
            self.api_server.log_incident(incident.copy())

        try:
            # Phase 1: Diagnose
            logger.info("📋 Phase 1: Diagnosing root cause...")
            diagnosis = await self.diagnose_agent.diagnose(alert)

            root_cause = diagnosis.get("diagnosis", {}).get("diagnosis", {}).get("root_cause", "Unknown")
            logger.info(f"🧠 Diagnosis: {root_cause}")

            incident["status"] = "remediating"
            incident["root_cause"] = root_cause

            # Phase 2: Remediate
            logger.info("🔧 Phase 2: Executing remediation...")
            result = await self.remediate_agent.remediate(diagnosis)

            # Phase 3: Record outcome
            resolved = result.get("status") == "resolved"
            incident["status"] = "resolved" if resolved else "requires_attention"
            incident["resolution"] = result.get("verification", {}).get("summary", "")

            # Move to history
            self._incident_history.append(incident)
            del self._active_incidents[alert.alert_id]

            # Update API server
            if self.api_server:
                self.api_server.log_incident(incident.copy())

            emoji = "✅" if resolved else "⚠️"
            logger.info(
                f"{emoji} Pipeline complete",
                alert_id=alert.alert_id,
                status=incident["status"],
            )

        except Exception as e:
            logger.error(f"❌ Pipeline error: {e}")
            incident["status"] = "error"
            incident["error"] = str(e)

    def get_status(self):
        return {
            "mode": "demo",
            "active_incidents": len(self._active_incidents),
            "total_resolved": len([i for i in self._incident_history if i.get("status") == "resolved"]),
            "total_incidents": len(self._incident_history),
        }


async def run_demo():
    """Run the complete demo system."""
    print_demo_banner()

    # Initialize simulator
    simulator = PipelineSimulator()

    # Initialize demo orchestrator
    orchestrator = DemoOrchestrator(simulator)

    # Initialize API server
    api_server = APIServer(simulator=simulator, orchestrator=orchestrator)
    orchestrator.api_server = api_server

    # Start API server
    logger.info("Starting all components...")
    api_runner = await api_server.start(host="0.0.0.0", port=8080)

    print("\n  🌐 Dashboard ready at: http://localhost:8080")
    print("  📡 API ready at: http://localhost:8080/api/health")
    print("\n  Press Ctrl+C to stop\n")

    # Run simulator + orchestrator concurrently
    try:
        await asyncio.gather(
            simulator.start(),
            orchestrator.start(),
        )
    except asyncio.CancelledError:
        pass
    finally:
        await orchestrator.stop()
        await api_runner.cleanup()


if __name__ == "__main__":
    try:
        asyncio.run(run_demo())
    except KeyboardInterrupt:
        print("\n\n  🎬 Demo ended. That's a wrap!\n")
