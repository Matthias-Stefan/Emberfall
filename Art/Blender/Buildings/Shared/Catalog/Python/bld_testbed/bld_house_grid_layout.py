# Copyright (c) 2026 Emberfall. All Rights Reserved.

import random
from dataclasses import replace

import bpy

from bld_architecture import Architect, Footprint, footprint_colors
from bld_blender import MeshWriter

from .bld_footprint_builder import FootprintBuilder
from .bld_house_set import HouseSet


class HouseGridLayout:
    """Places one house per create info and seed: rows are infos, columns are seeds."""

    def __init__(
        self,
        writer: MeshWriter,
        architect: Architect,
        house_set: HouseSet,
        start_x: float = 10.0,
        start_y: float = 0.0,
        pitch_x: float = 20.0,
        pitch_y: float = 20.0,
    ) -> None:
        """Creates a house grid layout.

        Args:
            writer: Writer the house objects are created with.
            architect: Architect that designs the footprints.
            house_set: Create infos and seeds to build.
            start_x: X of the first column in m, columns grow towards +X.
            start_y: Y of the first row in m, rows grow towards +Y.
            pitch_x: Distance between columns in m.
            pitch_y: Distance between rows in m.

        Returns:
            None.
        """
        self._writer: MeshWriter = writer
        self._architect: Architect = architect
        self._house_set: HouseSet = house_set
        self._start_x: float = start_x
        self._start_y: float = start_y
        self._pitch_x: float = pitch_x
        self._pitch_y: float = pitch_y
        return None

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
                footprint: Footprint = self._architect.design(replace(base_info, seed=seed))
                builder: FootprintBuilder = FootprintBuilder(footprint)

                house_object: bpy.types.Object = self._writer.write(
                    f"house_r{row_index}_s{seed}_main",
                    builder.build_main(),
                    footprint_colors.main,
                )
                house_object.color = footprint_colors.main
                house_object.location.x = self._start_x + column_index * self._pitch_x
                house_object.location.y = self._start_y + row_index * self._pitch_y
                placed_objects.append(house_object)

                kind: str = "fixed" if seed in self._house_set.fixed_seeds else "random"
                print(
                    f"houses: row {row_index} seed {seed} ({kind}) "
                    f"main {self._size_of(footprint)} = {len(footprint.main_cells)} cells"
                )

        return placed_objects

    @staticmethod
    def _size_of(footprint: Footprint) -> str:
        width: int = max(cell_x for cell_x, _ in footprint.main_cells) + 1
        depth: int = max(cell_y for _, cell_y in footprint.main_cells) + 1
        return f"{width}x{depth}"
