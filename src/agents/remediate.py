"""StudioPulse AI - Remediate Agent

This agent takes diagnosis results and executes remediation actions
to resolve pipeline incidents autonomously.
"""

from __future__ import annotations

import asyncio
from typing import Any
from src.grafana.dashboards import DashboardQuerier
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


# Available remediation actions
AVAILABLE_ACTIONS = [
    "scale_node_pool",
    "restart_workload",
    "resize_disk",
    "drain_and_replace_node",
    "reprioritize_queue",
    "clear_cache",
    "escalate_to_human",
]


class RemediateAgent:
    """Agent responsible for executing remediation actions.

    Takes diagnosis results, plans remediation using Gemini,
    executes actions, and verifies resolution.
    """

    def __init__(
        self,
        gemini_agent: Any,
        compute_ops: Any,
        grafana_client: Any,
        dashboard_querier: DashboardQuerier,
    ):
        self.gemini = gemini_agent
        self.compute = compute_ops
        self.grafana = grafana_client
        self.dashboard_querier = dashboard_querier

    async def remediate(self, diagnosis_result: dict[str, Any]) -> dict[str, Any]:
        """Execute remediation based on diagnosis.

        Steps:
        1. Plan remediation steps using Gemini
        2. Execute each step in order
        3. Wait for stabilization
        4. Verify resolution
        5. Create incident annotation in Grafana

        Args:
            diagnosis_result: Output from DiagnoseAgent

        Returns:
            Remediation result with status and summary
        """
        alert = diagnosis_result["alert"]
        diagnosis = diagnosis_result["diagnosis"]

        logger.info(
            "Starting remediation",
            alert_id=alert.alert_id,
            root_cause=diagnosis.get("diagnosis", {}).get("root_cause"),
        )

        # Step 1: Plan remediation
        plan = await self.gemini.plan_remediation(
            diagnosis=diagnosis,
            available_actions=AVAILABLE_ACTIONS,
        )

        if "error" in plan:
            logger.error("Failed to create remediation plan", error=plan["error"])
            return {"status": "failed", "reason": "planning_failed", "plan": plan}

        logger.info(
            "Remediation plan created",
            steps=len(plan.get("steps", [])),
            estimated_time=plan.get("estimated_resolution_time"),
        )

        # Step 2: Execute remediation steps
        execution_results = []
        for step in plan.get("steps", []):
            result = await self._execute_step(step)
            execution_results.append(result)

            if result.get("status") == "failed":
                logger.warning(
                    "Step failed",
                    step=step.get("action"),
                )
                break

        # Step 3: Wait for stabilization
        stabilization_time = 5  # seconds (shorter for demo)
        logger.info("⏳ Waiting for stabilization...", seconds=stabilization_time)
        await asyncio.sleep(stabilization_time)

        # Step 4: Verify resolution
        post_fix_metrics = await self.dashboard_querier.get_correlated_metrics(
            category=alert.category.value
        )

        verification = await self.gemini.verify_resolution(
            original_alert={
                "title": alert.title,
                "category": alert.category.value,
                "metrics": diagnosis_result["metrics_snapshot"],
            },
            post_fix_metrics=post_fix_metrics,
        )

        # Step 5: Create incident annotation in Grafana
        resolved = verification.get("resolved", False)
        annotation_text = (
            f"🤖 StudioPulse AI - Incident {'Resolved ✅' if resolved else 'Requires Attention ⚠️'}\n"
            f"Alert: {alert.title}\n"
            f"Root Cause: {diagnosis.get('diagnosis', {}).get('root_cause', 'Unknown')}\n"
            f"Actions Taken: {', '.join(s.get('action', '') for s in plan.get('steps', []))}\n"
            f"Resolution: {verification.get('summary', 'N/A')}"
        )

        await self.grafana.create_annotation(
            text=annotation_text,
            tags=["studiopulse", "auto-remediation", alert.category.value],
        )

        status = "resolved" if resolved else "requires_attention"
        logger.info(f"{'✅' if resolved else '⚠️'} Remediation {status}")

        return {
            "status": status,
            "alert_id": alert.alert_id,
            "plan": plan,
            "execution_results": execution_results,
            "verification": verification,
            "annotation_created": True,
        }

    async def _execute_step(self, step: dict[str, Any]) -> dict[str, Any]:
        """Execute a single remediation step."""
        action = step.get("action", "")
        params = step.get("parameters", {})

        logger.info(f"⚡ Executing: {action}", params=params)

        try:
            if action == "scale_node_pool":
                return await self.compute.scale_node_pool(
                    cluster_name=params.get("cluster_name", "render-cluster"),
                    node_pool_name=params.get("node_pool_name", "gpu-pool"),
                    target_size=params.get("target_size", 5),
                )
            elif action == "restart_workload":
                return await self.compute.restart_workload(
                    cluster_name=params.get("cluster_name", "render-cluster"),
                    namespace=params.get("namespace", "render"),
                    deployment_name=params.get("deployment_name", "render-worker"),
                )
            elif action == "resize_disk":
                return await self.compute.resize_disk(
                    instance_name=params.get("instance_name", "render-node-1"),
                    disk_name=params.get("disk_name", "render-data"),
                    new_size_gb=params.get("new_size_gb", 500),
                )
            elif action == "drain_and_replace_node":
                return await self.compute.drain_and_replace_node(
                    cluster_name=params.get("cluster_name", "render-cluster"),
                    node_name=params.get("node_name", ""),
                )
            elif action == "escalate_to_human":
                logger.warning("🚨 Escalating to human operator", reason=params.get("reason"))
                return {"action": "escalate", "status": "escalated", "reason": params.get("reason")}
            else:
                logger.warning("Unknown action", action=action)
                return {"action": action, "status": "skipped", "reason": "unknown_action"}

        except Exception as e:
            logger.error("Step execution failed", action=action, error=str(e))
            return {"action": action, "status": "failed", "error": str(e)}
