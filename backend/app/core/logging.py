"""
app/core/logging.py

Structured logging configuration using structlog.

* Development  → colourised, human-readable console output.
* Production   → JSON output (one JSON object per log line).

Each log record contains at minimum:
  timestamp, level, logger, message
and optionally:
  request_id  (bound from middleware context).

Usage
-----
    from app.core.logging import get_logger, setup_logging
    setup_logging(settings)          # call once at startup
    log = get_logger(__name__)
    log.info("server started", port=8000)
"""

from __future__ import annotations

import logging
import sys
from typing import TYPE_CHECKING

import structlog

if TYPE_CHECKING:
    from app.core.config import Settings


def setup_logging(settings: "Settings") -> None:
    """Configure structlog and the stdlib root logger.

    Must be called exactly once during application startup (in the lifespan
    context manager inside ``app/main.py``).
    """
    is_development = settings.APP_ENV == "development"
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.DEBUG)

    # ------------------------------------------------------------------ #
    # Shared processors that run for every log event
    # ------------------------------------------------------------------ #
    shared_processors: list[structlog.types.Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.StackInfoRenderer(),
    ]

    if is_development:
        # Human-readable colourised output for local development
        processors: list[structlog.types.Processor] = [
            *shared_processors,
            structlog.dev.ConsoleRenderer(colors=True),
        ]
    else:
        # Machine-readable JSON for staging / production
        processors = [
            *shared_processors,
            structlog.processors.dict_tracebacks,
            structlog.processors.JSONRenderer(),
        ]

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(log_level),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(sys.stdout),
        cache_logger_on_first_use=True,
    )

    # Keep stdlib logging in sync so that third-party libraries
    # (uvicorn, sqlalchemy, httpx, …) also respect the log level.
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=log_level,
    )
    # Silence noisy libraries in production
    if not is_development:
        logging.getLogger("uvicorn.access").setLevel(logging.WARNING)


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Return a structlog bound logger namespaced to *name*.

    Example::

        log = get_logger(__name__)
        log.info("processing document", document_id=str(doc.id))
    """
    return structlog.get_logger(name)
