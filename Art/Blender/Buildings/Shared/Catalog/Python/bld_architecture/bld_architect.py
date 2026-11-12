# Copyright (c) 2026 Emberfall. All Rights Reserved.
"""Designs building plans from create infos."""

__author__ = "Matthias Stefan"
__version__ = "0.1.0"

import random

from bld_modules import DoorModule

from .bld_create_info import BuildingCreateInfo
from .bld_house_plan import (
    Footprint,
    FootprintDesigner,
    HousePlan,
    ModuleRing,
    OpeningPlacer,
    OutlineReader,
    WallFiller,
)
from .bld_style import Style


class Architect:
    """Designs building plans in four steps: footprint, outline, walls, openings."""

    def __init__(self, style: Style) -> None:
        """Creates an architect.

        Args:
            style: Look of the buildings, provides the modules the architect may plan with.

        Returns:
            None.
        """
        self._style: Style = style
        self._footprint_designer: FootprintDesigner = FootprintDesigner()
        self._outline_reader: OutlineReader = OutlineReader()
        self._wall_filler: WallFiller = WallFiller(style.atlas)
        self._opening_placer: OpeningPlacer = OpeningPlacer(style.atlas)

    def design(self, create_info: BuildingCreateInfo) -> HousePlan:
        """Designs one building.

        Args:
            create_info: Description of the building to design.

        Returns:
            Footprint and module rings of the building, carrying the seed it was designed with.
        """
        footprint: Footprint = self._footprint_designer.design(create_info)

        # own random stream, so changes to the walls never move the footprint of a seed
        wall_random: random.Random = random.Random(f"{create_info.seed}:walls")
        filled_rings: tuple[ModuleRing, ...] = tuple(
            self._wall_filler.fill(ring, wall_random)
            for ring in self._outline_reader.read(footprint)
        )

        # own random stream again, so openings never move the walls of a seed
        opening_random: random.Random = random.Random(f"{create_info.seed}:openings")
        remaining_doors: int = create_info.openings.door_count
        rings: list[ModuleRing] = []
        for filled_ring in filled_rings:
            ring_with_openings: ModuleRing = self._opening_placer.place(
                filled_ring, remaining_doors, create_info.openings, opening_random
            )
            remaining_doors -= sum(
                isinstance(placement.module, DoorModule)
                for placement in ring_with_openings.placements
            )
            rings.append(ring_with_openings)
        return HousePlan(footprint=footprint, rings=tuple(rings))
