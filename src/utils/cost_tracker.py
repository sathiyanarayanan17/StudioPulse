"""StudioPulse AI - Cost Tracker

Estimates cost savings from automated incident resolution vs manual resolution.
Assumes:
- $500/hour engineer cost (configurable)
- 45 min average manual resolution time (configurable)
- Tracks cumulative savings per session and historically
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

from src.utils.logger import setup_logger

logger = setup_logger(__name__)


@dataclass
class ResolutionEvent:
    """A single resolution event for cost tracking."""
    incident_id: str
    title: str
    auto_resolution_seconds: float
    timestamp: float = field(default_factory=time.time)
    scenario: str = ""
    remediation_action: str = ""


class CostTracker:
    """Estimates and tracks cost savings from automated incident resolution.

    Calculates savings based on the difference between manual resolution time
    (average 45 minutes by a $500/hour engineer) and automated resolution time.
    """

    def __init__(
        self,
        engineer_hourly_rate: float = 500.0,
        avg_manual_resolution_minutes: float = 45.0,
    ):
        """Initialize the cost tracker.

        Args:
            engineer_hourly_rate: Cost per hour for an on-call engineer ($)
            avg_manual_resolution_minutes: Average time for manual resolution (minutes)
        """
        self.engineer_hourly_rate = engineer_hourly_rate
        self.avg_manual_resolution_minutes = avg_manual_resolution_minutes
        self._events: list[ResolutionEvent] = []

    @property
    def cost_per_minute(self) -> float:
        """Cost per minute of engineer time."""
        return self.engineer_hourly_rate / 60.0

    @property
    def manual_cost_per_incident(self) -> float:
        """Estimated cost of manual resolution per incident."""
        return self.cost_per_minute * self.avg_manual_resolution_minutes

    def record_resolution(
        self,
        incident_id: str,
        title: str,
        auto_resolution_seconds: float,
        scenario: str = "",
        remediation_action: str = "",
    ) -> dict[str, Any]:
        """Record an automated resolution and calculate savings.

        Args:
            incident_id: Unique incident ID
            title: Incident title
            auto_resolution_seconds: Time taken by automated resolution
            scenario: Scenario type (e.g. gpu_saturation)
            remediation_action: Action that was taken

        Returns:
            Dictionary with cost analysis for this resolution
        """
        event = ResolutionEvent(
            incident_id=incident_id,
            title=title,
            auto_resolution_seconds=auto_resolution_seconds,
            scenario=scenario,
            remediation_action=remediation_action,
        )
        self._events.append(event)

        analysis = self._calculate_savings(event)

        logger.info(
            "Cost savings recorded",
            incident_id=incident_id,
            savings=f"${analysis['savings_dollars']:.2f}",
            auto_time=f"{analysis['auto_resolution_minutes']:.1f}min",
            manual_time=f"{self.avg_manual_resolution_minutes:.0f}min",
        )

        return analysis

    def _calculate_savings(self, event: ResolutionEvent) -> dict[str, Any]:
        """Calculate cost savings for a single resolution event.

        Args:
            event: The resolution event

        Returns:
            Cost analysis dictionary
        """
        auto_minutes = event.auto_resolution_seconds / 60.0
        auto_cost = auto_minutes * self.cost_per_minute

        manual_cost = self.manual_cost_per_incident
        savings = manual_cost - auto_cost
        time_saved_minutes = self.avg_manual_resolution_minutes - auto_minutes

        return {
            "incident_id": event.incident_id,
            "title": event.title,
            "auto_resolution_minutes": round(auto_minutes, 2),
            "manual_resolution_minutes": self.avg_manual_resolution_minutes,
            "time_saved_minutes": round(max(0, time_saved_minutes), 2),
            "auto_cost_dollars": round(auto_cost, 2),
            "manual_cost_dollars": round(manual_cost, 2),
            "savings_dollars": round(max(0, savings), 2),
            "savings_percent": round(max(0, savings) / manual_cost * 100, 1) if manual_cost > 0 else 0,
            "timestamp": event.timestamp,
        }

    def get_total_savings(self) -> dict[str, Any]:
        """Get cumulative cost savings summary.

        Returns:
            Dictionary with total savings, event count, and averages
        """
        if not self._events:
            return {
                "total_incidents_resolved": 0,
                "total_savings_dollars": 0.0,
                "total_time_saved_minutes": 0.0,
                "total_manual_cost_dollars": 0.0,
                "avg_resolution_seconds": 0.0,
                "avg_savings_per_incident": 0.0,
                "engineer_hourly_rate": self.engineer_hourly_rate,
                "avg_manual_resolution_minutes": self.avg_manual_resolution_minutes,
            }

        total_auto_seconds = sum(e.auto_resolution_seconds for e in self._events)
        total_auto_minutes = total_auto_seconds / 60.0
        total_manual_minutes = self.avg_manual_resolution_minutes * len(self._events)
        total_manual_cost = self.manual_cost_per_incident * len(self._events)
        total_auto_cost = total_auto_minutes * self.cost_per_minute
        total_savings = total_manual_cost - total_auto_cost
        total_time_saved = total_manual_minutes - total_auto_minutes

        return {
            "total_incidents_resolved": len(self._events),
            "total_savings_dollars": round(max(0, total_savings), 2),
            "total_time_saved_minutes": round(max(0, total_time_saved), 2),
            "total_time_saved_hours": round(max(0, total_time_saved) / 60, 2),
            "total_manual_cost_dollars": round(total_manual_cost, 2),
            "total_auto_cost_dollars": round(total_auto_cost, 2),
            "avg_resolution_seconds": round(total_auto_seconds / len(self._events), 1),
            "avg_savings_per_incident": round(max(0, total_savings) / len(self._events), 2),
            "engineer_hourly_rate": self.engineer_hourly_rate,
            "avg_manual_resolution_minutes": self.avg_manual_resolution_minutes,
            "roi_multiplier": round(total_manual_cost / max(1, total_auto_cost), 1),
        }

    def get_event_history(self) -> list[dict[str, Any]]:
        """Get detailed history of all resolution events with cost analysis.

        Returns:
            List of cost analysis dictionaries for each event
        """
        return [self._calculate_savings(event) for event in self._events]

    def get_savings_by_scenario(self) -> dict[str, dict[str, Any]]:
        """Get savings breakdown by scenario type.

        Returns:
            Dictionary mapping scenario names to their aggregate savings
        """
        scenarios: dict[str, list[ResolutionEvent]] = {}
        for event in self._events:
            key = event.scenario or "unknown"
            if key not in scenarios:
                scenarios[key] = []
            scenarios[key].append(event)

        result = {}
        for scenario_name, events in scenarios.items():
            total_auto_seconds = sum(e.auto_resolution_seconds for e in events)
            total_manual_cost = self.manual_cost_per_incident * len(events)
            total_auto_cost = (total_auto_seconds / 60.0) * self.cost_per_minute
            savings = total_manual_cost - total_auto_cost

            result[scenario_name] = {
                "count": len(events),
                "total_savings_dollars": round(max(0, savings), 2),
                "avg_resolution_seconds": round(total_auto_seconds / len(events), 1),
            }

        return result

    def format_summary_text(self) -> str:
        """Generate a human-readable cost savings summary.

        Returns:
            Formatted string with cost savings information
        """
        stats = self.get_total_savings()

        if stats["total_incidents_resolved"] == 0:
            return "No incidents resolved yet. Cost savings will be tracked as incidents are auto-resolved."

        lines = [
            "╔══════════════════════════════════════════════╗",
            "║        💰 COST SAVINGS SUMMARY              ║",
            "╠══════════════════════════════════════════════╣",
            f"║  Incidents Auto-Resolved: {stats['total_incidents_resolved']:>14}   ║",
            f"║  Total $ Saved:         ${stats['total_savings_dollars']:>12,.2f}   ║",
            f"║  Time Saved:            {stats['total_time_saved_hours']:>10,.1f} hrs   ║",
            f"║  Avg Resolution Time:   {stats['avg_resolution_seconds']:>10,.0f} sec   ║",
            f"║  ROI Multiplier:        {stats.get('roi_multiplier', 0):>12,.1f}x   ║",
            "╠══════════════════════════════════════════════╣",
            f"║  Engineer Rate: ${self.engineer_hourly_rate:.0f}/hr               ║",
            f"║  Manual Resolution: {self.avg_manual_resolution_minutes:.0f} min avg         ║",
            "╚══════════════════════════════════════════════╝",
        ]
        return "\n".join(lines)
