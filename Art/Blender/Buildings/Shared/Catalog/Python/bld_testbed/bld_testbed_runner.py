# Copyright (c) 2026 Emberfall. All Rights Reserved.
"""Rebuilds the testbed: catalog modules in -X, house grid in +X."""

__author__ = "Matthias Stefan"
__version__ = "0.1.0"

import bpy

from bld_architecture import Architect, ModuleAtlas, Style
from bld_blender import MeshWriter
from bld_module_builder import (
    DoorBuilder,
    FloorBuilder,
    PostBuilder,
    RailBuilder,
    StairBuilder,
    WallBuilder,
    WindowBuilder,
)
from bld_presets import (
    door_200x30x260,
    door_400x30x260,
    floor_50x50x30,
    floor_100x50x30,
    floor_100x100x30,
    post_34x34x260,
    post_40x40x260,
    rail_100x8x90,
    rail_200x8x90,
    stair_80x400x290_16s_open,
    stair_100x60x40_2s_open,
    stair_100x60x40_2s_solid,
    stair_200x60x40_2s_open,
    stair_200x60x40_2s_solid,
    stair_200x90x60_3s_open_rail,
    stair_200x90x60_3s_solid_rail,
    stair_400x60x40_2s_open,
    stair_400x60x40_2s_solid,
    wall_100x30x260,
    wall_200x30x260,
    wall_400x30x260,
    wall_600x30x260,
    window_100x30x260,
    window_200x30x260,
    window_400x30x260,
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

    def run(self) -> None:
        """Prints all modules, then builds and places catalog and houses.

        Returns:
            None.
        """
        catalog_rows: list[CatalogRow] = self._build_catalog_rows()
        self._print_catalog(catalog_rows)

        module_writer: MeshWriter = MeshWriter(self._modules_collection)
        CatalogLayout(module_writer, catalog_rows).place()

        atlas: ModuleAtlas = ModuleAtlas(
            [module for row in catalog_rows for module, _ in row]
        )
        architect: Architect = Architect(Style("default", atlas))
        HouseGridLayout(self._houses_collection, architect, default_house_set).place()

    def _build_catalog_rows(self) -> list[CatalogRow]:
        """Pairs every preset with its builder, one row per module kind.

        The catalog shows every module closed on all sides, so the flags are set here.

        Returns:
            Wall row, door row, window row, post row, stair row, floor row and rail row.
        """
        closed: dict[str, bool] = {"close_top": True, "close_bottom": True, "close_ends": True}

        wall_row: CatalogRow = [
            (wall_100x30x260, WallBuilder(wall_100x30x260, **closed)),
            (wall_200x30x260, WallBuilder(wall_200x30x260, **closed)),
            (wall_400x30x260, WallBuilder(wall_400x30x260, **closed)),
            (wall_600x30x260, WallBuilder(wall_600x30x260, **closed)),
        ]
        door_row: CatalogRow = [
            (door_200x30x260, DoorBuilder(door_200x30x260, **closed)),
            (door_400x30x260, DoorBuilder(door_400x30x260, **closed)),
        ]
        window_row: CatalogRow = [
            (window_100x30x260, WindowBuilder(window_100x30x260, **closed)),
            (window_200x30x260, WindowBuilder(window_200x30x260, **closed)),
            (window_400x30x260, WindowBuilder(window_400x30x260, **closed)),
        ]
        post_row: CatalogRow = [
            (post_34x34x260, PostBuilder(post_34x34x260)),
            (post_40x40x260, PostBuilder(post_40x40x260)),
        ]
        stair_row: CatalogRow = [
            (stair_100x60x40_2s_solid, StairBuilder(stair_100x60x40_2s_solid)),
            (stair_100x60x40_2s_open, StairBuilder(stair_100x60x40_2s_open)),
            (stair_200x60x40_2s_solid, StairBuilder(stair_200x60x40_2s_solid)),
            (stair_200x60x40_2s_open, StairBuilder(stair_200x60x40_2s_open)),
            (stair_200x90x60_3s_solid_rail, StairBuilder(stair_200x90x60_3s_solid_rail)),
            (stair_200x90x60_3s_open_rail, StairBuilder(stair_200x90x60_3s_open_rail)),
            (stair_400x60x40_2s_solid, StairBuilder(stair_400x60x40_2s_solid)),
            (stair_400x60x40_2s_open, StairBuilder(stair_400x60x40_2s_open)),
            (stair_80x400x290_16s_open, StairBuilder(stair_80x400x290_16s_open)),
        ]
        floor_row: CatalogRow = [
            (floor_100x100x30, FloorBuilder(floor_100x100x30)),
            (floor_100x50x30, FloorBuilder(floor_100x50x30)),
            (floor_50x50x30, FloorBuilder(floor_50x50x30)),
        ]
        rail_row: CatalogRow = [
            (rail_100x8x90, RailBuilder(rail_100x8x90)),
            (rail_200x8x90, RailBuilder(rail_200x8x90)),
        ]
        return [wall_row, door_row, window_row, post_row, stair_row, floor_row, rail_row]

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
