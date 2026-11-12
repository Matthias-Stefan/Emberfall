# Copyright (c) 2026 Emberfall. All Rights Reserved.
"""Step 4: rings with posts and walls -> rings with doors and windows swapped in for walls."""

__author__ = "Matthias Stefan"
__version__ = "0.1.0"

import random
from dataclasses import replace

from bld_modules import TOLERANCE, DoorModule, OpeningWallModule, WallModule, WindowModule

from ...bld_create_info import OpeningCreateInfo
from ...bld_style import ModuleAtlas
from ..bld_house_plan import ModulePlacement, ModuleRing


class OpeningPlacer:
    """Replaces walls by doors and windows of the same size."""

    def __init__(self, atlas: ModuleAtlas) -> None:
        """Creates an opening placer.

        Args:
            atlas: Modules the placer may swap in.

        Returns:
            None.
        """
        self._atlas: ModuleAtlas = atlas
        return None

    def place(
        self,
        ring: ModuleRing,
        door_budget: int,
        openings: OpeningCreateInfo,
        random_source: random.Random,
    ) -> ModuleRing:
        """Swaps walls of a ring against doors and windows.

        Args:
            ring: Ring whose walls may be swapped.
            door_budget: Most doors this ring may receive.
            openings: Rules for the window chance and the spacing.
            random_source: Random stream for the choices, separate from the wall widths.

        Returns:
            New ring with the same slots, some walls replaced by openings.
        """
        # (index in ring.placements, wall), posts are skipped
        walls: list[tuple[int, WallModule]] = [
            (index, placement.module)
            for index, placement in enumerate(ring.placements)
            if isinstance(placement.module, WallModule)
        ]
        placements: list[ModulePlacement] = list(ring.placements)
        taken: list[int] = []  # positions in walls, not in ring.placements

        # doors first, on shuffled walls
        door_count: int = 0
        wall_order: list[int] = list(range(len(walls)))
        random_source.shuffle(wall_order)
        for wall_position in wall_order:
            if door_count >= door_budget:
                break
            if not self._has_clearance(
                wall_position, taken, len(walls), openings.min_walls_between_openings
            ):
                continue
            ring_index, wall = walls[wall_position]
            doors: list[OpeningWallModule] = self._find_same_width(wall, DoorModule)
            if not doors:
                continue
            placements[ring_index] = replace(
                placements[ring_index], module=random_source.choice(doors)
            )
            taken.append(wall_position)
            door_count += 1

        # windows on the remaining walls in walking order
        for wall_position, (ring_index, wall) in enumerate(walls):
            if wall_position in taken:
                continue
            if not self._has_clearance(
                wall_position, taken, len(walls), openings.min_walls_between_openings
            ):
                continue
            windows: list[OpeningWallModule] = self._find_same_width(wall, WindowModule)
            if not windows:
                continue
            if random_source.random() >= openings.window_chance:
                continue
            placements[ring_index] = replace(
                placements[ring_index], module=random_source.choice(windows)
            )
            taken.append(wall_position)
        return ModuleRing(tuple(placements))

    @staticmethod
    def _has_clearance(
        wall_position: int, taken: list[int], wall_count: int, min_walls_between: int
    ) -> bool:
        """Tests whether enough plain walls separate a wall from all taken walls.

        Args:
            wall_position: Position of the wall in the wall list of the ring.
            taken: Positions of the walls that are already openings.
            wall_count: Number of walls in the ring, the ring is closed.
            min_walls_between: Plain walls that must stand between two openings.

        Returns:
            True if every taken wall is more than min_walls_between steps away,
            otherwise False.
        """
        for other_position in taken:
            gap: int = abs(wall_position - other_position)
            ring_gap: int = min(gap, wall_count - gap)
            if ring_gap <= min_walls_between:
                return False
        return True

    def _find_same_width(
        self, wall: WallModule, opening_type: type[OpeningWallModule]
    ) -> list[OpeningWallModule]:
        """Finds all openings that replace a wall one to one.

        Args:
            wall: Wall that should be swapped.
            opening_type: Kind of opening to look for, e.g. DoorModule.

        Returns:
            Atlas modules of the given kind with the same width as the wall,
            empty if there is none. Depth and height already match, the style
            checks that for every module.
        """
        return [
            module
            for module in self._atlas.modules_of(opening_type)
            if isinstance(module, opening_type)
            and abs(module.width - wall.width) <= TOLERANCE
        ]
