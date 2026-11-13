# Copyright (c) 2026 Emberfall. All Rights Reserved.
"""Short wall module that closes the sides of a bay."""

__author__ = "Matthias Stefan"
__version__ = "0.1.0"

from dataclasses import dataclass

from .bld_wall_module import WallModule


@dataclass(frozen=True)
class BayWallModule(WallModule):
    """Immutable short wall on the side of a bay, never used to fill a straight wall segment."""

    @property
    def name_prefix(self) -> str:
        return "bay_wall"
