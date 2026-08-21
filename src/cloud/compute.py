"""StudioPulse AI - GKE / Compute Engine Operations for Remediation"""

from google.cloud import compute_v1, container_v1
from typing import Any
from src.utils.config import load_config
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class ComputeOperations:
    """Handles GKE and Compute Engine operations for remediation."""

    def __init__(self):
        config = load_config()
        self.project_id = config.google_cloud.project_id
        self.region = config.google_cloud.region
        self.zone = f"{self.region}-a"
        self.gke_client = container_v1.ClusterManagerClient()
        self.instance_client = compute_v1.InstancesClient()

    async def scale_node_pool(
        self,
        cluster_name: str,
        node_pool_name: str,
        target_size: int,
    ) -> dict[str, Any]:
        """Scale a GKE node pool to handle increased load.

        Args:
            cluster_name: GKE cluster name
            node_pool_name: Node pool to scale
            target_size: Desired number of nodes

        Returns:
            Operation result
        """
        logger.info(
            "Scaling node pool",
            cluster=cluster_name,
            pool=node_pool_name,
            target=target_size,
        )

        name = (
            f"projects/{self.project_id}/locations/{self.region}/"
            f"clusters/{cluster_name}/nodePools/{node_pool_name}"
        )

        request = container_v1.SetNodePoolSizeRequest(
            name=name,
            node_count=target_size,
        )

        operation = self.gke_client.set_node_pool_size(request=request)

        return {
            "action": "scale_node_pool",
            "status": "initiated",
            "operation_name": operation.name if hasattr(operation, 'name') else "unknown",
            "target_size": target_size,
        }

    async def restart_workload(
        self,
        cluster_name: str,
        namespace: str,
        deployment_name: str,
    ) -> dict[str, Any]:
        """Restart a Kubernetes deployment (rolling restart).

        Args:
            cluster_name: GKE cluster name
            namespace: Kubernetes namespace
            deployment_name: Deployment to restart

        Returns:
            Operation result
        """
        logger.info(
            "Restarting workload",
            cluster=cluster_name,
            namespace=namespace,
            deployment=deployment_name,
        )

        # Use kubectl via subprocess for rolling restart
        import asyncio

        cmd = (
            f"kubectl rollout restart deployment/{deployment_name} "
            f"-n {namespace} --context gke_{self.project_id}_{self.region}_{cluster_name}"
        )

        proc = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()

        success = proc.returncode == 0
        return {
            "action": "restart_workload",
            "status": "success" if success else "failed",
            "deployment": deployment_name,
            "output": stdout.decode() if success else stderr.decode(),
        }

    async def resize_disk(
        self,
        instance_name: str,
        disk_name: str,
        new_size_gb: int,
    ) -> dict[str, Any]:
        """Resize a persistent disk to handle storage issues.

        Args:
            instance_name: VM instance name
            disk_name: Disk name to resize
            new_size_gb: New size in GB

        Returns:
            Operation result
        """
        logger.info(
            "Resizing disk",
            instance=instance_name,
            disk=disk_name,
            new_size=new_size_gb,
        )

        disk_client = compute_v1.DisksClient()
        request = compute_v1.ResizeDiskRequest(
            project=self.project_id,
            zone=self.zone,
            disk=disk_name,
            disks_resize_request_resource=compute_v1.DisksResizeRequest(
                size_gb=new_size_gb,
            ),
        )

        operation = disk_client.resize(request=request)

        return {
            "action": "resize_disk",
            "status": "initiated",
            "disk": disk_name,
            "new_size_gb": new_size_gb,
        }

    async def drain_and_replace_node(
        self,
        cluster_name: str,
        node_name: str,
    ) -> dict[str, Any]:
        """Drain a problematic node and let the autoscaler replace it.

        Args:
            cluster_name: GKE cluster name
            node_name: Node to drain

        Returns:
            Operation result
        """
        logger.info("Draining node", cluster=cluster_name, node=node_name)

        import asyncio

        cmd = (
            f"kubectl drain {node_name} --ignore-daemonsets --delete-emptydir-data "
            f"--context gke_{self.project_id}_{self.region}_{cluster_name}"
        )

        proc = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()

        return {
            "action": "drain_and_replace_node",
            "status": "success" if proc.returncode == 0 else "failed",
            "node": node_name,
            "output": stdout.decode() if proc.returncode == 0 else stderr.decode(),
        }
