# Copyright (c) 2026 Emberfall. All Rights Reserved.
"""Builds the mesh of a floor module."""

__author__ = "Matthias Stefan"
__version__ = "0.1.0"

import bmesh

from bld_modules import FloorModule
from .bld_base_module_builder import BaseModuleBuilder


class FloorBuilder(BaseModuleBuilder):
    """Builds a plain closed slab."""

    def __init__(self, module: FloorModule) -> None:
        """Creates a floor builder.

        Args:
            module: Floor module providing the slab dimensions.

        Returns:
            None.
        """
        super().__init__(module)
        self._floor_module: FloorModule = module
        return None

    def build(self) -> bmesh.types.BMesh:
        """Builds a closed box from the slab dimensions.

        Returns:
            A new BMesh in m, centered in X and Y, bottom at Z = 0, top at the thickness.
            The caller owns it and must call free() on it.
        """
        floor: FloorModule = self._floor_module
        bm: bmesh.types.BMesh = bmesh.new()

        # unit cube around the origin, scaled to size, then lifted so the bottom sits at Z = 0
        bmesh.ops.create_cube(bm, size=1.0)
        bmesh.ops.scale(bm, vec=(floor.width, floor.depth, floor.height), verts=bm.verts)
        bmesh.ops.translate(bm, vec=(0.0, 0.0, floor.height * 0.5), verts=bm.verts)
        return bm
