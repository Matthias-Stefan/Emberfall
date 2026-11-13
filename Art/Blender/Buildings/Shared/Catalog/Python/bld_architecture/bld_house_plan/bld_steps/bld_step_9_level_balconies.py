# Copyright (c) 2026 Emberfall. All Rights Reserved.
"""Step 9 helper: rings of a level -> rings with a new door, a railed platform in front of it and pillars below."""

__author__ = "Matthias Stefan"
__version__ = "0.1.0"

import math
import random
from dataclasses import dataclass, replace

from bld_modules import (
    TOLERANCE,
    ArcWallModule,
    BayWallModule,
    DiagonalWallModule,
    DoorModule,
    PillarModule,
    RailModule,
    WallModule,
    WindowModule,
)

from ...bld_create_info import LevelsCreateInfo
from ...bld_style import ModuleAtlas
from ..bld_house_plan import ModulePlacement, ModuleRing
from .bld_step_1_footprint import Footprint
from .bld_step_2_outline import OutlineRing
from .bld_step_6_stairs import Rectangle, StairPlacer
from .bld_step_8_floor import FloorPlanner

Cell = tuple[int, int]
Point = tuple[float, float]

# front direction (-Y turned by n quarter turns) per rotation, the width axis is the next one
_FRONT: tuple[tuple[int, int], ...] = ((0, -1), (1, 0), (0, 1), (-1, 0))

_PILLAR_INSET: float = 0.25
"""Distance in m from the edges of the platform to the center of a corner pillar."""
_PILLAR_CLEARANCE: float = 0.25
"""Distance in m a pillar keeps from the cells of the building below, the foundation sticks out."""
_WALL_CLEARANCE: float = 0.25
"""Distance in m the platform keeps clear of walls that do not stand on its back edge, the bays."""


@dataclass(frozen=True)
class _Platform:
    """One planned balcony before it is built."""

    cells: frozenset[Cell]
    """Cells of the platform."""
    pillars: tuple[Point, ...]
    """Centers of the pillars that stand on the ground in m."""


class LevelBalconyPlacer:
    """Swaps a wall of a level for a door and builds a railed platform on pillars in front of it."""

    def __init__(self, atlas: ModuleAtlas, floor_planner: FloorPlanner) -> None:
        """Creates a level balcony placer.

        Args:
            atlas: Doors, rails and pillars the placer may use.
            floor_planner: Lays the floor slabs of the platform.

        Returns:
            None.
        """
        self._atlas: ModuleAtlas = atlas
        self._floor_planner: FloorPlanner = floor_planner
        return None

    def place(
        self,
        rings: tuple[ModuleRing, ...],
        outlines: tuple[OutlineRing, ...],
        upper_cells: frozenset[Cell],
        lower_cells: frozenset[Cell],
        ground_obstacles: tuple[Rectangle, ...],
        slab_elevation: float,
        wall_elevation: float,
        levels_info: LevelsCreateInfo,
        random_source: random.Random,
    ) -> tuple[tuple[ModuleRing, ...], ModuleRing | None, tuple[ModulePlacement, ...]]:
        """Builds balconies for a level.

        Args:
            rings are the rings of the level, walls, windows and bays at the wall elevation.
            outlines are the outline rings the rings were filled from, balconies keep away from their corners.
            upper_cells are the cells of the level.
            lower_cells are the cells of the level below, the pillars stand outside of them.
            ground_obstacles are the areas on the ground a pillar must keep clear of, e.g. stairs.
            slab_elevation is the height of the bottom of the floor slabs in m, the pillars reach up to it.
            wall_elevation is the height of the top of the floor slabs in m, doors and rails stand on it.
            levels_info is the rules for the balconies.
            random_source is the random stream for the choices, separate from all other steps.

        Returns:
            The rings with the new doors, a ring with the rails and pillars and the floor slabs of the platforms.
            Rings unchanged, no extra ring and no slabs if no balcony fits or the atlas lacks a door or a rail.
        """
        rails: list[RailModule] = [
            module for module in self._atlas.modules_of(RailModule) if isinstance(module, RailModule)
        ]
        door_widths: list[float] = sorted(
            {module.width for module in self._atlas.modules_of(DoorModule)}
        )
        if (
            levels_info.max_balconies == 0
            or not rails
            or not door_widths
            or self._floor_planner.slab_height is None
            or random_source.random() >= levels_info.balcony_chance
        ):
            return rings, None, ()

        corners: list[Point] = [
            (float(corner.point[0]), float(corner.point[1]))
            for outline in outlines
            for corner in outline.corners
        ]
        bay_sides: list[ModulePlacement] = [
            placement
            for ring in rings
            for placement in ring.placements
            if isinstance(placement.module, BayWallModule)
        ]
        candidates: list[tuple[int, int]] = [
            (ring_index, index)
            for ring_index, ring in enumerate(rings)
            for index, placement in enumerate(ring.placements)
            if self._fits(placement, door_widths, corners, bay_sides, levels_info)
        ]
        random_source.shuffle(candidates)

        new_rings: list[list[ModulePlacement]] = [list(ring.placements) for ring in rings]
        wall_rectangles: list[tuple[int, int, Rectangle]] = [
            (ring_index, index, self.rectangle_of_wall(placement))
            for ring_index, ring in enumerate(rings)
            for index, placement in enumerate(ring.placements)
        ]
        taken: set[Cell] = set()
        extras: list[ModulePlacement] = []
        floor: list[ModulePlacement] = []
        built: int = 0
        for ring_index, index in candidates:
            if built >= levels_info.max_balconies:
                break
            door_wall: ModulePlacement = rings[ring_index].placements[index]
            platform: _Platform | None = self._choose(
                door_wall,
                upper_cells,
                lower_cells,
                taken,
                [
                    rectangle
                    for other_ring, other_index, rectangle in wall_rectangles
                    if (other_ring, other_index) != (ring_index, index)
                ],
                ground_obstacles,
                slab_elevation,
                levels_info,
                random_source,
            )
            if platform is None:
                continue

            doors: list[DoorModule] = [
                module
                for module in self._atlas.modules_of(DoorModule)
                if isinstance(module, DoorModule) and abs(module.width - door_wall.module.width) <= TOLERANCE
            ]
            new_rings[ring_index][index] = replace(door_wall, module=random_source.choice(doors))
            extras.extend(self._rails(platform.cells, upper_cells, rails, wall_elevation))
            extras.extend(self._pillars(platform.pillars, slab_elevation))
            floor.extend(
                self._floor_planner.lay(Footprint(seed=0, main_cells=platform.cells), slab_elevation)
            )
            taken |= platform.cells
            built += 1

        if built == 0:
            return rings, None, ()
        return (
            tuple(ModuleRing(tuple(placements)) for placements in new_rings),
            ModuleRing(tuple(extras)),
            tuple(floor),
        )

    def _fits(
        self,
        placement: ModulePlacement,
        door_widths: list[float],
        corners: list[Point],
        bay_sides: list[ModulePlacement],
        levels_info: LevelsCreateInfo,
    ) -> bool:
        """Tests whether a placed module may be swapped for a door.

        Args:
            placement is the placed module.
            door_widths are the widths in m the atlas has doors for.
            corners are the corner points of the outline in m.
            bay_sides are the short side walls of all bays of the level.
            levels_info is the rules for the balconies.

        Returns:
            @c True if it is a wall or window as wide as a door whose ends keep the corner distance
            and that is no front wall of a bay, otherwise @c False.
        """
        module = placement.module
        if not isinstance(module, (WallModule, WindowModule)) or isinstance(module, BayWallModule):
            return False
        if not any(abs(module.width - width) <= TOLERANCE for width in door_widths):
            return False
        width_direction: tuple[int, int] = _FRONT[(placement.rotation_steps + 1) % 4]
        normal: tuple[int, int] = _FRONT[placement.rotation_steps]
        for side in bay_sides:
            # the side walls of a bay stand behind its front wall, a neighbour of a bay has them in front
            offset_x: float = side.position[0] - placement.position[0]
            offset_y: float = side.position[1] - placement.position[1]
            behind: float = -(offset_x * normal[0] + offset_y * normal[1])
            along: float = abs(offset_x * width_direction[0] + offset_y * width_direction[1])
            if behind > TOLERANCE and abs(along - module.width * 0.5) <= TOLERANCE:
                return False
        for sign in (-1, 1):
            end: Point = (
                placement.position[0] + sign * width_direction[0] * module.width * 0.5,
                placement.position[1] + sign * width_direction[1] * module.width * 0.5,
            )
            if any(
                math.dist(end, corner) < levels_info.min_bay_corner_distance - TOLERANCE
                for corner in corners
            ):
                return False
        return True

    def _choose(
        self,
        door_wall: ModulePlacement,
        upper_cells: frozenset[Cell],
        lower_cells: frozenset[Cell],
        taken: set[Cell],
        wall_rectangles: list[Rectangle],
        ground_obstacles: tuple[Rectangle, ...],
        slab_elevation: float,
        levels_info: LevelsCreateInfo,
        random_source: random.Random,
    ) -> _Platform | None:
        """Picks a platform for a door out of all sizes that fit, bigger ones more likely.

        Args:
            door_wall is the wall that becomes the door.
            upper_cells are the cells of the level.
            lower_cells are the cells of the level below.
            taken are the cells of the platforms already planned.
            wall_rectangles are the areas of all other walls, posts and windows of the level.
            ground_obstacles are the areas on the ground the pillars keep clear of.
            slab_elevation is the height the pillars must reach in m.
            levels_info is the rules for the balconies.
            random_source is the random stream for the choice.

        Returns:
            The platform, @c None if no size fits.
        """
        width: int = round(door_wall.module.width)
        normal: tuple[int, int] = _FRONT[door_wall.rotation_steps]
        tangent: tuple[int, int] = _FRONT[(door_wall.rotation_steps + 1) % 4]
        start: Point = (
            door_wall.position[0] - tangent[0] * width * 0.5,
            door_wall.position[1] - tangent[1] * width * 0.5,
        )
        pillar_module: PillarModule | None = self._find_pillar(slab_elevation)

        options: list[_Platform] = []
        for depth in range(levels_info.balcony_min_depth, levels_info.balcony_max_depth + 1):
            for extra_left in range(levels_info.balcony_max_extra_width + 1):
                for extra_right in range(levels_info.balcony_max_extra_width + 1):
                    cells: frozenset[Cell] = self._cells_of(
                        start, tangent, normal, -extra_left, width + extra_right, depth
                    )
                    if not self._is_free(cells, normal, upper_cells, taken):
                        continue
                    if self._hits_walls(cells, wall_rectangles):
                        continue
                    pillars: tuple[Point, ...] | None = self._pillars_for(
                        start, tangent, normal, -extra_left, width + extra_right, depth,
                        lower_cells, ground_obstacles, pillar_module, levels_info.pillar_spacing,
                    )
                    if pillars is None:
                        continue
                    options.append(_Platform(cells, pillars))
        if not options:
            return None
        return random_source.choices(options, weights=[len(option.cells) for option in options])[0]

    @staticmethod
    def _cells_of(
        start: Point,
        tangent: tuple[int, int],
        normal: tuple[int, int],
        first: int,
        last: int,
        depth: int,
    ) -> frozenset[Cell]:
        """Collects the cells of a rectangle that stands out from a wall line.

        Args:
            start is the point on the wall line where the door begins in m.
            tangent is the unit direction along the wall.
            normal is the unit direction away from the building.
            first is the first cell along the wall, counted from start, may be negative.
            last is the end of the rectangle along the wall, counted from start, exclusive.
            depth is the extent away from the building in cells.

        Returns:
            The cells of the rectangle.
        """
        cells: set[Cell] = set()
        for along in range(first, last):
            for away in range(depth):
                center_x: float = start[0] + tangent[0] * (along + 0.5) + normal[0] * (away + 0.5)
                center_y: float = start[1] + tangent[1] * (along + 0.5) + normal[1] * (away + 0.5)
                cells.add((math.floor(center_x), math.floor(center_y)))
        return frozenset(cells)

    @staticmethod
    def _is_free(
        cells: frozenset[Cell],
        normal: tuple[int, int],
        upper_cells: frozenset[Cell],
        taken: set[Cell],
    ) -> bool:
        """Tests whether a platform touches the building only with its back edge.

        Args:
            cells are the cells of the platform.
            normal is the unit direction away from the building.
            upper_cells are the cells of the level.
            taken are the cells of the platforms already planned.

        Returns:
            @c True if no cell is built on, no cell touches another platform and every cell that
            touches the building does so with the edge at the wall, otherwise @c False.
        """
        if cells & upper_cells or cells & taken:
            return False
        back_cells: int = 0
        for cell_x, cell_y in cells:
            for step_x, step_y in _FRONT:
                neighbor: Cell = (cell_x + step_x, cell_y + step_y)
                if neighbor in taken:
                    return False
                if neighbor in upper_cells:
                    if (step_x, step_y) != (-normal[0], -normal[1]):
                        return False
                    back_cells += 1
        # one back edge per cell of the row at the wall, none missing
        row: int = sum(
            1
            for cell_x, cell_y in cells
            if (cell_x - normal[0], cell_y - normal[1]) not in cells
        )
        return back_cells == row

    @staticmethod
    def rectangle_of_wall(placement: ModulePlacement) -> Rectangle:
        """Measures the area a placed wall, post or window covers on the plan.

        Args:
            placement is the placed module, a curved wall also covers the area of its bulge.

        Returns:
            The rectangle in m.
        """
        module = placement.module
        if isinstance(module, DiagonalWallModule):
            # the box around a wall that runs at 45 degrees
            half: float = (module.width + module.depth) / (2.0 * math.sqrt(2.0))
            return (
                placement.position[0] - half,
                placement.position[1] - half,
                placement.position[0] + half,
                placement.position[1] + half,
            )
        if not isinstance(module, ArcWallModule):
            return StairPlacer.rectangle_of(placement, module.width, module.depth)
        normal: tuple[int, int] = _FRONT[placement.rotation_steps]
        # from the inner face of the wall to the outermost point of the arc
        shifted: ModulePlacement = replace(
            placement,
            position=(
                placement.position[0] + normal[0] * module.bulge * 0.5,
                placement.position[1] + normal[1] * module.bulge * 0.5,
            ),
        )
        return StairPlacer.rectangle_of(shifted, module.width, module.depth + module.bulge)

    @staticmethod
    def _hits_walls(cells: frozenset[Cell], wall_rectangles: list[Rectangle]) -> bool:
        """Tests whether a platform runs into walls that do not stand on its back edge.

        Args:
            cells are the cells of the platform.
            wall_rectangles are the areas of all other walls, posts and windows of the level.

        Returns:
            @c True if one of them overlaps the platform, the edge at the wall excepted.
        """
        shrink: float = _WALL_CLEARANCE
        for cell_x, cell_y in cells:
            area: Rectangle = (
                cell_x + shrink, cell_y + shrink, cell_x + 1.0 - shrink, cell_y + 1.0 - shrink
            )
            if any(StairPlacer.overlaps(area, rectangle) for rectangle in wall_rectangles):
                return True
        return False

    @staticmethod
    def _pillars_for(
        start: Point,
        tangent: tuple[int, int],
        normal: tuple[int, int],
        first: int,
        last: int,
        depth: int,
        lower_cells: frozenset[Cell],
        ground_obstacles: tuple[Rectangle, ...],
        pillar_module: PillarModule | None,
        spacing: float,
    ) -> tuple[Point, ...] | None:
        """Plans the pillars under the front edge of a platform.

        Args:
            start is the point on the wall line where the door begins in m.
            tangent is the unit direction along the wall.
            normal is the unit direction away from the building.
            first is the first cell along the wall, counted from start.
            last is the end of the platform along the wall, counted from start, exclusive.
            depth is the extent of the platform away from the building in cells.
            lower_cells are the cells of the level below, a pillar over them is not needed.
            ground_obstacles are the areas on the ground a pillar must keep clear of.
            pillar_module is the pillar of the right height, @c None if the atlas has none.
            spacing is the largest distance in m between two pillars.

        Returns:
            Pillar centers in m, empty if the building below carries the whole platform.
            @c None if a pillar is needed but cannot stand.
        """
        length: int = last - first
        count: int = math.ceil(length / spacing) + 1
        offsets: list[int] = sorted({round(index * length / (count - 1)) for index in range(count)})

        pillars: list[Point] = []
        for offset in offsets:
            # the pillar sits under the platform, away from the front edge and, at the ends, from the side edge
            inset_along: float = _PILLAR_INSET if offset == 0 else -_PILLAR_INSET if offset == length else 0.0
            center: Point = (
                start[0] + tangent[0] * (first + offset + inset_along) + normal[0] * (depth - _PILLAR_INSET),
                start[1] + tangent[1] * (first + offset + inset_along) + normal[1] * (depth - _PILLAR_INSET),
            )
            if (math.floor(center[0]), math.floor(center[1])) in lower_cells:
                continue  # the building below carries it
            if pillar_module is None:
                return None
            half: float = pillar_module.width * 0.5
            area: Rectangle = (center[0] - half, center[1] - half, center[0] + half, center[1] + half)
            for cell_x, cell_y in lower_cells:
                inflated: Rectangle = (
                    cell_x - _PILLAR_CLEARANCE, cell_y - _PILLAR_CLEARANCE,
                    cell_x + 1.0 + _PILLAR_CLEARANCE, cell_y + 1.0 + _PILLAR_CLEARANCE,
                )
                if StairPlacer.overlaps(area, inflated):
                    return None
            if any(StairPlacer.overlaps(area, obstacle) for obstacle in ground_obstacles):
                return None
            pillars.append(center)
        return tuple(pillars)

    def _pillars(self, centers: tuple[Point, ...], slab_elevation: float) -> list[ModulePlacement]:
        """Places the pillars on the ground.

        Args:
            centers are the pillar centers in m.
            slab_elevation is the height the pillars reach in m.

        Returns:
            One placement per pillar, empty if there are none.
        """
        pillar: PillarModule | None = self._find_pillar(slab_elevation)
        if pillar is None:
            return []
        return [ModulePlacement(pillar, center, 0, 0.0) for center in centers]

    def _find_pillar(self, height: float) -> PillarModule | None:
        """Finds the pillar that reaches exactly up to the platform.

        Args:
            height is the height from the ground to the bottom of the floor slabs in m.

        Returns:
            The pillar, @c None if the atlas has none of that height.
        """
        for module in self._atlas.modules_of(PillarModule):
            if isinstance(module, PillarModule) and abs(module.height - height) <= TOLERANCE:
                return module
        return None

    @staticmethod
    def _rails(
        cells: frozenset[Cell],
        upper_cells: frozenset[Cell],
        rails: list[RailModule],
        elevation: float,
    ) -> list[ModulePlacement]:
        """Lays rails along every edge of the platform that does not touch the building or another cell.

        Args:
            cells are the cells of the platform.
            upper_cells are the cells of the level, the building has walls there.
            rails are the rail modules, a run is filled with the widest that fit first.
            elevation is the height of the top of the floor slabs in m.

        Returns:
            The rail placements, their fronts face away from the platform.
        """
        # edges per direction and line: the along coordinate of every edge cell
        runs: dict[tuple[int, int], list[int]] = {}
        for cell_x, cell_y in cells:
            for direction, (step_x, step_y) in enumerate(_FRONT):
                neighbor: Cell = (cell_x + step_x, cell_y + step_y)
                if neighbor in cells or neighbor in upper_cells:
                    continue
                line: int = cell_y + (1 if step_y > 0 else 0) if step_x == 0 else cell_x + (1 if step_x > 0 else 0)
                along: int = cell_x if step_x == 0 else cell_y
                runs.setdefault((direction, line), []).append(along)

        placements: list[ModulePlacement] = []
        for (direction, line), alongs in sorted(runs.items()):
            alongs.sort()
            run_start: int = alongs[0]
            previous: int = alongs[0]
            for along in [*alongs[1:], None]:
                if along is not None and along == previous + 1:
                    previous = along
                    continue
                placements.extend(
                    LevelBalconyPlacer._tile(direction, line, run_start, previous + 1, rails, elevation)
                )
                if along is not None:
                    run_start = previous = along
        return placements

    @staticmethod
    def _tile(
        direction: int,
        line: int,
        run_start: int,
        run_end: int,
        rails: list[RailModule],
        elevation: float,
    ) -> list[ModulePlacement]:
        """Fills one straight run of rail with modules.

        Args:
            direction is the rotation of the rails, their front faces that way.
            line is the grid line the run lies on.
            run_start is the along coordinate where the run begins in m.
            run_end is the along coordinate where the run ends in m.
            rails are the rail modules.
            elevation is the height of the rails above the ground in m.

        Returns:
            The rail placements, widest modules first from the start of the run.
        """
        along_x: bool = _FRONT[direction][0] == 0
        placements: list[ModulePlacement] = []
        offset: float = float(run_start)
        while run_end - offset > TOLERANCE:
            rail: RailModule = next(
                (module for module in rails if module.width <= run_end - offset + TOLERANCE), rails[-1]
            )
            center: float = offset + rail.width * 0.5
            position: Point = (center, float(line)) if along_x else (float(line), center)
            placements.append(ModulePlacement(rail, position, direction, elevation))
            offset += rail.width
        return placements
