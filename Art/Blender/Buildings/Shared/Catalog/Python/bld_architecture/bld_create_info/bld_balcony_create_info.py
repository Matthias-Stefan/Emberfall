# Copyright (c) 2026 Emberfall. All Rights Reserved.
"""Create info for the optional balconies in front of the doors."""

__author__ = "Matthias Stefan"
__version__ = "0.1.0"

from dataclasses import dataclass


@dataclass(frozen=True)
class BalconyCreateInfo:
    """Rules for the balconies, a railed platform at foundation height in front of a door."""

    enabled: bool = True
    """Whether doors may get a balcony, needs a foundation."""
    chance: float = 0.5
    """Probability that a door gets a balcony instead of a plain stair, 0..1."""
    min_depth: int = 1
    """Smallest balcony depth away from the wall in cells."""
    max_depth: int = 2
    """Largest balcony depth away from the wall in cells."""
    max_extra_width: int = 1
    """Cells the balcony may reach past each side of its doors, never past the end of the wall."""
    merge_door_gap: float = 4.0
    """Largest stretch of wall in m between two doors of one wall that still share one balcony."""

    def __post_init__(self) -> None:
        """Validates the rules right after construction.

        Raises:
            ValueError: If a value is out of range or contradicts another.

        Returns:
            None.
        """
        if not 0.0 <= self.chance <= 1.0:
            raise ValueError(f"chance must be in 0..1, got {self.chance}")
        if self.min_depth < 1:
            raise ValueError(f"min_depth must be >= 1, got {self.min_depth}")
        if self.min_depth > self.max_depth:
            raise ValueError(f"min_depth ({self.min_depth}) exceeds max_depth ({self.max_depth})")
        if self.max_extra_width < 0:
            raise ValueError(f"max_extra_width must be >= 0, got {self.max_extra_width}")
        if self.merge_door_gap < 0.0:
            raise ValueError(f"merge_door_gap must be >= 0, got {self.merge_door_gap}")
        return None
