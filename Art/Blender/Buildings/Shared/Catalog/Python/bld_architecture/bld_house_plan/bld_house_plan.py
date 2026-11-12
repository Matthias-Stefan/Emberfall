# Copyright (c) 2026 Emberfall. All Rights Reserved.
"""Result of the architect: footprint plus the modules placed on its outline."""

__author__ = "Matthias Stefan"
__version__ = "0.1.0"

from dataclasses import dataclass

from bld_modules import BaseModule

from .bld_steps.bld_step_1_footprint import Footprint


@dataclass(frozen=True)
class ModulePlacement:
    """One module placed on the grid."""

    module: BaseModule
    """Module that stands in this slot."""
    position: tuple[float, float]
    """Slot center in m, on the wall midline."""
    rotation_steps: int
    """Quarter turns counter-clockwise around Z, 0 means the front (-Y) faces south."""


@dataclass(frozen=True)
class ModuleRing:
    """Closed outer outline of a footprint, posts, walls, doors and windows in walking order."""

    placements: tuple[ModulePlacement, ...]


@dataclass(frozen=True)
class HousePlan:
    """Footprint plus everything placed on its outer outline."""

    footprint: Footprint
    """Cells the plan was derived from."""
    rings: tuple[ModuleRing, ...]
    """One ring per closed outer outline."""
