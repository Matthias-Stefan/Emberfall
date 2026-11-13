# Copyright (c) 2026 Emberfall. All Rights Reserved.
"""Step 9 helper: footprint of the level below -> footprints for the level above, always cut from it."""

__author__ = "Matthias Stefan"
__version__ = "0.1.0"

import random
from collections import deque

from ...bld_create_info import LevelsCreateInfo
from .bld_step_1_footprint import Footprint

Cell = tuple[int, int]


class LevelFootprintDesigner:
    """Cuts footprints for a level out of the footprint below, so nothing of it hangs in the air."""

    def options(
        self,
        levels_info: LevelsCreateInfo,
        lower_footprint: Footprint,
        random_source: random.Random,
    ) -> list[Footprint]:
        """Collects the footprints a level above could have, in random order.

        A footprint is cut from the one below by dropping one extension or by taking away the
        outermost row or column on one side. Only shapes that stay in one piece and nowhere
        get narrower than two cells are offered.

        Args:
            levels_info is the rules for the levels, the area ratios limit the options.
            lower_footprint is the footprint of the level below.
            random_source is the random stream of the level, separate from all other steps.

        Returns:
            The footprints in random order, the footprint below itself included if the area
            ratios allow it. Empty if none is allowed. The caller must not rely on any option
            being usable, e.g. for a stair.
        """
        lower_cells: frozenset[Cell] = self.cells_of(lower_footprint)
        if not levels_info.vary_footprint:
            return [lower_footprint]

        shapes: list[frozenset[Cell]] = [lower_cells]
        for extension_cells in lower_footprint.extension_cells:
            shapes.append(lower_cells - extension_cells)
        for direction in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            shapes.append(self._without_outer_row(lower_cells, direction))

        options: list[Footprint] = []
        seen: set[frozenset[Cell]] = set()
        for shape in shapes:
            ratio: float = len(shape) / len(lower_cells)
            if shape in seen or not shape:
                continue
            seen.add(shape)
            if not levels_info.min_area_ratio <= ratio <= levels_info.max_area_ratio:
                continue
            if not self._is_solid(shape):
                continue
            options.append(self._cut(lower_footprint, shape))
        random_source.shuffle(options)
        return options

    @staticmethod
    def cells_of(footprint: Footprint) -> frozenset[Cell]:
        """Collects all cells of a footprint.

        Args:
            footprint is the footprint to read.

        Returns:
            The cells of the main building and all extensions.
        """
        return footprint.main_cells.union(*footprint.extension_cells)

    @staticmethod
    def _without_outer_row(cells: frozenset[Cell], direction: tuple[int, int]) -> frozenset[Cell]:
        """Takes the outermost row or column away on one side.

        Args:
            cells are the cells to cut.
            direction is the unit direction of the side, (1, 0) is the east side.

        Returns:
            The cells without the row or column that lies farthest in that direction.
        """
        reach: int = max(cell_x * direction[0] + cell_y * direction[1] for cell_x, cell_y in cells)
        return frozenset(
            (cell_x, cell_y)
            for cell_x, cell_y in cells
            if cell_x * direction[0] + cell_y * direction[1] < reach
        )

    @staticmethod
    def _is_solid(cells: frozenset[Cell]) -> bool:
        """Tests whether a shape is in one piece and every cell is part of a block of two by two.

        Args:
            cells are the cells to test.

        Returns:
            @c True if the shape is connected and nowhere narrower than two cells, otherwise @c False.
        """
        start: Cell = min(cells)
        reached: set[Cell] = {start}
        queue: deque[Cell] = deque([start])
        while queue:
            cell_x, cell_y = queue.popleft()
            for neighbor in ((cell_x + 1, cell_y), (cell_x - 1, cell_y), (cell_x, cell_y + 1), (cell_x, cell_y - 1)):
                if neighbor in cells and neighbor not in reached:
                    reached.add(neighbor)
                    queue.append(neighbor)
        if len(reached) != len(cells):
            return False

        def in_block(cell_x: int, cell_y: int) -> bool:
            return any(
                all(
                    (cell_x + step_x, cell_y + step_y) in cells
                    for step_x in (0, 1)
                    for step_y in (0, 1)
                )
                for cell_x, cell_y in (
                    (cell_x, cell_y),
                    (cell_x - 1, cell_y),
                    (cell_x, cell_y - 1),
                    (cell_x - 1, cell_y - 1),
                )
            )

        return all(in_block(cell_x, cell_y) for cell_x, cell_y in cells)

    @staticmethod
    def _cut(lower_footprint: Footprint, cells: frozenset[Cell]) -> Footprint:
        """Keeps the parts of a footprint that remain inside a shape.

        Args:
            lower_footprint is the footprint to cut.
            cells are the cells that remain.

        Returns:
            The footprint with the same seed, parts that lost all cells are dropped and the
            first part that is left becomes the main building.
        """
        parts: list[frozenset[Cell]] = [
            part & cells
            for part in (lower_footprint.main_cells, *lower_footprint.extension_cells)
            if part & cells
        ]
        return Footprint(
            seed=lower_footprint.seed,
            main_cells=parts[0],
            extension_cells=tuple(parts[1:]),
        )
