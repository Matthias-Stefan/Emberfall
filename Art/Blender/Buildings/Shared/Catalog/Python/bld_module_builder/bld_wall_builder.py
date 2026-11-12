# Copyright (c) 2026 Emberfall. All Rights Reserved.
"""Builds the mesh of a plain wall module."""

__author__ = "Matthias Stefan"
__version__ = "0.1.0"

import bmesh

from bld_modules import TOLERANCE, WallModule

from .bld_base_module_builder import BaseModuleBuilder


class WallBuilder(BaseModuleBuilder):
    """Builds a wall as two parallel faces, optionally closed at the top, bottom and ends."""

    def __init__(
        self,
        module: WallModule,
        close_top: bool = False,
        close_bottom: bool = False,
        close_ends: bool = False,
    ) -> None:
        """Creates a wall builder.

        Args:
            module: Wall module providing the dimensions.
            close_top: Whether the top face is generated.
            close_bottom: Whether the bottom face is generated.
            close_ends: Whether the faces on both module ends are generated.

        Returns:
            None.
        """
        super().__init__(module, close_top, close_bottom, close_ends)
        self._wall_module: WallModule = module

    def build(self) -> bmesh.types.BMesh:
        """Builds the wall from one grid cell.

        Returns:
            A new BMesh in m, centered in X and Y, floor at Z = 0.
            The caller owns it and must call free() on it.
        """
        wall: WallModule = self._wall_module
        bm: bmesh.types.BMesh = bmesh.new()

        half_width: float = wall.width * 0.5
        half_depth: float = wall.depth * 0.5
        # the whole wall is a single cell, so it touches every side
        self._add_cell(
            bm, -half_width, half_width, 0.0, wall.height, half_depth,
            is_top_row=True, is_bottom_row=True, is_left_column=True, is_right_column=True,
        )
        # welds the shared vertices of the closing faces
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=TOLERANCE)
        return bm
