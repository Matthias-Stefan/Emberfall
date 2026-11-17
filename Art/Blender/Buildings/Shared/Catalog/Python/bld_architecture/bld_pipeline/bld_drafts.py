# Copyright (c) 2026 Emberfall. All Rights Reserved.
"""Half-finished plans the passes fill one after the other, one for the house and one per level."""

__author__ = "Matthias Stefan"
__version__ = "0.1.0"

import random
from dataclasses import dataclass

from bld_modules import ArcWallModule, StairModule

from ..bld_create_info import BuildingCreateInfo
from ..bld_house_plan import (
    BalconyPlan,
    CornerCut,
    Footprint,
    FoundationPlan,
    HousePlan,
    LevelPlan,
    ModulePlacement,
    ModuleRing,
    OutlineRing,
)
from ..bld_planners.bld_level_balcony_placer import LevelBalconyPlacer
from ..bld_planners.bld_level_stair_placer import StairCandidate
from ..bld_planners.bld_stair_placer import Rectangle, StairPlacer
from ..bld_style import Style

Cell = tuple[int, int]


@dataclass
class HouseDraft:
    """Ground floor of a house while the passes fill it, footprint and outline are fixed from the start."""

    info: BuildingCreateInfo
    """Building the draft is planned for, its seed drives all random streams."""
    style: Style
    """Look of the building, wall size and modules."""
    footprint: Footprint
    """Cells of the ground floor."""
    outlines: tuple[OutlineRing, ...]
    """Outline rings of the footprint, wall midline."""
    foundation: FoundationPlan | None = None
    """Foundation under the rings, @c None if the house stands on the ground."""
    rings: tuple[ModuleRing, ...] = ()
    """One module ring per outline, empty until the walls are filled."""
    balconies: tuple[BalconyPlan, ...] = ()
    """Balconies in front of the doors of the ground floor."""
    cuts: tuple[CornerCut, ...] = ()
    """Corners of the ground floor that are cut off."""
    floor: tuple[ModulePlacement, ...] = ()
    """Floor slabs of the ground floor, extra slabs of earlier passes stay behind the regular ones."""
    levels: tuple[LevelPlan, ...] = ()
    """Levels above the ground floor from bottom to top."""

    @property
    def elevation(self) -> float:
        """Height of the ground floor walls above the ground in m."""
        return self.foundation.height if self.foundation is not None else 0.0

    def random(self, stream: str) -> random.Random:
        """Creates the random stream of one pass.

        Every pass rolls on a stream of its own, so a change in one pass never moves the results of another.

        Args:
            stream is the name of the stream, unique per pass.

        Returns:
            A fresh random stream seeded with the building seed and the name.
        """
        return random.Random(f"{self.info.seed}:{stream}")

    def ground_obstacles(self) -> tuple[Rectangle, ...]:
        """Collects the areas on the ground that pillars and round ends must keep clear of.

        Returns:
            One area per stair, per round end, per balcony cell and per balcony stair.
        """
        obstacles: list[Rectangle] = [
            StairPlacer.rectangle_of(placement, placement.module.width, placement.module.depth)
            for ring in self.rings
            for placement in ring.placements
            if isinstance(placement.module, StairModule)
        ]
        # the half circles of round ends reach out of the wall line
        obstacles.extend(
            LevelBalconyPlacer.rectangle_of_wall(placement)
            for ring in self.rings
            for placement in ring.placements
            if isinstance(placement.module, ArcWallModule)
        )
        for balcony in self.balconies:
            obstacles.extend((cell_x, cell_y, cell_x + 1.0, cell_y + 1.0) for cell_x, cell_y in balcony.cells)
            obstacles.extend(
                StairPlacer.rectangle_of(stair, stair.module.width, stair.module.depth)
                for stair in balcony.stairs
            )
        return tuple(obstacles)

    def to_plan(self) -> HousePlan:
        """Freezes the draft.

        Returns:
            The finished plan of the house.
        """
        return HousePlan(
            footprint=self.footprint,
            rings=self.rings,
            balconies=self.balconies,
            foundation=self.foundation,
            floor=self.floor,
            levels=self.levels,
        )


@dataclass
class LevelDraft:
    """One level above the ground floor while the passes fill it, footprint and stair are fixed from the start."""

    house: HouseDraft
    """Ground floor and building the level belongs to."""
    number: int
    """Number of the level, 1 is the first level above the ground floor."""
    footprint: Footprint
    """Cells of the level."""
    outlines: tuple[OutlineRing, ...]
    """Outline rings of the level, empty if the levels get no walls."""
    stair: StairCandidate
    """Interior stair that leads up to the level."""
    lower_footprint: Footprint
    """Cells of the level below."""
    lower_rings: tuple[ModuleRing, ...]
    """Rings of the level below, carried up features and braces stand on them."""
    slab_elevation: float
    """Height of the bottom of the floor slabs in m."""
    slab_height: float
    """Thickness of the floor slabs in m."""
    rings: tuple[ModuleRing, ...] = ()
    """One module ring per outline, an extra ring with balcony rails may follow."""
    cuts: tuple[CornerCut, ...] = ()
    """Corners of the level that are cut off."""
    floor: tuple[ModulePlacement, ...] = ()
    """Floor slabs of the level, extra slabs of earlier passes stay behind the regular ones."""

    @property
    def wall_elevation(self) -> float:
        """Height of the wall bottoms above the ground in m, on top of the slabs."""
        return self.slab_elevation + self.slab_height

    @property
    def hole(self) -> frozenset[Cell]:
        """Cells of the level without a slab, the stair comes through them."""
        return self.stair.covered & self.footprint.cells

    def random(self, stream: str) -> random.Random:
        """Creates the random stream of one pass on this level.

        Args:
            stream is the name of the stream, unique per pass.

        Returns:
            A fresh random stream seeded with the building seed, the level number and the name.
        """
        return self.house.random(f"level{self.number}:{stream}")

    def to_plan(self) -> LevelPlan:
        """Freezes the draft.

        Returns:
            The finished plan of the level.
        """
        return LevelPlan(
            footprint=self.footprint,
            elevation=self.wall_elevation,
            rings=self.rings,
            floor=self.floor,
            stairs=(self.stair.stair,),
            hole=self.hole,
        )
