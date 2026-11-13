# Copyright (c) 2026 Emberfall. All Rights Reserved.
"""Curved wall module that closes the front of a round bay."""

__author__ = "Matthias Stefan"
__version__ = "0.1.0"

from dataclasses import dataclass

from ..bld_base_slot_module import TOLERANCE
from .bld_bay_wall_module import BayWallModule


@dataclass(frozen=True)
class ArcWallModule(BayWallModule):
    """Immutable wall bent to a circular arc, it replaces a straight wall of the same width.

    Local frame: the origin is the middle of the chord on the wall line, the ends of the arc
    lie at X = -width / 2 and X = width / 2, the arc bulges toward the front (-Y).
    The inherited depth is the wall thickness.
    """

    bulge: float = 0.5
    """Distance in m from the chord to the middle of the arc, half the width makes a half circle."""
    segments: int = 8
    """Number of straight pieces the arc is built from."""

    @property
    def name_prefix(self) -> str:
        return "arc_wall"

    @property
    def name(self) -> str:
        """Asset name with dimensions and bulge in cm."""
        return f"{super().name}_b{round(self.bulge * 100)}"

    def validate(self) -> None:
        """Validates that the arc is a real arc of at most a half circle.

        Raises:
            ValueError: If the bulge is not positive, exceeds half the width, or there are too few segments.

        Returns:
            None.
        """
        super().validate()
        if self.bulge <= 0.0 or self.bulge > self.width * 0.5 + TOLERANCE:
            raise ValueError(f"bulge must be in 0..width/2, got {self.bulge} for width {self.width}")
        if self.segments < 2:
            raise ValueError(f"segments must be >= 2, got {self.segments}")
