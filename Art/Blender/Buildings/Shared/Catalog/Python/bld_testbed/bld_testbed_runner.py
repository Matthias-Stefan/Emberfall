# Copyright (c) 2026 Emberfall. All Rights Reserved.

import bpy

from bld_architecture import Architect, ModuleAtlas
from bld_blender import MeshWriter
from bld_module_builder import DoorBuilder, WallBuilder
from bld_presets import (
    door_200x30x260,
    door_400x30x260,
    wall_100x30x260,
    wall_200x30x260,
    wall_400x30x260,
    wall_600x30x260,
)

from .bld_catalog_layout import CatalogLayout, CatalogRow
from .bld_house_grid_layout import HouseGridLayout
from .bld_house_set import default_house_set


class TestbedRunner:
    """Rebuilds the testbed: catalog modules in -X, house grid in +X."""

    def __init__(
        self,
        modules_collection: bpy.types.Collection,
        houses_collection: bpy.types.Collection,
    ) -> None:
        """Creates a testbed runner.

        Args:
            modules_collection: Fresh collection the catalog objects are written into.
            houses_collection: Fresh collection the house objects are written into.

        Returns:
            None.
        """
        self._modules_collection: bpy.types.Collection = modules_collection
        self._houses_collection: bpy.types.Collection = houses_collection
        return None

    def run(self) -> None:
        """Prints all modules, then builds and places catalog and houses.

        Returns:
            None.
        """
        catalog_rows: list[CatalogRow] = self._build_catalog_rows()
        self._print_catalog(catalog_rows)

        module_writer: MeshWriter = MeshWriter(self._modules_collection)
        CatalogLayout(module_writer, catalog_rows).place()

        house_writer: MeshWriter = MeshWriter(self._houses_collection)
        architect: Architect = Architect(ModuleAtlas())
        HouseGridLayout(house_writer, architect, default_house_set).place()
        return None

    def _build_catalog_rows(self) -> list[CatalogRow]:
        """Pairs every preset with its builder, one row per module kind.

        Returns:
            Wall row first, door row second.
        """
        wall_row: CatalogRow = [
            (wall_100x30x260, WallBuilder(wall_100x30x260)),
            (wall_200x30x260, WallBuilder(wall_200x30x260)),
            (wall_400x30x260, WallBuilder(wall_400x30x260)),
            (wall_600x30x260, WallBuilder(wall_600x30x260)),
        ]
        door_row: CatalogRow = [
            (door_200x30x260, DoorBuilder(door_200x30x260)),
            (door_400x30x260, DoorBuilder(door_400x30x260)),
        ]
        return [wall_row, door_row]

    def _print_catalog(self, catalog_rows: list[CatalogRow]) -> None:
        """Prints one line per module to the console.

        Args:
            catalog_rows: Rows to print.

        Returns:
            None.
        """
        for row in catalog_rows:
            for module, _ in row:
                print(
                    f"testbed: {module.name} ({type(module).__name__}) "
                    f"{module.width} x {module.depth} x {module.height} m"
                )
        return None
