"""External Isaac Lab tasks for the MicroDuck teaching playground."""

from __future__ import annotations

import sys

from . import tasks  # noqa: F401


def register_tasks() -> list[str]:
    """External-callback entry point used by Isaac Lab train/play commands."""
    return sys.argv[1:]
