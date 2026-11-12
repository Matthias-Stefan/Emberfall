# Copyright (c) 2026 Emberfall. All Rights Reserved.
"""Create info for the levels above the ground floor."""

__author__ = "Matthias Stefan"
__version__ = "0.1.0"

from dataclasses import dataclass


@dataclass(frozen=True)
class LevelsCreateInfo:
    """Rules for the levels above the ground floor."""

    upper_count: int = 1
    """Number of levels above the ground floor, each one repeats the footprint of the ground floor."""
    build_walls: bool = False
    """Whether the levels get walls and windows, off while only floors and stairs are developed."""

    def __post_init__(self) -> None:
        """Validates the rules right after construction.

        Raises:
            ValueError: If a value is out of range.

        Returns:
            None.
        """
        if self.upper_count < 0:
            raise ValueError(f"upper_count must be >= 0, got {self.upper_count}")
        return None
