# Copyright (c) 2026 Emberfall. All Rights Reserved.
"""Wall module that cuts off a corner at 45 degrees."""

__author__ = "Matthias Stefan"
__version__ = "0.1.0"

from dataclasses import dataclass

from .bld_wall_module import WallModule


@dataclass(frozen=True)
class DiagonalWallModule(WallModule):
    """Immutable wall that runs at 45 degrees, it closes the cut corner of a building.

    Local frame: the module is a straight wall turned 45 degrees counter-clockwise, its width
    axis points north-east and its front (-Y) looks south-east. Quarter turns move it to the
    other three corners. The inherited width is the length of the diagonal.
    """

    @property
    def name_prefix(self) -> str:
        return "diagonal_wall"
