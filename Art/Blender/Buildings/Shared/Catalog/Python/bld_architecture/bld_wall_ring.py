# Copyright (c) 2026 Emberfall. All Rights Reserved.

from dataclasses import dataclass

from .bld_placement import Placement


@dataclass(frozen=True)
class WallRing:
    """Closed outer contour of a footprint, corners and wall slots in walking order."""

    placements: tuple[Placement, ...]
