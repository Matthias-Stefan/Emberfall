# Copyright (c) 2026 Emberfall. All Rights Reserved.
"""Floor slab of half a cell, the floor of a cell that a cut corner halves."""

__author__ = "Matthias Stefan"
__version__ = "0.1.0"

from dataclasses import dataclass

from .bld_floor_module import FloorModule


@dataclass(frozen=True)
class TriangleFloorModule(FloorModule):
    """Immutable slab in the shape of a right triangle, half of a rectangular slab.

    Local frame: the slab is centered in X and Y like every slab, the right angle lies in the
    north-west corner and the hypotenuse runs from the south-west to the north-east corner.
    It belongs to a cell whose south-east corner is cut off, quarter turns move the cut.
    """

    @property
    def name_prefix(self) -> str:
        return "triangle_floor"
