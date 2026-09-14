"""Log configuration shared by the command line entry points."""

from __future__ import annotations

import logging

LOG_FORMAT = "%(asctime)s %(levelname)-8s %(name)s: %(message)s"

VALID_LOG_LEVELS = frozenset({"DEBUG", "INFO", "WARNING", "ERROR"})


def configure_logging(level: str) -> None:
    """Sets up the root logger.

    Args:
        level: Name of the log level, for example ``INFO``.
    """
    logging.basicConfig(level=level, format=LOG_FORMAT)
