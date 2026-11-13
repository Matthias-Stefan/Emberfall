# Copyright (c) 2026 Emberfall. All Rights Reserved.
"""Builds the mesh of a diagonal wall or window by turning a straight one."""

__author__ = "Matthias Stefan"
__version__ = "0.1.0"

import math

import bmesh
import mathutils

from bld_modules import DiagonalWallModule, DiagonalWindowModule, WallModule, WindowModule

from .bld_base_module_builder import BaseModuleBuilder
from .bld_wall_builder import WallBuilder
from .bld_window_builder import WindowBuilder


class DiagonalWallBuilder(BaseModuleBuilder):
    """Builds a straight wall or window and turns it 45 degrees around Z."""

    def __init__(
        self,
        module: DiagonalWallModule,
        close_top: bool = False,
        close_bottom: bool = False,
        close_ends: bool = False,
    ) -> None:
        """Creates a diagonal wall builder.

        Args:
            module: Diagonal wall or window module providing the dimensions.
            close_top: Whether the top faces are generated.
            close_bottom: Whether the bottom faces are generated.
            close_ends: Whether the faces on both module ends are generated.

        Returns:
            None.
        """
        super().__init__(module, close_top, close_bottom, close_ends)
        self._diagonal: DiagonalWallModule = module

    def build(self) -> bmesh.types.BMesh:
        """Builds the straight module and turns it.

        Returns:
            A new BMesh in m, the origin in the middle of the wall, floor at Z = 0, the front looks south-east.
            The caller owns it and must call free() on it.
        """
        module: DiagonalWallModule = self._diagonal
        straight: BaseModuleBuilder
        if isinstance(module, DiagonalWindowModule):
            straight = WindowBuilder(
                WindowModule(
                    width=module.width,
                    height=module.height,
                    depth=module.depth,
                    opening_width=module.opening_width,
                    opening_height=module.opening_height,
                    sill_height=module.sill_height,
                ),
                self._close_top,
                self._close_bottom,
                self._close_ends,
            )
        else:
            straight = WallBuilder(
                WallModule(width=module.width, height=module.height, depth=module.depth),
                self._close_top,
                self._close_bottom,
                self._close_ends,
            )
        bm: bmesh.types.BMesh = straight.build()
        bmesh.ops.rotate(
            bm,
            cent=(0.0, 0.0, 0.0),
            matrix=mathutils.Matrix.Rotation(math.radians(45.0), 3, "Z"),
            verts=list(bm.verts),
        )
        return bm
