"""StudioPulse AI - Vertex AI / Gemini Integration"""

import vertexai
from vertexai.generative_models import GenerativeModel, Part
from typing import Any
from src.utils.config import load_config
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class GeminiAgent:
    """Wrapper for Google Gemini via Vertex AI for agent reasoning."""

    def __init__(self):
        config = load_config()
        vertexai.init(
            project=config.google_cloud.project_id,
            location=config.google_cloud.vertex_ai_location,
        )
        self.model = GenerativeModel(
            model_name=config.agent.gemini_model,
            system_instruction=self._get_system_instruction(),
        )
        self._chat = None

    def _get_system_instruction(self) -> str:
        return """You are StudioPulse AI, an expert Site Reliability Engineer (SRE) 
specialized in media rendering pipelines and VFX production infrastructure.

Your role is to:
1. Analyze alerts and metrics from Grafana to understand infrastructure issues
2. Diagnose root causes by correlating multiple signals
3. Recommend and execute remediation actions
4. Verify that fixes resolved the issue

You have deep knowledge of:
- GPU rendering pipelines (NVIDIA, AMD)
- Kubernetes (GKE) orchestration
- Cloud infrastructure (Google Cloud)
- Media encoding/transcoding workflows
- Queue-based job scheduling systems

Always provide structured, actionable responses. When diagnosing, list:
- Observed symptoms
- Probable root cause(s) ranked by likelihood
- Recommended actions with expected impact
- Risk assessment of each action
"""

    async def analyze_alert(self, alert_context: dict[str, Any]) -> dict[str, Any]:
        """Use Gemini to analyze an alert and provide diagnosis.

        Args:
            alert_context: Alert data with correlated metrics

        Returns:
            Structured analysis with diagnosis and recommendations
        """
        prompt = f"""Analyze the following infrastructure alert and correlated metrics 
from our media rendering pipeline:

ALERT:
- Title: {alert_context.get('title', 'Unknown')}
- Severity: {alert_context.get('severity', 'Unknown')}
- Category: {alert_context.get('category', 'Unknown')}
- Labels: {alert_context.get('labels', {})}

CORRELATED METRICS:
{alert_context.get('metrics', {})}

Provide your analysis in the following JSON format:
{{
    "diagnosis": {{
        "root_cause": "description of the most likely root cause",
        "confidence": 0.0-1.0,
        "contributing_factors": ["factor1", "factor2"]
    }},
    "recommendations": [
        {{
            "action": "description of action",
            "type": "scale|restart|reconfigure|escalate",
            "priority": 1-5,
            "risk": "low|medium|high",
            "expected_impact": "description"
        }}
    ],
    "requires_human": false,
    "explanation": "brief explanation for the incident report"
}}
"""
        logger.info("Sending analysis request to Gemini")
        response = await self._generate(prompt)
        return self._parse_json_response(response)

    async def plan_remediation(
        self,
        diagnosis: dict[str, Any],
        available_actions: list[str],
    ) -> dict[str, Any]:
        """Plan remediation steps based on diagnosis.

        Args:
            diagnosis: Output from analyze_alert
            available_actions: List of actions the system can perform

        Returns:
            Ordered remediation plan
        """
        prompt = f"""Based on this diagnosis, create an execution plan using only
the available actions:

DIAGNOSIS:
{diagnosis}

AVAILABLE ACTIONS:
{available_actions}

Return a JSON plan:
{{
    "steps": [
        {{
            "order": 1,
            "action": "action_name",
            "parameters": {{}},
            "rollback": "how to undo if it fails",
            "timeout_seconds": 60
        }}
    ],
    "estimated_resolution_time": "Xm",
    "confidence": 0.0-1.0
}}
"""
        logger.info("Planning remediation with Gemini")
        response = await self._generate(prompt)
        return self._parse_json_response(response)

    async def verify_resolution(
        self,
        original_alert: dict[str, Any],
        post_fix_metrics: dict[str, Any],
    ) -> dict[str, Any]:
        """Verify if remediation was successful.

        Args:
            original_alert: The original alert context
            post_fix_metrics: Metrics after remediation was applied

        Returns:
            Verification result
        """
        prompt = f"""Verify if the following remediation was successful by comparing
the original alert with current metrics:

ORIGINAL ALERT:
{original_alert}

POST-FIX METRICS:
{post_fix_metrics}

Return JSON:
{{
    "resolved": true/false,
    "confidence": 0.0-1.0,
    "remaining_issues": ["any remaining concerns"],
    "summary": "brief resolution summary"
}}
"""
        response = await self._generate(prompt)
        return self._parse_json_response(response)

    async def _generate(self, prompt: str) -> str:
        """Generate response from Gemini model."""
        response = self.model.generate_content(prompt)
        return response.text

    def _parse_json_response(self, response: str) -> dict[str, Any]:
        """Parse JSON from Gemini response, handling markdown code blocks."""
        import json

        # Strip markdown code block if present
        text = response.strip()
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]

        try:
            return json.loads(text.strip())
        except json.JSONDecodeError:
            logger.error("Failed to parse Gemini response as JSON", response=text[:200])
            return {"error": "Failed to parse response", "raw": text}
