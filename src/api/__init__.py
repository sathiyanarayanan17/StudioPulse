"""StudioPulse AI - REST API Server

Provides a web API for:
- Serving the React dashboard (built from studiopulse-ui)
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
        # API endpoints
        self.app.router.add_get("/api/health", self._health)
        self.app.router.add_get("/api/metrics", self._get_metrics)
        self.app.router.add_get("/api/alerts", self._get_alerts)
        self.app.router.add_get("/api/jobs", self._get_jobs)
        self.app.router.add_get("/api/incidents", self._get_incidents)
        self.app.router.add_get("/api/status", self._get_status)
        self.app.router.add_post("/api/trigger", self._trigger_scenario)

        # Serve React build (static files)
        dist_dir = self._find_dist_dir()
        if dist_dir:
            # Serve assets directory
            assets_dir = os.path.join(dist_dir, "assets")
            if os.path.isdir(assets_dir):
                self.app.router.add_static("/assets", assets_dir)

            # Serve index.html for all other routes (SPA fallback)
            self.app.router.add_get("/", self._serve_index)
            self.app.router.add_get("/{path:.*}", self._serve_index_fallback)
        else:
            self.app.router.add_get("/", self._serve_fallback_html)
            self.app.router.add_get("/{path:.*}", self._serve_fallback_html)

    def _find_dist_dir(self) -> str | None:
        """Find the React build dist directory."""
        possible_paths = [
            os.path.join(os.path.dirname(__file__), "..", "dashboard", "dist"),
            os.path.join(os.getcwd(), "src", "dashboard", "dist"),
            "src/dashboard/dist",
        ]
        for path in possible_paths:
            abs_path = os.path.abspath(path)
            if os.path.isdir(abs_path) and os.path.exists(os.path.join(abs_path, "index.html")):
                logger.info(f"📂 Serving React UI from: {abs_path}")
                return abs_path
        return None

    async def _serve_index(self, request: web.Request) -> web.Response:
        """Serve the React index.html."""
        dist_dir = self._find_dist_dir()
        if dist_dir:
            index_path = os.path.join(dist_dir, "index.html")
            with open(index_path, "r", encoding="utf-8") as f:
                return web.Response(text=f.read(), content_type="text/html")
        return await self._serve_fallback_html(request)

    async def _serve_index_fallback(self, request: web.Request) -> web.Response:
        """SPA fallback - serve index.html for unknown routes (except /api)."""
        path = request.match_info.get("path", "")
        if path.startswith("api/"):
            return web.Response(status=404, text="Not found")

        # Try to serve static file first
        dist_dir = self._find_dist_dir()
        if dist_dir:
            file_path = os.path.join(dist_dir, path)
            if os.path.isfile(file_path):
                content_type = "application/octet-stream"
                if path.endswith(".js"):
                    content_type = "application/javascript"
                elif path.endswith(".css"):
                    content_type = "text/css"
                elif path.endswith(".svg"):
                    content_type = "image/svg+xml"
                elif path.endswith(".png"):
                    content_type = "image/png"
                with open(file_path, "rb") as f:
                    return web.Response(body=f.read(), content_type=content_type)

            # Fallback to index.html for SPA routing
            return await self._serve_index(request)

        return await self._serve_fallback_html(request)

    async def _serve_fallback_html(self, request: web.Request) -> web.Response:
        """Serve a simple fallback if React build isn't available."""
        # Try the old dashboard HTML
        old_paths = [
            os.path.join(os.path.dirname(__file__), "..", "dashboard", "index.html"),
            os.path.join(os.getcwd(), "src", "dashboard", "index.html"),
        ]
        for path in old_paths:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return web.Response(text=f.read(), content_type="text/html")
            except FileNotFoundError:
                continue

        return web.Response(
            text="<h1>StudioPulse AI</h1><p>API is running at /api/health. Build the React UI with: cd src/dashboard && npm run build</p>",
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
