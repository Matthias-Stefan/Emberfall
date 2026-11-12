# Copyright (c) 2026 Emberfall. All Rights Reserved.
"""Builds flat floor quads from the cells of a footprint."""

__author__ = "Matthias Stefan"
__version__ = "0.1.0"

import bmesh

from bld_architecture import Footprint


class FootprintBuilder:
    """Builds flat floor quads from the cells of a footprint, one quad per cell."""

    def __init__(self, footprint: Footprint, floor_offset: float = 0.01) -> None:
        """Creates a footprint builder.

        Args:
            footprint: Footprint to display.
            floor_offset: Height of the quads above Z = 0 in m, avoids z-fighting.

        Returns:
            None.
        """
        self._footprint: Footprint = footprint
        self._floor_offset: float = floor_offset

    def build_main(self) -> bmesh.types.BMesh:
        """Builds the quads of the main building.

        Returns:
            A new BMesh in m, one cell is 1 m x 1 m.
            The caller owns it and must call free() on it.
        """
        return self._build_cells(self._footprint.main_cells)

    def build_extension(self, extension_index: int) -> bmesh.types.BMesh:
        """Builds the quads of one extension.

        Args:
            extension_index: Index of the extension in placement order.

        Returns:
            A new BMesh in m, one cell is 1 m x 1 m.
            The caller owns it and must call free() on it.
        """
        return self._build_cells(self._footprint.extension_cells[extension_index])

    def _build_cells(self, cells: frozenset[tuple[int, int]]) -> bmesh.types.BMesh:
        """Builds one quad per cell, facing up.

        Args:
            cells: Cell indices as (x, y) tuples.

        Returns:
            A new BMesh, the caller must free it.
        """
        bm: bmesh.types.BMesh = bmesh.new()
        height: float = self._floor_offset
        for cell_x, cell_y in sorted(cells):
            bm.faces.new([
                bm.verts.new((cell_x, cell_y, height)),
                bm.verts.new((cell_x + 1, cell_y, height)),
                bm.verts.new((cell_x + 1, cell_y + 1, height)),
                bm.verts.new((cell_x, cell_y + 1, height)),
            ])
        return bm
