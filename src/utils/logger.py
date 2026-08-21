"""StudioPulse AI - Structured Logging"""

import os
import sys
import logging
import structlog


def setup_logger(name: str) -> structlog.BoundLogger:
    """Set up structured logging for the application."""
    log_level = os.getenv("AGENT_LOG_LEVEL", "INFO")

    # Map string level to int
    level = getattr(logging, log_level.upper(), logging.INFO)

    # Handle Windows console encoding issues with emojis
    if sys.platform == "win32":
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, OSError):
            pass

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.dev.ConsoleRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(level),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=False,
    )

    return structlog.get_logger(name)
