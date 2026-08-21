"""StudioPulse AI - Simulated Compute Operations

Drop-in replacement for real GKE/Compute operations
that applies changes to the pipeline simulator instead.
"""

from typing import Any
from src.simulator import PipelineSimulator
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class SimulatedComputeOperations:
    """Simulated GKE and Compute operations backed by the simulator."""

    def __init__(self, simulator: PipelineSimulator):
        self.simulator = simulator

    async def scale_node_pool(
        self,
        cluster_name: str,
        node_pool_name: str,
        target_size: int,
    ) -> dict[str, Any]:
        """Simulate scaling a node pool."""
        logger.info(
            "⚡ Simulated: Scaling node pool",
            cluster=cluster_name,
            pool=node_pool_name,
            target=target_size,
        )
        result = self.simulator.apply_remediation(
            "scale_node_pool", {"target_size": target_size}
        )
        return {
            "action": "scale_node_pool",
            "status": "initiated",
            "operation_name": f"operation-scale-{target_size}",
            "target_size": target_size,
            "simulated": True,
        }

    async def restart_workload(
        self,
        cluster_name: str,
        namespace: str,
        deployment_name: str,
    ) -> dict[str, Any]:
        """Simulate restarting a deployment."""
        logger.info(
            "⚡ Simulated: Restarting workload",
            cluster=cluster_name,
            namespace=namespace,
            deployment=deployment_name,
        )
        self.simulator.apply_remediation("restart_workload")
        return {
            "action": "restart_workload",
            "status": "success",
            "deployment": deployment_name,
            "output": f"deployment.apps/{deployment_name} restarted",
            "simulated": True,
        }

    async def resize_disk(
        self,
        instance_name: str,
        disk_name: str,
        new_size_gb: int,
    ) -> dict[str, Any]:
        """Simulate resizing a disk."""
        logger.info(
            "⚡ Simulated: Resizing disk",
            instance=instance_name,
            disk=disk_name,
            new_size=new_size_gb,
        )
        self.simulator.apply_remediation("resize_disk", {"new_size_gb": new_size_gb})
        return {
            "action": "resize_disk",
            "status": "initiated",
            "disk": disk_name,
            "new_size_gb": new_size_gb,
            "simulated": True,
        }

    async def drain_and_replace_node(
        self,
        cluster_name: str,
        node_name: str,
    ) -> dict[str, Any]:
        """Simulate draining and replacing a node."""
        logger.info(
            "⚡ Simulated: Draining node",
            cluster=cluster_name,
            node=node_name,
        )
        self.simulator.apply_remediation("drain_and_replace_node")
        return {
            "action": "drain_and_replace_node",
            "status": "success",
            "node": node_name,
            "output": f"node/{node_name} drained and cordoned",
            "simulated": True,
        }
