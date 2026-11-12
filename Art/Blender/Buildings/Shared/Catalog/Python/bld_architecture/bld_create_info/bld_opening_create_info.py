# Copyright (c) 2026 Emberfall. All Rights Reserved.
"""Create info for the doors and windows of one building."""

__author__ = "Matthias Stefan"
__version__ = "0.1.0"

from dataclasses import dataclass


@dataclass(frozen=True)
class OpeningCreateInfo:
    """Rules for the doors and windows of one building."""

    door_count: int = 1
    """Number of doors, capped by the walls that have a door of the same width."""
    window_chance: float = 0.5
    """Probability that a wall with a matching window becomes a window, 0..1."""
    min_walls_between_openings: int = 1
    """Plain walls that must stand between two openings in a ring."""

    def __post_init__(self) -> None:
        """Validates the rules right after construction.

        Raises:
            ValueError: If a value is out of range.

        Returns:
            None.
        """
        if self.door_count < 0:
            raise ValueError(f"door_count must be >= 0, got {self.door_count}")
        if not 0.0 <= self.window_chance <= 1.0:
            raise ValueError(f"window_chance must be in 0..1, got {self.window_chance}")
        if self.min_walls_between_openings < 0:
            raise ValueError(
                f"min_walls_between_openings must be >= 0, got {self.min_walls_between_openings}"
            )
