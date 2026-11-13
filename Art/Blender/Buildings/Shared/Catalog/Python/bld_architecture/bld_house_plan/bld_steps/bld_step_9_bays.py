# Copyright (c) 2026 Emberfall. All Rights Reserved.
"""Step 9 helper: ring of a level -> ring with bays, walls swapped against a box that sticks out."""

__author__ = "Matthias Stefan"
__version__ = "0.1.0"

import random
from dataclasses import replace

from bld_modules import (
    TOLERANCE,
    ArcFloorModule,
    ArcWallModule,
    ArcWindowModule,
    BayWallModule,
    FloorModule,
    PillarModule,
    PostModule,
    WallModule,
    WindowModule,
)

from ...bld_create_info import LevelsCreateInfo
from ...bld_style import ModuleAtlas
from ..bld_house_plan import ModulePlacement, ModuleRing
from .bld_step_2_outline import OutlineRing

# front direction (-Y turned by n quarter turns) per rotation, the width axis is the next one
_FRONT: tuple[tuple[int, int], ...] = ((0, -1), (1, 0), (0, 1), (-1, 0))


class BayPlacer:
    """Swaps a wall of a level for a bay: a front wall, two short side walls and a floor strip."""

    def __init__(self, atlas: ModuleAtlas) -> None:
        """Creates a bay placer.

        Args:
            atlas: Modules the placer may use, it needs a bay wall and a floor strip as deep as the bay wall is wide.

        Returns:
            None.
        """
        self._atlas: ModuleAtlas = atlas
        return None

    def place(
        self,
        ring: ModuleRing,
        outline: OutlineRing,
        slab_elevation: float,
        levels_info: LevelsCreateInfo,
        random_source: random.Random,
    ) -> tuple[ModuleRing, tuple[ModulePlacement, ...]]:
        """Swaps some walls of a ring against bays.

        Args:
            ring is the ring of the level, posts, walls and windows, at the wall elevation.
            outline is the outline the ring was filled from, the bays keep away from its corners.
            slab_elevation is the height of the bottom of the floor slabs of the level in m.
            levels_info is the rules for the bays.
            random_source is the random stream for the choices, separate from all other steps.

        Returns:
            The ring with the bays and the floor strips under them. Both unchanged and empty if
            the atlas lacks a bay wall or a fitting floor strip or no wall fits a bay.
        """
        bay_wall: BayWallModule | None = self._find_bay_wall()
        if bay_wall is None or levels_info.max_bays == 0:
            return ring, ()
        strip: FloorModule | None = self._find_strip(bay_wall.width)
        posts: list[PostModule] = [
            module
            for module in self._atlas.modules_of(PostModule)
            if isinstance(module, PostModule) and not isinstance(module, PillarModule)
        ]
        if strip is None or not posts:
            return ring, ()

        corners: list[tuple[float, float]] = [
            (float(corner.point[0]), float(corner.point[1])) for corner in outline.corners
        ]
        candidates: list[int] = [
            index
            for index, placement in enumerate(ring.placements)
            if self._fits(placement, corners, levels_info)
        ]
        random_source.shuffle(candidates)

        chosen: list[int] = []
        for index in candidates:
            if len(chosen) >= levels_info.max_bays:
                break
            if random_source.random() >= levels_info.bay_chance:
                continue
            center: tuple[float, float] = ring.placements[index].position
            if any(
                self._distance(center, ring.placements[other].position) < levels_info.min_bay_distance
                for other in chosen
            ):
                continue
            chosen.append(index)

        placements: list[ModulePlacement] = [
            placement for index, placement in enumerate(ring.placements) if index not in chosen
        ]
        floor: list[ModulePlacement] = []
        for index in sorted(chosen):
            round_bay: tuple[list[ModulePlacement], list[ModulePlacement]] | None = None
            if random_source.random() < levels_info.round_bay_chance:
                round_bay = self._build_round(ring.placements[index], slab_elevation, random_source)
            if round_bay is None:
                round_bay = self._build(
                    ring.placements[index], bay_wall, strip, posts[0], slab_elevation, random_source
                )
            bay_placements, bay_floor = round_bay
            placements.extend(bay_placements)
            floor.extend(bay_floor)
        return ModuleRing(tuple(placements)), tuple(floor)

    def _fits(
        self,
        placement: ModulePlacement,
        corners: list[tuple[float, float]],
        levels_info: LevelsCreateInfo,
    ) -> bool:
        """Tests whether a placed module may be swapped for a bay.

        Args:
            placement is the placed module.
            corners are the corner points of the outline in m.
            levels_info is the rules for the bays.

        Returns:
            @c True if it is a wall or window of an allowed width whose ends keep the corner
            distance, otherwise @c False.
        """
        module = placement.module
        if not isinstance(module, (WallModule, WindowModule)) or isinstance(module, BayWallModule):
            return False
        if not any(abs(module.width - width) <= TOLERANCE for width in levels_info.bay_widths):
            return False
        width_direction: tuple[int, int] = _FRONT[(placement.rotation_steps + 1) % 4]
        for sign in (-1, 1):
            end: tuple[float, float] = (
                placement.position[0] + sign * width_direction[0] * module.width * 0.5,
                placement.position[1] + sign * width_direction[1] * module.width * 0.5,
            )
            if any(
                self._distance(end, corner) < levels_info.min_bay_corner_distance - TOLERANCE
                for corner in corners
            ):
                return False
        return True

    def _build(
        self,
        wall: ModulePlacement,
        bay_wall: BayWallModule,
        strip: FloorModule,
        post: PostModule,
        slab_elevation: float,
        random_source: random.Random,
    ) -> tuple[list[ModulePlacement], list[ModulePlacement]]:
        """Builds the bay that replaces one wall.

        Args:
            wall is the wall or window that is replaced.
            bay_wall is the short wall for the two sides.
            strip is the floor strip under the bay, one per meter of width.
            post is the post on the two outer corners.
            slab_elevation is the height of the bottom of the floor slabs in m.
            random_source is the random stream that picks the window of the front.

        Returns:
            The walls and posts of the bay and its floor strips. The front is a window if the
            atlas has one of that width, otherwise the replaced module again.
        """
        width: float = wall.module.width
        rotation: int = wall.rotation_steps
        normal: tuple[int, int] = _FRONT[rotation]
        tangent: tuple[int, int] = _FRONT[(rotation + 1) % 4]
        depth: float = bay_wall.width
        center_x, center_y = wall.position

        windows: list[WindowModule] = [
            module
            for module in self._atlas.modules_of(WindowModule)
            if isinstance(module, WindowModule) and abs(module.width - width) <= TOLERANCE
        ]
        front_module = random_source.choice(windows) if windows else wall.module

        placements: list[ModulePlacement] = [
            replace(
                wall,
                module=front_module,
                position=(center_x + normal[0] * depth, center_y + normal[1] * depth),
            )
        ]
        for sign, side_rotation in ((-1, (rotation + 3) % 4), (1, (rotation + 1) % 4)):
            side_x: float = center_x + sign * tangent[0] * width * 0.5
            side_y: float = center_y + sign * tangent[1] * width * 0.5
            placements.append(
                replace(
                    wall,
                    module=bay_wall,
                    position=(side_x + normal[0] * depth * 0.5, side_y + normal[1] * depth * 0.5),
                    rotation_steps=side_rotation,
                )
            )
            placements.append(
                replace(
                    wall,
                    module=post,
                    position=(side_x + normal[0] * depth, side_y + normal[1] * depth),
                    rotation_steps=0,
                )
            )

        floor: list[ModulePlacement] = []
        for step in range(round(width / strip.width)):
            offset: float = (step - (width / strip.width - 1.0) * 0.5) * strip.width
            floor.append(
                ModulePlacement(
                    strip,
                    (
                        center_x + tangent[0] * offset + normal[0] * depth * 0.5,
                        center_y + tangent[1] * offset + normal[1] * depth * 0.5,
                    ),
                    rotation,
                    slab_elevation,
                )
            )
        return placements, floor

    def _build_round(
        self,
        wall: ModulePlacement,
        slab_elevation: float,
        random_source: random.Random,
    ) -> tuple[list[ModulePlacement], list[ModulePlacement]] | None:
        """Builds the round bay that replaces one wall.

        The curved front takes the place of the wall and bulges out of the wall line, so it
        needs no side walls and no posts, the posts at the ends of the wall stay.

        Args:
            wall is the wall or window that is replaced.
            slab_elevation is the height of the bottom of the floor slabs in m.
            random_source is the random stream that picks the front.

        Returns:
            The curved front and the floor slab under it, @c None if the atlas has no curved
            wall or no curved floor as wide as the wall.
        """
        width: float = wall.module.width
        fronts: list[ArcWallModule] = [
            module
            for module in self._atlas.modules_of(ArcWallModule)
            if isinstance(module, ArcWallModule) and abs(module.width - width) <= TOLERANCE
        ]
        floors: list[ArcFloorModule] = [
            module
            for module in self._atlas.modules_of(ArcFloorModule)
            if isinstance(module, ArcFloorModule) and abs(module.width - width) <= TOLERANCE
        ]
        if not fronts or not floors:
            return None
        # a window if the replaced module was one or by chance, a plain wall stays plain otherwise
        windows: list[ArcWallModule] = [front for front in fronts if isinstance(front, ArcWindowModule)]
        plain: list[ArcWallModule] = [front for front in fronts if not isinstance(front, ArcWindowModule)]
        pool: list[ArcWallModule] = windows if windows and (not plain or random_source.random() < 0.7) else plain
        front_module: ArcWallModule = random_source.choice(pool)
        floor_module: ArcFloorModule = floors[0]

        normal: tuple[int, int] = _FRONT[wall.rotation_steps]
        floor_placement: ModulePlacement = ModulePlacement(
            floor_module,
            (
                wall.position[0] + normal[0] * floor_module.depth * 0.5,
                wall.position[1] + normal[1] * floor_module.depth * 0.5,
            ),
            wall.rotation_steps,
            slab_elevation,
        )
        return [replace(wall, module=front_module)], [floor_placement]

    def _find_bay_wall(self) -> BayWallModule | None:
        """Finds the short wall for the sides of a bay.

        Returns:
            The first bay wall of the atlas, @c None if there is none.
        """
        for module in self._atlas.modules_of(BayWallModule):
            if isinstance(module, BayWallModule) and not isinstance(module, ArcWallModule):
                return module
        return None

    def _find_strip(self, bay_depth: float) -> FloorModule | None:
        """Finds the floor strip that fills a bay, one meter wide.

        Args:
            bay_depth is the depth of the bay in m.

        Returns:
            A floor module 1 m wide and as deep as the bay, @c None if the atlas has none.
        """
        for module in self._atlas.modules_of(FloorModule):
            if (
                isinstance(module, FloorModule)
                and abs(module.width - 1.0) <= TOLERANCE
                and abs(module.depth - bay_depth) <= TOLERANCE
            ):
                return module
        return None

    @staticmethod
    def _distance(first: tuple[float, float], second: tuple[float, float]) -> float:
        """Measures the distance between two points.

        Args:
            first is the first point in m.
            second is the second point in m.

        Returns:
            Distance in m.
        """
        return ((first[0] - second[0]) ** 2 + (first[1] - second[1]) ** 2) ** 0.5
