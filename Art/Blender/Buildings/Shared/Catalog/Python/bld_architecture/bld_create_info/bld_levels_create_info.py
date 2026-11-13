# Copyright (c) 2026 Emberfall. All Rights Reserved.
"""Create info for the levels above the ground floor."""

__author__ = "Matthias Stefan"
__version__ = "0.1.0"

from dataclasses import dataclass


@dataclass(frozen=True)
class LevelsCreateInfo:
    """Rules for the levels above the ground floor."""

    upper_count: int = 1
    """Number of levels above the ground floor."""
    build_walls: bool = True
    """Whether the levels get walls, windows and bays."""
    vary_footprint: bool = True
    """Whether a level may use fewer cells than the level below, False repeats its footprint."""
    min_area_ratio: float = 0.5
    """Smallest area of a level divided by the area of the level below."""
    max_area_ratio: float = 1.0
    """Largest area of a level divided by the area of the level below, 1 allows the same footprint."""
    max_bays: int = 2
    """Most bays per level, 0 builds none."""
    bay_chance: float = 0.6
    """Chance that a bay is placed on a free wall that fits one."""
    bay_widths: tuple[float, ...] = (1.0, 2.0)
    """Widths in m of the walls a bay may replace."""
    min_bay_distance: float = 3.0
    """Smallest distance in m between the centers of two bays of one level."""
    min_bay_corner_distance: float = 1.0
    """Smallest distance in m between a bay and the next corner of the outline."""

    def __post_init__(self) -> None:
        """Validates the rules right after construction.

        Raises:
            ValueError: If a value is out of range.

        Returns:
            None.
        """
        if self.upper_count < 0:
            raise ValueError(f"upper_count must be >= 0, got {self.upper_count}")
        if not 0.0 < self.min_area_ratio <= self.max_area_ratio <= 1.0:
            raise ValueError(
                f"area ratios must satisfy 0 < min <= max <= 1, got {self.min_area_ratio}..{self.max_area_ratio}"
            )
        if self.max_bays < 0:
            raise ValueError(f"max_bays must be >= 0, got {self.max_bays}")
        if not 0.0 <= self.bay_chance <= 1.0:
            raise ValueError(f"bay_chance must be in 0..1, got {self.bay_chance}")
        if self.min_bay_distance < 0.0 or self.min_bay_corner_distance < 0.0:
            raise ValueError("bay distances must be >= 0")
        return None
