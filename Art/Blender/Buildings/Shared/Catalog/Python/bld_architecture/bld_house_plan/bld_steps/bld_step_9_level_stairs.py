# Copyright (c) 2026 Emberfall. All Rights Reserved.
"""Step 9 helper: cells and rings of a level -> the interior stairs that lead up from it."""

__author__ = "Matthias Stefan"
__version__ = "0.1.0"

import random
from dataclasses import dataclass

from bld_modules import TOLERANCE, DoorModule, StairModule

from ...bld_style import ModuleAtlas
from ..bld_house_plan import ModulePlacement, ModuleRing
from .bld_step_1_footprint import Footprint
from .bld_step_6_stairs import Rectangle, StairPlacer

Cell = tuple[int, int]

# climbing direction per quarter turn: the stair front (-Y) is the bottom, so it climbs the other way
_CLIMB: tuple[tuple[int, int], ...] = ((0, 1), (-1, 0), (0, -1), (1, 0))

DOOR_CLEARANCE: float = 1.0
"""Free space in m around a door in which no interior stair may stand."""


@dataclass(frozen=True)
class StairCandidate:
    """One stair that fits on a level, before it is matched with the level above."""

    stair: ModulePlacement
    """The stair, it starts on the floor of its level."""
    covered: frozenset[Cell]
    """Cells of the level below the stair stands on, they are a hole in the level above."""
    landing: Cell
    """Cell behind the top of the stair, it needs a floor on the level above."""


class LevelStairPlacer:
    """Puts a straight stair inside the footprint that climbs from one floor to the next."""

    def __init__(self, atlas: ModuleAtlas) -> None:
        """Creates a level stair placer.

        Args:
            atlas: Stairs the placer may choose from.

        Returns:
            None.
        """
        self._atlas: ModuleAtlas = atlas
        return None

    def candidates(
        self,
        lower_cells: frozenset[Cell],
        lower_rings: tuple[ModuleRing, ...],
        blocked_cells: frozenset[Cell],
        bottom_elevation: float,
        rise: float,
        random_source: random.Random,
    ) -> tuple[StairCandidate, ...]:
        """Collects every place where a stair of the right rise fits on the level below.

        The cells of the level above are not known yet, the caller keeps the candidates whose
        landing cell lies on that level.

        Args:
            lower_cells are the cells of the level the stair starts on, the stair stands on them.
            lower_rings are the rings of that level, the stair keeps clear of their walls and doors.
            blocked_cells are the cells the stair must not use, e.g. the hole of the level below.
            bottom_elevation is the height of the floor the stair starts on in m.
            rise is the height the stair climbs in m.
            random_source is the random stream that picks the stair module, separate from all other steps.

        Returns:
            One candidate per rotation and start cell, empty if no stair of that rise fits.
            There is a free cell in front of the bottom of every candidate.
        """
        modules: list[StairModule] = [
            module
            for module in self._atlas.modules_of(StairModule)
            if isinstance(module, StairModule) and abs(module.height - rise) <= TOLERANCE
        ]
        if not modules:
            return ()
        module: StairModule = random_source.choice(modules)

        obstacles: list[Rectangle] = self._obstacles(lower_rings)
        candidates: list[StairCandidate] = []
        for rotation_steps in range(4):
            climb: tuple[int, int] = _CLIMB[rotation_steps]
            for cell_x, cell_y in sorted(lower_cells):
                # the stair starts at the edge of the cell it begins in and runs along the climb direction
                start_x: float = cell_x + (0.0 if climb[0] > 0 else 1.0 if climb[0] < 0 else 0.5)
                start_y: float = cell_y + (0.0 if climb[1] > 0 else 1.0 if climb[1] < 0 else 0.5)
                center: tuple[float, float] = (
                    start_x + climb[0] * module.depth * 0.5,
                    start_y + climb[1] * module.depth * 0.5,
                )
                stair: ModulePlacement = ModulePlacement(module, center, rotation_steps, bottom_elevation)
                area: Rectangle = StairPlacer.rectangle_of(stair, module.width, module.depth)
                covered: frozenset[Cell] = self._cells_under(area, lower_cells)
                if not covered or not covered <= lower_cells or covered & blocked_cells:
                    continue
                if any(StairPlacer.overlaps(area, obstacle) for obstacle in obstacles):
                    continue
                # somebody has to be able to step on at the bottom
                before: Cell = self._neighbor(start_x, start_y, (-climb[0], -climb[1]))
                if before not in lower_cells or before in blocked_cells or before in covered:
                    continue
                landing: Cell = self._neighbor(
                    start_x + climb[0] * module.depth, start_y + climb[1] * module.depth, climb
                )
                if landing in covered:
                    continue
                candidates.append(StairCandidate(stair, covered, landing))
        return tuple(candidates)

    @staticmethod
    def _neighbor(point_x: float, point_y: float, direction: tuple[int, int]) -> Cell:
        """Finds the cell that lies just past a stair end in a direction.

        Args:
            point_x is the X of the stair end center in m.
            point_y is the Y of the stair end center in m.
            direction is the unit direction pointing away from the stair.

        Returns:
            The cell next to the end point in that direction.
        """
        return (
            int((point_x + direction[0] * 0.5) // 1),
            int((point_y + direction[1] * 0.5) // 1),
        )

    @staticmethod
    def _cells_under(area: Rectangle, cells: frozenset[Cell]) -> frozenset[Cell]:
        """Collects the cells a stair area overlaps.

        Args:
            area is the area of the stair in m.
            cells are the cells of the footprint.

        Returns:
            The cells the area overlaps by more than the tolerance, cells outside the footprint
            included so the caller can reject stairs that leave it.
        """
        covered: set[Cell] = set()
        for cell_x in range(int(area[0] // 1), int(area[2] // 1) + 1):
            for cell_y in range(int(area[1] // 1), int(area[3] // 1) + 1):
                if StairPlacer.overlaps(area, (cell_x, cell_y, cell_x + 1.0, cell_y + 1.0)):
                    covered.add((cell_x, cell_y))
        return frozenset(covered)

    @staticmethod
    def _obstacles(ground_rings: tuple[ModuleRing, ...]) -> list[Rectangle]:
        """Collects the areas of the ground floor walls, posts and doors the stair keeps clear of.

        Args:
            ground_rings are the rings of the ground floor.

        Returns:
            One area per wall or post, doors with the clearance around them. Stairs in front of
            the doors are left out because they stand outside.
        """
        obstacles: list[Rectangle] = []
        for ring in ground_rings:
            for placement in ring.placements:
                if isinstance(placement.module, StairModule):
                    continue
                area: Rectangle = StairPlacer.rectangle_of(
                    placement, placement.module.width, placement.module.depth
                )
                if isinstance(placement.module, DoorModule):
                    area = (
                        area[0] - DOOR_CLEARANCE,
                        area[1] - DOOR_CLEARANCE,
                        area[2] + DOOR_CLEARANCE,
                        area[3] + DOOR_CLEARANCE,
                    )
                obstacles.append(area)
        return obstacles
