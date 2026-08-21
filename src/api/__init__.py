"""StudioPulse AI - REST API Server

Provides a web API for:
- Viewing real-time pipeline metrics
- Triggering demo scenarios
- Viewing incident history
- Health checks
"""

import asyncio
import os
from aiohttp import web
from typing import Any
from src.simulator import PipelineSimulator
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class APIServer:
    """REST API server for StudioPulse AI web dashboard."""

    def __init__(self, simulator: PipelineSimulator, orchestrator=None):
        self.simulator = simulator
        self.orchestrator = orchestrator
        self.app = web.Application()
        self._setup_routes()
        self._incident_log: list[dict[str, Any]] = []

    def _setup_routes(self):
        """Register API routes."""
        self.app.router.add_get("/", self._index)
        self.app.router.add_get("/api/health", self._health)
        self.app.router.add_get("/api/metrics", self._get_metrics)
        self.app.router.add_get("/api/alerts", self._get_alerts)
        self.app.router.add_get("/api/jobs", self._get_jobs)
        self.app.router.add_get("/api/incidents", self._get_incidents)
        self.app.router.add_get("/api/status", self._get_status)
        self.app.router.add_post("/api/trigger", self._trigger_scenario)

    async def _index(self, request: web.Request) -> web.Response:
        """Serve the dashboard HTML."""
        # Try multiple paths to find the dashboard
        possible_paths = [
            os.path.join(os.path.dirname(__file__), "..", "dashboard", "index.html"),
            os.path.join(os.getcwd(), "src", "dashboard", "index.html"),
            "src/dashboard/index.html",
        ]
        for path in possible_paths:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    html = f.read()
                return web.Response(text=html, content_type="text/html")
            except FileNotFoundError:
                continue

        return web.Response(
            text="<h1>StudioPulse AI</h1><p>Dashboard file not found. API is running at /api/health</p>",
            content_type="text/html",
        )

    async def _health(self, request: web.Request) -> web.Response:
        """Health check endpoint."""
        return web.json_response({
            "status": "healthy",
            "service": "studiopulse-ai",
            "version": "1.0.0",
            "mode": "demo",
        })

    async def _get_metrics(self, request: web.Request) -> web.Response:
        """Get current pipeline metrics."""
        metrics = self.simulator.get_current_metrics()
        return web.json_response(metrics)

    async def _get_alerts(self, request: web.Request) -> web.Response:
        """Get active alerts."""
        alerts = self.simulator.get_alerts_as_grafana_format()
        return web.json_response({"alerts": alerts, "count": len(alerts)})

    async def _get_jobs(self, request: web.Request) -> web.Response:
        """Get render job status."""
        jobs = self.simulator.get_render_jobs()
        return web.json_response({"jobs": jobs})

    async def _get_incidents(self, request: web.Request) -> web.Response:
        """Get incident history."""
        return web.json_response({"incidents": self._incident_log})

    async def _get_status(self, request: web.Request) -> web.Response:
        """Get orchestrator status."""
        if self.orchestrator:
            status = self.orchestrator.get_status()
        else:
            status = {"message": "Orchestrator not connected"}
        return web.json_response(status)

    async def _trigger_scenario(self, request: web.Request) -> web.Response:
        """Trigger a failure scenario for demo."""
        try:
            data = await request.json() if request.can_read_body else {}
        except Exception:
            data = {}

        scenario_name = data.get("scenario")

        alert = await self.simulator.trigger_scenario(scenario_name)

        incident = {
            "alert_id": alert.uid,
            "title": alert.title,
            "scenario": scenario_name or "random",
            "status": "triggered",
            "timestamp": __import__("time").time(),
        }
        self._incident_log.append(incident)

        return web.json_response({
            "status": "triggered",
            "alert": {
                "uid": alert.uid,
                "title": alert.title,
                "severity": alert.severity,
            },
        })

    def log_incident(self, incident: dict[str, Any]):
        """Log an incident from the orchestrator."""
        self._incident_log.append(incident)

    async def start(self, host: str = "0.0.0.0", port: int = 8080):
        """Start the API server."""
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, host, port)
        await site.start()
        logger.info(f"🌐 API Server running at http://{host}:{port}")
        return runner
