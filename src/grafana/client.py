"""StudioPulse AI - Grafana API Client"""

import httpx
from typing import Any
from src.utils.config import load_config
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class GrafanaClient:
    """Client for interacting with Grafana APIs."""

    def __init__(self):
        config = load_config()
        self.base_url = config.grafana.url.rstrip("/")
        self.headers = {
            "Authorization": f"Bearer {config.grafana.api_key}",
            "Content-Type": "application/json",
        }
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            headers=self.headers,
            timeout=30.0,
        )

    async def get_alerts(self, state: str = "firing") -> list[dict[str, Any]]:
        """Fetch current alerts from Grafana.

        Args:
            state: Alert state filter (firing, pending, inactive)

        Returns:
            List of alert objects
        """
        logger.info("Fetching Grafana alerts", state=state)
        response = await self._client.get(
            "/api/v1/provisioning/alert-rules"
        )
        response.raise_for_status()
        alerts = response.json()

        # Filter by state if applicable
        if state:
            alerts = [a for a in alerts if a.get("state", "") == state]

        logger.info("Fetched alerts", count=len(alerts))
        return alerts

    async def query_datasource(
        self,
        datasource_uid: str,
        query: str,
        from_time: str = "now-1h",
        to_time: str = "now",
    ) -> dict[str, Any]:
        """Execute a query against a Grafana datasource.

        Args:
            datasource_uid: UID of the datasource
            query: PromQL or datasource-specific query
            from_time: Start time (relative or absolute)
            to_time: End time (relative or absolute)

        Returns:
            Query results
        """
        logger.info(
            "Querying datasource",
            datasource_uid=datasource_uid,
            query=query,
        )
        payload = {
            "queries": [
                {
                    "datasource": {"uid": datasource_uid},
                    "expr": query,
                    "refId": "A",
                }
            ],
            "from": from_time,
            "to": to_time,
        }
        response = await self._client.post("/api/ds/query", json=payload)
        response.raise_for_status()
        return response.json()

    async def get_dashboard(self, uid: str) -> dict[str, Any]:
        """Fetch a dashboard by UID.

        Args:
            uid: Dashboard UID

        Returns:
            Dashboard JSON model
        """
        response = await self._client.get(f"/api/dashboards/uid/{uid}")
        response.raise_for_status()
        return response.json()

    async def get_annotations(
        self,
        from_time: int,
        to_time: int,
        dashboard_id: int | None = None,
    ) -> list[dict[str, Any]]:
        """Fetch annotations (events/incidents) from Grafana.

        Args:
            from_time: Start timestamp (epoch ms)
            to_time: End timestamp (epoch ms)
            dashboard_id: Optional dashboard filter

        Returns:
            List of annotation objects
        """
        params: dict[str, Any] = {"from": from_time, "to": to_time}
        if dashboard_id:
            params["dashboardId"] = dashboard_id

        response = await self._client.get("/api/annotations", params=params)
        response.raise_for_status()
        return response.json()

    async def create_annotation(
        self,
        text: str,
        tags: list[str] | None = None,
        dashboard_id: int | None = None,
    ) -> dict[str, Any]:
        """Create an annotation in Grafana for incident tracking.

        Args:
            text: Annotation text
            tags: Optional tags for categorization
            dashboard_id: Optional dashboard to attach to

        Returns:
            Created annotation object
        """
        payload: dict[str, Any] = {"text": text}
        if tags:
            payload["tags"] = tags
        if dashboard_id:
            payload["dashboardId"] = dashboard_id

        response = await self._client.post("/api/annotations", json=payload)
        response.raise_for_status()
        logger.info("Created annotation", text=text)
        return response.json()

    async def close(self):
        """Close the HTTP client."""
        await self._client.aclose()
