# Copyright (c) 2026 Emberfall. All Rights Reserved.
"""Places one house per create info and seed on a grid."""

__author__ = "Matthias Stefan"
__version__ = "0.1.0"

import math
import random
from dataclasses import replace

import bpy

from bld_architecture import Architect, Footprint, HousePlan, ModulePlacement
from bld_blender import SharedMeshCache
from bld_house_builder import FoundationBuilder
from bld_module_builder import (
    BaseModuleBuilder,
    DoorBuilder,
    FloorBuilder,
    PostBuilder,
    StairBuilder,
    WallBuilder,
    WindowBuilder,
)
from bld_modules import (
    BaseSlotModule,
    DoorModule,
    FloorModule,
    PostModule,
    StairModule,
    WindowModule,
)

from .bld_footprint_builder import FootprintBuilder
from .bld_house_colors import house_colors
from .bld_house_part import HousePart
from .bld_house_set import HouseSet
from .bld_house_writers import HouseWriters


class HouseGridLayout:
    """Places one house per create info and seed: rows are infos, columns are seeds."""

    def __init__(
        self,
        houses_collection: bpy.types.Collection,
        architect: Architect,
        house_set: HouseSet,
        start_x: float = 10.0,
        start_y: float = 0.0,
        pitch_x: float = 30.0,
        pitch_y: float = 30.0,
    ) -> None:
        """Creates a house grid layout.

        Args:
            houses_collection: Collection that gets one sub collection per house.
            architect: Architect that designs the house plans.
            house_set: Create infos and seeds to build.
            start_x: X of the first column in m, columns grow towards +X.
            start_y: Y of the first row in m, rows grow towards +Y.
            pitch_x: Distance between columns in m.
            pitch_y: Distance between rows in m.

        Returns:
            None.
        """
        self._houses_collection: bpy.types.Collection = houses_collection
        self._cache: SharedMeshCache = SharedMeshCache()
        self._architect: Architect = architect
        self._house_set: HouseSet = house_set
        self._start_x: float = start_x
        self._start_y: float = start_y
        self._pitch_x: float = pitch_x
        self._pitch_y: float = pitch_y

    def place(self) -> list[bpy.types.Object]:
        """Designs, builds and places all houses.

        Returns:
            The created objects in row order.
        """
        placed_objects: list[bpy.types.Object] = []

        for row_index, base_info in enumerate(self._house_set.create_infos):
            random_seeds: list[int] = [
                random.SystemRandom().randrange(100_000_000)
                for _ in range(self._house_set.random_seed_count)
            ]
            seeds: list[int] = [*self._house_set.fixed_seeds, *random_seeds]

            for column_index, seed in enumerate(seeds):
                plan: HousePlan = self._architect.design(replace(base_info, seed=seed))
                footprint: Footprint = plan.footprint
                builder: FootprintBuilder = FootprintBuilder(footprint)
                writers: HouseWriters = HouseWriters(
                    self._houses_collection, f"house_r{row_index}_s{seed}", self._cache
                )

                house_object: bpy.types.Object = writers.writer_for(HousePart.FOOTPRINT).write(
                    f"house_r{row_index}_s{seed}_main",
                    builder.build_main(),
                    house_colors.main,
                )
                house_object.location.x = self._start_x + column_index * self._pitch_x
                house_object.location.y = self._start_y + row_index * self._pitch_y
                placed_objects.append(house_object)

                for extension_index in range(len(footprint.extension_cells)):
                    extension_object: bpy.types.Object = writers.writer_for(HousePart.FOOTPRINT).write(
                        f"house_r{row_index}_s{seed}_ext{extension_index}",
                        builder.build_extension(extension_index),
                        house_colors.extension,
                    )
                    extension_object.location.x = house_object.location.x
                    extension_object.location.y = house_object.location.y
                    placed_objects.append(extension_object)

                if plan.foundation is not None:
                    foundation_builder: FoundationBuilder = FoundationBuilder(plan.foundation)
                    for ring_index in range(foundation_builder.ring_count):
                        foundation_object: bpy.types.Object = writers.writer_for(
                            HousePart.FOUNDATION
                        ).write(
                            f"house_r{row_index}_s{seed}_foundation{ring_index}",
                            foundation_builder.build_ring(ring_index),
                            house_colors.foundation,
                        )
                        foundation_object.location.x = house_object.location.x
                        foundation_object.location.y = house_object.location.y
                        placed_objects.append(foundation_object)

                # posts and walls, rotated so the module front (-Y) faces outward
                placement_count: int = 0
                all_placements: list[ModulePlacement] = [
                    placement for ring in plan.rings for placement in ring.placements
                ]
                all_placements.extend(plan.floor)
                for placement in all_placements:
                    module: BaseSlotModule = placement.module
                    # the same module always has the same geometry, so all objects share one mesh
                    module_object: bpy.types.Object = writers.writer_for(
                        HousePart.of(module)
                    ).write_shared(
                        f"house_r{row_index}_s{seed}_{module.name}_{placement_count}",
                        module.name,
                        self._builder_for(module).build,
                        house_colors.color_for(module),
                    )
                    module_object.location.x = house_object.location.x + placement.position[0]
                    module_object.location.y = house_object.location.y + placement.position[1]
                    module_object.location.z = placement.elevation
                    module_object.rotation_euler.z = placement.rotation_steps * math.pi * 0.5
                    placed_objects.append(module_object)
                    placement_count += 1

                writers.remove_empty_parts()

                kind: str = "fixed" if seed in self._house_set.fixed_seeds else "random"
                total_cells: int = len(footprint.main_cells) + sum(
                    len(cells) for cells in footprint.extension_cells
                )
                print(
                    f"houses: row {row_index} seed {seed} ({kind}) "
                    f"main {self._size_of(footprint)}, "
                    f"{len(footprint.extension_cells)} extensions, "
                    f"{total_cells} cells, {placement_count} placements"
                )

        return placed_objects

    @staticmethod
    def _size_of(footprint: Footprint) -> str:
        width: int = max(cell_x for cell_x, _ in footprint.main_cells) + 1
        depth: int = max(cell_y for _, cell_y in footprint.main_cells) + 1
        return f"{width}x{depth}"

    @staticmethod
    def _builder_for(module: BaseSlotModule) -> BaseModuleBuilder:
        if isinstance(module, PostModule):
            return PostBuilder(module)
        if isinstance(module, DoorModule):
            return DoorBuilder(module)
        if isinstance(module, WindowModule):
            return WindowBuilder(module)
        if isinstance(module, StairModule):
            return StairBuilder(module)
        if isinstance(module, FloorModule):
            return FloorBuilder(module)
        return WallBuilder(module)  # type: ignore[arg-type]
