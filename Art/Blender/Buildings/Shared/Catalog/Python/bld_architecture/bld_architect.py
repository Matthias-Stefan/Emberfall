# Copyright (c) 2026 Emberfall. All Rights Reserved.
# bld_architecture/bld_architect.py

import random

from .bld_building_create_info import BuildingCreateInfo
from .bld_footprint import Footprint
from .bld_module_atlas import ModuleAtlas


class Architect:
    """Designs building plans from create infos, using only modules from its atlas."""

    def __init__(self, atlas: ModuleAtlas) -> None:
        """Creates an architect.

        Args:
            atlas: Modules the architect may plan with.

        Returns:
            None.
        """
        self._atlas: ModuleAtlas = atlas
        return None

    def design(self, create_info: BuildingCreateInfo) -> Footprint:
        """Designs one building.

        Args:
            create_info: Description of the building to design.

        Returns:
            Footprint of the building, carrying the seed it was designed with.
        """
        random_source: random.Random = random.Random(create_info.seed)

        main_width, main_depth = self._roll_main_size(create_info, random_source)
        main_cells: frozenset[tuple[int, int]] = frozenset(
            (cell_x, cell_y)
            for cell_x in range(main_width)
            for cell_y in range(main_depth)
        )

        # next: extensions, attached to the sides of main_cells
        return Footprint(seed=create_info.seed, main_cells=main_cells)

    def _roll_main_size(
        self, create_info: BuildingCreateInfo, random_source: random.Random
    ) -> tuple[int, int]:
        """Rolls width and depth of the main building in cells.

        Args:
            create_info: Limits for the building.
            random_source: The only source of randomness.

        Raises:
            ValueError: If no area in the allowed range has a fitting rectangle.

        Returns:
            Width and depth in cells.
        """
        areas: list[int] = list(
            range(create_info.min_main_area, create_info.max_main_area + 1)
        )
        random_source.shuffle(areas)

        # walk the areas in random order, the first one with a valid rectangle wins
        for area in areas:
            candidates: list[tuple[int, int]] = self._rectangles_for_area(
                area, create_info
            )
            if candidates:
                return random_source.choice(candidates)

        raise ValueError(
            f"No main building size fits the limits: areas "
            f"{create_info.min_main_area}..{create_info.max_main_area}, "
            f"min edge {create_info.min_main_edge}, "
            f"max aspect ratio {create_info.max_aspect_ratio}"
        )

    @staticmethod
    def _rectangles_for_area(
        area: int, create_info: BuildingCreateInfo
    ) -> list[tuple[int, int]]:
        """Collects all width and depth pairs that give exactly the given area.

        Args:
            area: Target area in cells.
            create_info: Limits for the edge length and aspect ratio.

        Returns:
            Valid (width, depth) pairs in ascending width order, both
            orientations included, empty if the area has none (e.g. a prime).
        """
        rectangles: list[tuple[int, int]] = []
        min_edge: int = create_info.min_main_edge

        for width in range(min_edge, area // min_edge + 1):
            if area % width != 0:
                continue
            depth: int = area // width
            if depth < min_edge:
                continue
            longer_edge: int = max(width, depth)
            shorter_edge: int = min(width, depth)
            if longer_edge / shorter_edge > create_info.max_aspect_ratio:
                continue
            rectangles.append((width, depth))
        return rectangles
