# Copyright (c) 2026 Emberfall. All Rights Reserved.

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class BuildingCreateInfo:
    """Describes one building to design, including its seed."""

    min_total_area: int
    """Minimum footprint of the whole building in cells."""
    max_total_area: int
    """Maximum footprint of the whole building in cells."""

    min_main_edge: int
    """Smallest edge length of the main building in cells."""
    max_aspect_ratio: float
    """Longer divided by shorter edge of the main building, upper limit."""

    max_extensions: int
    """Maximum number of extensions."""
    max_attempts: int
    """Placement attempts per extension before it is skipped."""
    min_extension_size: int
    """Smallest extension edge length in cells."""
    max_extension_size: int
    """Largest extension edge length in cells."""
    max_extension_area_ratio: float
    """Extension area divided by main building area, upper limit."""
    allow_chained_extensions: bool
    """Whether extensions may attach to other extensions."""

    seed: int
    """Seed for reproducible results."""

    @property
    def extension_factor(self) -> float:
        """Total area divided by main area if every extension uses its full ratio."""
        return 1.0 + self.max_extensions * self.max_extension_area_ratio

    @property
    def min_main_area(self) -> int:
        """Smallest main building area in cells that can still reach the total minimum."""
        return math.ceil(self.min_total_area / self.extension_factor)

    @property
    def max_main_area(self) -> int:
        """Largest main building area in cells that still fits the total maximum."""
        return math.floor(self.max_total_area / self.extension_factor)

    def __post_init__(self) -> None:
        """Validates the limits right after construction.

        Raises:
            ValueError: If any limit is out of range or contradicts another.

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
            raise ValueError(
                f"max_aspect_ratio must be >= 1, got {self.max_aspect_ratio}"
            )
        if self.max_extensions < 0:
            raise ValueError(f"max_extensions must be >= 0, got {self.max_extensions}")
        if self.max_extensions > 0 and self.max_attempts < 1:
            raise ValueError(
                f"max_attempts must be >= 1 when extensions are allowed, got {self.max_attempts}"
            )
        if self.min_extension_size < 1:
            raise ValueError(
                f"min_extension_size must be >= 1, got {self.min_extension_size}"
            )
        if self.min_extension_size > self.max_extension_size:
            raise ValueError(
                f"min_extension_size ({self.min_extension_size}) exceeds "
                f"max_extension_size ({self.max_extension_size})"
            )
        if self.max_extension_area_ratio <= 0.0:
            raise ValueError(
                f"max_extension_area_ratio must be > 0, got {self.max_extension_area_ratio}"
            )
        if self.min_main_area > self.max_main_area:
            raise ValueError(
                f"No main building fits: area {self.min_main_area}..{self.max_main_area} cells"
            )
        if self.min_main_edge * self.min_main_edge > self.max_main_area:
            raise ValueError(
                f"max main area ({self.max_main_area}) is smaller than "
                f"min_main_edge squared ({self.min_main_edge ** 2})"
            )
        return None
