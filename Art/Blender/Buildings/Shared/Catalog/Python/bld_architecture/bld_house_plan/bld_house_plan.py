# Copyright (c) 2026 Emberfall. All Rights Reserved.
"""Result of the architect: footprint plus the modules placed on its outline."""

__author__ = "Matthias Stefan"
__version__ = "0.1.0"

from dataclasses import dataclass

from bld_modules import BaseModule

from .bld_steps.bld_step_1_footprint import Footprint, Side
from .bld_steps.bld_step_2_outline import OutlineRing


@dataclass(frozen=True)
class ModulePlacement:
    """One module placed on the grid."""

    module: BaseModule
    """Module that stands in this slot."""
    position: tuple[float, float]
    """Slot center in m, on the wall midline."""
    rotation_steps: int
    """Quarter turns counter-clockwise around Z, 0 means the front (-Y) faces south."""
    elevation: float = 0.0
    """Height of the module floor above the ground in m, the foundation height for house modules."""


@dataclass(frozen=True)
class ModuleRing:
    """Closed outer outline of a footprint, posts, walls, doors and windows in walking order."""

    placements: tuple[ModulePlacement, ...]


@dataclass(frozen=True)
class FoundationPlan:
    """Stone band under the outline rings that lifts the house off the ground."""

    outlines: tuple[OutlineRing, ...]
    """Outline rings the band follows, wall midline."""
    height: float
    """Height of the band in m."""
    overhang: float
    """How far the band sticks out past the wall faces in m."""
    wall_depth: float
    """Wall thickness in m, the band is centered on the wall midline."""


@dataclass(frozen=True)
class BalconyPlan:
    """Railed platform at foundation height on grid cells outside the building, in front of its doors."""

    cells: frozenset[tuple[int, int]]
    """Grid cells the platform covers, none of them belongs to the footprint."""
    doors: tuple[ModulePlacement, ...]
    """Doors the balcony leads to in walking order, their elevation is the platform height."""
    outward: Side
    """Side of the building the balcony lies on."""
    stairs: tuple[ModulePlacement, ...]
    """Stairs from the ground up to the balcony, side by side over the whole width of its front edge."""


@dataclass(frozen=True)
class LevelPlan:
    """One level above the ground floor: its footprint, walls and the floor slabs it stands on."""

    footprint: Footprint
    """Cells of the level, they may differ from the cells of the level below and overhang it."""
    elevation: float
    """Height of the wall bottoms above the ground in m."""
    rings: tuple[ModuleRing, ...]
    """One ring per closed outer outline, posts, walls and openings."""
    floor: tuple[ModulePlacement, ...]
    """Floor slabs the walls of the level stand on, without the cells of the stair hole."""
    stairs: tuple[ModulePlacement, ...] = ()
    """Interior stairs that lead up to this level, they start on the floor of the level below."""
    hole: frozenset[tuple[int, int]] = frozenset()
    """Cells without a floor slab where the stair comes through."""


@dataclass(frozen=True)
class HousePlan:
    """Footprint plus everything placed on its outer outline."""

    footprint: Footprint
    """Cells the plan was derived from."""
    rings: tuple[ModuleRing, ...]
    """One ring per closed outer outline."""
    foundation: FoundationPlan | None = None
    """Foundation under the rings, None if the house stands on the ground."""
    floor: tuple[ModulePlacement, ...] = ()
    """Floor slabs of the ground level, empty if the house stands on the ground."""
    balconies: tuple[BalconyPlan, ...] = ()
    """Balconies in front of the doors, empty if there are none."""
    levels: tuple[LevelPlan, ...] = ()
    """Levels above the ground floor from bottom to top, empty for a one story house."""
