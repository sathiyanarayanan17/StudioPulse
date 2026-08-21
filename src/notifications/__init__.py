"""StudioPulse AI - Notification Module

Sends webhook/Slack notifications when incidents are detected and resolved.
Supports Slack incoming webhooks and generic webhook endpoints.
"""

from __future__ import annotations

import asyncio
import json
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

import aiohttp

from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class NotificationLevel(str, Enum):
    """Notification severity levels."""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    RESOLVED = "resolved"


@dataclass
class NotificationPayload:
    """Represents a notification to be sent."""
    title: str
    message: str
    level: NotificationLevel
    timestamp: float = field(default_factory=time.time)
    incident_id: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


class WebhookNotifier:
    """Sends notifications to Slack or generic webhook endpoints.

    Supports:
    - Slack incoming webhooks (auto-detected by URL)
    - Generic webhook endpoints (sends JSON POST)
    - Retry with exponential backoff
    - Notification history tracking
    """

    def __init__(
        self,
        webhook_url: str | None = None,
        slack_channel: str | None = None,
        max_retries: int = 3,
        timeout_seconds: int = 10,
    ):
        """Initialize the webhook notifier.

        Args:
            webhook_url: Webhook endpoint URL (Slack or generic)
            slack_channel: Optional Slack channel override
            max_retries: Maximum retry attempts for failed sends
            timeout_seconds: HTTP request timeout
        """
        self.webhook_url = webhook_url
        self.slack_channel = slack_channel
        self.max_retries = max_retries
        self.timeout_seconds = timeout_seconds
        self._session: aiohttp.ClientSession | None = None
        self._notification_history: list[dict[str, Any]] = []
        self._enabled = webhook_url is not None

    @property
    def is_enabled(self) -> bool:
        """Check if notifications are enabled."""
        return self._enabled

    @property
    def history(self) -> list[dict[str, Any]]:
        """Get notification history."""
        return self._notification_history.copy()

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create an aiohttp session."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.timeout_seconds)
            )
        return self._session

    def _is_slack_url(self) -> bool:
        """Check if the webhook URL is a Slack webhook."""
        if not self.webhook_url:
            return False
        return "hooks.slack.com" in self.webhook_url

    def _build_slack_payload(self, notification: NotificationPayload) -> dict[str, Any]:
        """Build a Slack-formatted message payload."""
        emoji_map = {
            NotificationLevel.INFO: ":information_source:",
            NotificationLevel.WARNING: ":warning:",
            NotificationLevel.CRITICAL: ":rotating_light:",
            NotificationLevel.RESOLVED: ":white_check_mark:",
        }

        color_map = {
            NotificationLevel.INFO: "#36a64f",
            NotificationLevel.WARNING: "#ff9900",
            NotificationLevel.CRITICAL: "#ff0000",
            NotificationLevel.RESOLVED: "#2eb886",
        }

        emoji = emoji_map.get(notification.level, ":bell:")
        color = color_map.get(notification.level, "#808080")

        fields = []
        if notification.incident_id:
            fields.append({
                "title": "Incident ID",
                "value": notification.incident_id,
                "short": True,
            })
        if notification.level:
            fields.append({
                "title": "Severity",
                "value": notification.level.value.upper(),
                "short": True,
            })
        for key, value in notification.metadata.items():
            fields.append({
                "title": key.replace("_", " ").title(),
                "value": str(value),
                "short": True,
            })

        payload: dict[str, Any] = {
            "text": f"{emoji} *StudioPulse AI* | {notification.title}",
            "attachments": [
                {
                    "color": color,
                    "text": notification.message,
                    "fields": fields,
                    "footer": "StudioPulse AI | Automated Pipeline Management",
                    "ts": int(notification.timestamp),
                }
            ],
        }

        if self.slack_channel:
            payload["channel"] = self.slack_channel

        return payload

    def _build_generic_payload(self, notification: NotificationPayload) -> dict[str, Any]:
        """Build a generic JSON webhook payload."""
        return {
            "event": "studiopulse_notification",
            "title": notification.title,
            "message": notification.message,
            "level": notification.level.value,
            "incident_id": notification.incident_id,
            "timestamp": notification.timestamp,
            "metadata": notification.metadata,
        }

    async def send(self, notification: NotificationPayload) -> bool:
        """Send a notification via webhook.

        Args:
            notification: The notification payload to send

        Returns:
            True if sent successfully, False otherwise
        """
        if not self._enabled or not self.webhook_url:
            logger.debug("Notifications disabled, skipping send")
            self._record_history(notification, success=False, reason="disabled")
            return False

        if self._is_slack_url():
            payload = self._build_slack_payload(notification)
        else:
            payload = self._build_generic_payload(notification)

        for attempt in range(1, self.max_retries + 1):
            try:
                session = await self._get_session()
                async with session.post(
                    self.webhook_url,
                    json=payload,
                    headers={"Content-Type": "application/json"},
                ) as response:
                    if response.status in (200, 201, 202, 204):
                        logger.info(
                            "Notification sent",
                            title=notification.title,
                            level=notification.level.value,
                        )
                        self._record_history(notification, success=True)
                        return True
                    else:
                        body = await response.text()
                        logger.warning(
                            "Webhook returned non-success status",
                            status=response.status,
                            body=body[:200],
                            attempt=attempt,
                        )
            except asyncio.TimeoutError:
                logger.warning(
                    "Webhook request timed out",
                    attempt=attempt,
                    url=self.webhook_url[:50],
                )
            except aiohttp.ClientError as e:
                logger.warning(
                    "Webhook request failed",
                    error=str(e),
                    attempt=attempt,
                )

            if attempt < self.max_retries:
                backoff = 2 ** (attempt - 1)
                await asyncio.sleep(backoff)

        logger.error(
            "Failed to send notification after retries",
            title=notification.title,
            max_retries=self.max_retries,
        )
        self._record_history(notification, success=False, reason="max_retries_exceeded")
        return False

    async def notify_incident_detected(
        self,
        incident_id: str,
        title: str,
        severity: str = "critical",
        details: str = "",
    ) -> bool:
        """Send a notification for a newly detected incident.

        Args:
            incident_id: Unique incident identifier
            title: Alert/incident title
            severity: Severity level
            details: Additional details about the incident

        Returns:
            True if sent successfully
        """
        level = NotificationLevel.CRITICAL if severity == "critical" else NotificationLevel.WARNING
        notification = NotificationPayload(
            title=f"Incident Detected: {title}",
            message=details or f"A {severity} incident has been detected in the rendering pipeline.",
            level=level,
            incident_id=incident_id,
            metadata={"severity": severity, "pipeline": "render-cluster"},
        )
        return await self.send(notification)

    async def notify_incident_resolved(
        self,
        incident_id: str,
        title: str,
        resolution_summary: str = "",
        time_to_resolve_seconds: float = 0,
    ) -> bool:
        """Send a notification for a resolved incident.

        Args:
            incident_id: Unique incident identifier
            title: Original alert/incident title
            resolution_summary: Summary of how it was resolved
            time_to_resolve_seconds: Time taken to resolve

        Returns:
            True if sent successfully
        """
        metadata: dict[str, Any] = {"pipeline": "render-cluster"}
        if time_to_resolve_seconds > 0:
            minutes = time_to_resolve_seconds / 60
            metadata["time_to_resolve"] = f"{minutes:.1f} minutes"

        notification = NotificationPayload(
            title=f"Incident Resolved: {title}",
            message=resolution_summary or "The incident has been automatically resolved by StudioPulse AI.",
            level=NotificationLevel.RESOLVED,
            incident_id=incident_id,
            metadata=metadata,
        )
        return await self.send(notification)

    async def notify_diagnosis_complete(
        self,
        incident_id: str,
        root_cause: str,
        confidence: float,
    ) -> bool:
        """Send a notification when diagnosis is complete.

        Args:
            incident_id: Unique incident identifier
            root_cause: Diagnosed root cause
            confidence: Confidence score (0-1)

        Returns:
            True if sent successfully
        """
        notification = NotificationPayload(
            title="Diagnosis Complete",
            message=f"Root cause identified: {root_cause}",
            level=NotificationLevel.INFO,
            incident_id=incident_id,
            metadata={
                "confidence": f"{confidence:.0%}",
                "status": "remediating",
            },
        )
        return await self.send(notification)

    def _record_history(
        self,
        notification: NotificationPayload,
        success: bool,
        reason: str = "",
    ) -> None:
        """Record notification in history."""
        record = {
            "title": notification.title,
            "level": notification.level.value,
            "incident_id": notification.incident_id,
            "timestamp": notification.timestamp,
            "success": success,
        }
        if reason:
            record["failure_reason"] = reason

        self._notification_history.append(record)

        # Keep history bounded
        if len(self._notification_history) > 500:
            self._notification_history = self._notification_history[-250:]

    async def close(self) -> None:
        """Close the HTTP session."""
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None
