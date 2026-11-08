# Copyright (c) 2026 Emberfall. All Rights Reserved.

from dataclasses import dataclass

from bld_modules import BaseModule


@dataclass(frozen=True)
class Placement:
    """One module placed on the grid."""

    module: BaseModule
    """Module that stands in this slot."""
    position: tuple[float, float]
    """Slot center in m, on the wall midline."""
    rotation_steps: int
    """Quarter turns counter-clockwise around Z, 0 means the front (-Y) faces south."""
