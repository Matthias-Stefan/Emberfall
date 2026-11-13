# Copyright (c) 2026 Emberfall. All Rights Reserved.
"""Floor slab in the shape of a circular segment, the floor of a round bay."""

__author__ = "Matthias Stefan"
__version__ = "0.1.0"

from dataclasses import dataclass

from ..bld_base_slot_module import TOLERANCE
from .bld_floor_module import FloorModule


@dataclass(frozen=True)
class ArcFloorModule(FloorModule):
    """Immutable slab between a chord and a circular arc, its bottom at Z = 0.

    Local frame: centered in X and Y like every slab, the chord runs along the back (+Y)
    and the arc bulges toward the front (-Y). The inherited width is the chord and the
    inherited depth is the bulge, so it fills a bay of that size.
    """

    segments: int = 8
    """Number of straight pieces the arc is built from."""

    @property
    def name_prefix(self) -> str:
        return "arc_floor"

    def validate(self) -> None:
        """Validates that the arc is at most a half circle.

        Raises:
            ValueError: If the depth exceeds half the width or there are too few segments.

        Returns:
            None.
        """
        super().validate()
        if self.depth > self.width * 0.5 + TOLERANCE:
            raise ValueError(f"depth must be <= width/2, got {self.depth} for width {self.width}")
        if self.segments < 2:
            raise ValueError(f"segments must be >= 2, got {self.segments}")
