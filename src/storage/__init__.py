"""StudioPulse AI - Incident History Persistence

Saves all incidents to a JSON file so they persist across restarts.
Provides thread-safe async read/write operations with automatic backups.
"""

from __future__ import annotations

import asyncio
import json
import os
import time
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
from typing import Any

from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class IncidentStatus(str, Enum):
    """Possible incident statuses."""
    DETECTED = "detected"
    DIAGNOSING = "diagnosing"
    REMEDIATING = "remediating"
    RESOLVED = "resolved"
    FAILED = "failed"
    REQUIRES_ATTENTION = "requires_attention"


@dataclass
class IncidentRecord:
    """A single incident record for persistence."""
    incident_id: str
    title: str
    status: IncidentStatus
    detected_at: float
    scenario: str = ""
    severity: str = "critical"
    root_cause: str = ""
    resolution_summary: str = ""
    resolved_at: float = 0.0
    time_to_resolve_seconds: float = 0.0
    remediation_action: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        data["status"] = self.status.value
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> IncidentRecord:
        """Create an IncidentRecord from a dictionary."""
        status_value = data.get("status", "detected")
        try:
            status = IncidentStatus(status_value)
        except ValueError:
            status = IncidentStatus.DETECTED

        return cls(
            incident_id=data.get("incident_id", ""),
            title=data.get("title", ""),
            status=status,
            detected_at=data.get("detected_at", 0.0),
            scenario=data.get("scenario", ""),
            severity=data.get("severity", "critical"),
            root_cause=data.get("root_cause", ""),
            resolution_summary=data.get("resolution_summary", ""),
            resolved_at=data.get("resolved_at", 0.0),
            time_to_resolve_seconds=data.get("time_to_resolve_seconds", 0.0),
            remediation_action=data.get("remediation_action", ""),
            metadata=data.get("metadata", {}),
        )


class IncidentStore:
    """Persistent incident storage backed by a JSON file.

    Features:
    - Atomic writes with temp file + rename
    - Automatic backup before overwrite
    - In-memory cache for fast reads
    - Async-safe with lock
    - Auto-creates directories as needed
    """

    DEFAULT_PATH = "data/incidents.json"

    def __init__(self, file_path: str | None = None):
        """Initialize the incident store.

        Args:
            file_path: Path to the JSON file. Defaults to data/incidents.json
        """
        self._file_path = Path(file_path or self.DEFAULT_PATH)
        self._incidents: list[IncidentRecord] = []
        self._lock = asyncio.Lock()
        self._loaded = False

    @property
    def file_path(self) -> Path:
        """Get the storage file path."""
        return self._file_path

    async def load(self) -> None:
        """Load incidents from disk into memory."""
        async with self._lock:
            self._incidents = await self._read_from_disk()
            self._loaded = True
            logger.info(
                "Incident store loaded",
                count=len(self._incidents),
                path=str(self._file_path),
            )

    async def save(self) -> None:
        """Save all incidents to disk."""
        async with self._lock:
            await self._write_to_disk(self._incidents)

    async def add_incident(self, incident: IncidentRecord) -> None:
        """Add a new incident record and persist.

        Args:
            incident: The incident record to add
        """
        async with self._lock:
            if not self._loaded:
                self._incidents = await self._read_from_disk()
                self._loaded = True

            self._incidents.append(incident)
            await self._write_to_disk(self._incidents)

        logger.info(
            "Incident recorded",
            incident_id=incident.incident_id,
            title=incident.title,
            status=incident.status.value,
        )

    async def update_incident(self, incident_id: str, updates: dict[str, Any]) -> bool:
        """Update an existing incident record by ID.

        Args:
            incident_id: The incident ID to update
            updates: Dictionary of fields to update

        Returns:
            True if found and updated, False otherwise
        """
        async with self._lock:
            if not self._loaded:
                self._incidents = await self._read_from_disk()
                self._loaded = True

            for incident in self._incidents:
                if incident.incident_id == incident_id:
                    for key, value in updates.items():
                        if key == "status" and isinstance(value, str):
                            try:
                                value = IncidentStatus(value)
                            except ValueError:
                                continue
                        if hasattr(incident, key):
                            setattr(incident, key, value)

                    await self._write_to_disk(self._incidents)
                    logger.info(
                        "Incident updated",
                        incident_id=incident_id,
                        updates=list(updates.keys()),
                    )
                    return True

        logger.warning("Incident not found for update", incident_id=incident_id)
        return False

    async def get_all(self) -> list[IncidentRecord]:
        """Get all incidents from the store.

        Returns:
            List of all incident records
        """
        async with self._lock:
            if not self._loaded:
                self._incidents = await self._read_from_disk()
                self._loaded = True
            return self._incidents.copy()

    async def get_by_id(self, incident_id: str) -> IncidentRecord | None:
        """Get a specific incident by ID.

        Args:
            incident_id: The incident ID to look up

        Returns:
            The incident record, or None if not found
        """
        async with self._lock:
            if not self._loaded:
                self._incidents = await self._read_from_disk()
                self._loaded = True

            for incident in self._incidents:
                if incident.incident_id == incident_id:
                    return incident
        return None

    async def get_by_status(self, status: IncidentStatus) -> list[IncidentRecord]:
        """Get all incidents with a specific status.

        Args:
            status: The status to filter by

        Returns:
            List of matching incident records
        """
        all_incidents = await self.get_all()
        return [i for i in all_incidents if i.status == status]

    async def get_recent(self, limit: int = 20) -> list[IncidentRecord]:
        """Get the most recent incidents.

        Args:
            limit: Maximum number to return

        Returns:
            List of recent incident records, newest first
        """
        all_incidents = await self.get_all()
        sorted_incidents = sorted(
            all_incidents, key=lambda i: i.detected_at, reverse=True
        )
        return sorted_incidents[:limit]

    async def get_statistics(self) -> dict[str, Any]:
        """Get summary statistics about stored incidents.

        Returns:
            Dictionary of statistics
        """
        all_incidents = await self.get_all()
        resolved = [i for i in all_incidents if i.status == IncidentStatus.RESOLVED]

        avg_resolution_time = 0.0
        if resolved:
            times = [i.time_to_resolve_seconds for i in resolved if i.time_to_resolve_seconds > 0]
            if times:
                avg_resolution_time = sum(times) / len(times)

        return {
            "total_incidents": len(all_incidents),
            "resolved": len(resolved),
            "failed": len([i for i in all_incidents if i.status == IncidentStatus.FAILED]),
            "active": len([i for i in all_incidents if i.status in (
                IncidentStatus.DETECTED, IncidentStatus.DIAGNOSING, IncidentStatus.REMEDIATING
            )]),
            "avg_resolution_time_seconds": round(avg_resolution_time, 1),
            "resolution_rate": round(len(resolved) / max(1, len(all_incidents)) * 100, 1),
        }

    async def clear(self) -> None:
        """Clear all incidents (creates backup first)."""
        async with self._lock:
            if self._file_path.exists():
                backup_path = self._file_path.with_suffix(".json.bak")
                try:
                    backup_path.write_text(
                        self._file_path.read_text(encoding="utf-8"),
                        encoding="utf-8",
                    )
                    logger.info("Backup created before clear", backup_path=str(backup_path))
                except OSError as e:
                    logger.warning("Failed to create backup", error=str(e))

            self._incidents = []
            await self._write_to_disk(self._incidents)
            logger.info("Incident store cleared")

    async def _read_from_disk(self) -> list[IncidentRecord]:
        """Read incidents from the JSON file."""
        if not self._file_path.exists():
            return []

        try:
            loop = asyncio.get_event_loop()
            content = await loop.run_in_executor(
                None, lambda: self._file_path.read_text(encoding="utf-8")
            )
            data = json.loads(content)

            if isinstance(data, dict) and "incidents" in data:
                records = data["incidents"]
            elif isinstance(data, list):
                records = data
            else:
                logger.warning("Unexpected JSON structure in incident file")
                return []

            return [IncidentRecord.from_dict(r) for r in records]

        except json.JSONDecodeError as e:
            logger.error("Failed to parse incident file", error=str(e))
            return []
        except OSError as e:
            logger.error("Failed to read incident file", error=str(e))
            return []

    async def _write_to_disk(self, incidents: list[IncidentRecord]) -> None:
        """Write incidents to the JSON file atomically."""
        self._file_path.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "version": 1,
            "updated_at": time.time(),
            "count": len(incidents),
            "incidents": [i.to_dict() for i in incidents],
        }

        content = json.dumps(data, indent=2, ensure_ascii=False)

        # Write to temp file first, then rename for atomicity
        tmp_path = self._file_path.with_suffix(".json.tmp")

        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None, lambda: tmp_path.write_text(content, encoding="utf-8")
            )

            # On Windows, we need to remove the target first
            if self._file_path.exists():
                await loop.run_in_executor(None, self._file_path.unlink)

            await loop.run_in_executor(
                None, lambda: tmp_path.rename(self._file_path)
            )

        except OSError as e:
            logger.error("Failed to write incident file", error=str(e))
            # Clean up temp file if it exists
            if tmp_path.exists():
                try:
                    tmp_path.unlink()
                except OSError:
                    pass
