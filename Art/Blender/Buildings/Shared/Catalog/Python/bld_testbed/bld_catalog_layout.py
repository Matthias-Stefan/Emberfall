# Copyright (c) 2026 Emberfall. All Rights Reserved.
"""Lays out the module catalog as rows of closed modules."""

__author__ = "Matthias Stefan"
__version__ = "0.1.0"

import bpy

from bld_blender import MeshWriter
from bld_module_builder import BaseModuleBuilder
from bld_modules import BaseWallModule

from .bld_footprint_colors import footprint_colors

CatalogRow = list[tuple[BaseWallModule, BaseModuleBuilder]]


class CatalogLayout:
    """Places catalog modules in rows along -X, one row per module kind."""

    def __init__(
        self,
        writer: MeshWriter,
        rows: list[CatalogRow],
        start_x: float = -10.0,
        start_y: float = 0.0,
        row_spacing: float = 10.0,
        module_gap: float = 1.0,
    ) -> None:
        """Creates a catalog layout.

        Args:
writer: Writer the module objects are created with.
            rows: One row per module kind, each a list of module and builder pairs.
            start_x: X of the first module edge in m, rows grow towards -X from here.
            start_y: Y of the first row in m, further rows grow towards +Y.
            row_spacing: Distance between rows along Y in m.
            module_gap: Gap between neighbouring modules along X in m.

        Returns:
            None.
        """
        self._writer: MeshWriter = writer
        self._rows: list[CatalogRow] = rows
        self._start_x: float = start_x
        self._start_y: float = start_y
        self._row_spacing: float = row_spacing
        self._module_gap: float = module_gap
        return None

    def place(self) -> list[bpy.types.Object]:
        """Builds and places all modules of all rows.

        Returns:
            The created objects in row order.
        """
        placed_objects: list[bpy.types.Object] = []

        for row_index, row in enumerate(self._rows):
            row_y: float = self._start_y + row_index * self._row_spacing
            cursor_x: float = 0.0

            for module, builder in row:
                module_object: bpy.types.Object = self._writer.write(
                    module.name, builder.build(), footprint_colors.color_for(module)
                )
                module_object.location.x = self._start_x - (cursor_x + module.width * 0.5)
                module_object.location.y = row_y
                cursor_x += module.width + self._module_gap
                placed_objects.append(module_object)

        return placed_objects
