# Copyright (c) 2026 Emberfall. All Rights Reserved.
"""Parts a house is sorted into in the outliner."""

__author__ = "Matthias Stefan"
__version__ = "0.1.0"

from enum import Enum

from bld_modules import ArcWindowModule, DiagonalWindowModule, BaseSlotModule, DoorModule, FloorModule, StairModule, WindowModule


class HousePart(Enum):
    """Part of a house, every part gets its own collection."""

    FOOTPRINT = "footprint"
    """Flat cell quads that show the footprint."""
    FOUNDATION = "foundation"
    """Foundation bands."""
    FLOOR = "floor"
    """Floor slabs."""
    WALLS = "walls"
    """Posts and plain walls."""
    OPENINGS = "openings"
    """Doors and windows."""
    STAIRS = "stairs"
    """Stairs in front of the doors."""

    @staticmethod
    def of(module: BaseSlotModule) -> "HousePart":
        """Finds the part a placed module belongs to.

        Args:
            module is the placed module.

        Returns:
            The part, posts and plain walls count as walls.
        """
        if isinstance(module, (DoorModule, WindowModule, ArcWindowModule, DiagonalWindowModule)):
            return HousePart.OPENINGS
        if isinstance(module, StairModule):
            return HousePart.STAIRS
        if isinstance(module, FloorModule):
            return HousePart.FLOOR
        return HousePart.WALLS
