# Copyright (c) 2026 Emberfall. All Rights Reserved.
"""Create info that describes one building to design: the sub infos plus the seed."""

__author__ = "Matthias Stefan"
__version__ = "0.1.0"

import math
from dataclasses import dataclass, field

from .bld_balcony_create_info import BalconyCreateInfo
from .bld_extensions_create_info import ExtensionsCreateInfo
from .bld_footprint_create_info import FootprintCreateInfo
from .bld_foundation_create_info import FoundationCreateInfo
from .bld_opening_create_info import OpeningCreateInfo


@dataclass(frozen=True)
class BuildingCreateInfo:
    """Describes one building to design: the sub infos plus the seed."""

    footprint: FootprintCreateInfo
    """Limits for the main building."""
    seed: int
    """Seed for reproducible results."""
    extensions: ExtensionsCreateInfo = field(default_factory=ExtensionsCreateInfo)
    """Rules for the extensions."""
    openings: OpeningCreateInfo = field(default_factory=OpeningCreateInfo)
    """Rules for doors and windows."""
    foundation: FoundationCreateInfo = field(default_factory=FoundationCreateInfo)
    """Rules for the foundation."""
    balconies: BalconyCreateInfo = field(default_factory=BalconyCreateInfo)
    """Rules for the balconies."""

    @property
    def extension_factor(self) -> float:
        """Total area divided by main area if every extension uses its full ratio."""
        return 1.0 + self.extensions.max_count * self.extensions.max_area_ratio

    @property
    def min_main_area(self) -> int:
        """Smallest main building area in cells that can still reach the total minimum."""
        return math.ceil(self.footprint.min_total_area / self.extension_factor)

    @property
    def max_main_area(self) -> int:
        """Largest main building area in cells that still fits the total maximum."""
        return math.floor(self.footprint.max_total_area / self.extension_factor)

    def __post_init__(self) -> None:
        """Validates the rules that involve more than one sub info.

        Each sub info validates itself, only the combinations are checked here.

        Raises:
            ValueError: If no main building can satisfy the combined limits.

        Returns:
            None.
        """
        if self.min_main_area > self.max_main_area:
            raise ValueError(
                f"No main building fits: area {self.min_main_area}..{self.max_main_area} cells"
            )
        if self.footprint.min_main_edge ** 2 > self.max_main_area:
            raise ValueError(
                f"max main area ({self.max_main_area}) is smaller than "
                f"min_main_edge squared ({self.footprint.min_main_edge ** 2})"
            )
