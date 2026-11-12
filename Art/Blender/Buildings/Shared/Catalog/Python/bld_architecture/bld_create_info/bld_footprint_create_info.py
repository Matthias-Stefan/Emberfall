# Copyright (c) 2026 Emberfall. All Rights Reserved.
"""Create infos that describe one building to design."""

__author__ = "Matthias Stefan"
__version__ = "0.1.0"

from dataclasses import dataclass


@dataclass(frozen=True)
class FootprintCreateInfo:
    """Limits for the main building, measured in cells."""

    min_total_area: int
    """Minimum footprint of the whole building in cells."""
    max_total_area: int
    """Maximum footprint of the whole building in cells."""
    min_main_edge: int
    """Smallest edge length of the main building in cells."""
    max_aspect_ratio: float
    """Longer divided by shorter edge of the main building, upper limit."""

    def __post_init__(self) -> None:
        """Validates the limits right after construction.

        Raises:
            ValueError: If a limit is out of range or contradicts another.

        Returns:
            None.
        """
        if self.min_total_area < 1:
            raise ValueError(f"min_total_area must be >= 1, got {self.min_total_area}")
        if self.min_total_area > self.max_total_area:
            raise ValueError(
                f"min_total_area ({self.min_total_area}) exceeds "
                f"max_total_area ({self.max_total_area})"
            )
        if self.min_main_edge < 1:
            raise ValueError(f"min_main_edge must be >= 1, got {self.min_main_edge}")
        if self.max_aspect_ratio < 1.0:
            raise ValueError(f"max_aspect_ratio must be >= 1, got {self.max_aspect_ratio}")
