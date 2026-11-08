# Copyright (c) 2026 Emberfall. All Rights Reserved.

from dataclasses import dataclass

from .bld_footprint import Footprint
from .bld_wall_ring import WallRing

@dataclass(frozen=True)
class HousePlan:
    """Footprint plus everything placed on its outer contour."""

    footprint: Footprint
    """Cells the plan was derived from."""
    rings: tuple[WallRing, ...]
    """One ring per closed outer contour."""
