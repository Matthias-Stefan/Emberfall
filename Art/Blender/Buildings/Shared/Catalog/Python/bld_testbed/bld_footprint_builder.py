# Copyright (c) 2026 Emberfall. All Rights Reserved.
# bld_testbed/bld_footprint_builder.py

from bld_architecture import Footprint
from bld_geometry import MeshData


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
        return None

    def build_main(self) -> MeshData:
        """Builds the quads of the main building.

        Returns:
            Mesh data in m, one cell is 1 m x 1 m.
        """
        return self._build_cells(self._footprint.main_cells)

    def build_extension(self, extension_index: int) -> MeshData:
        """Builds the quads of one extension.

        Args:
            extension_index: Index of the extension in placement order.

        Returns:
            Mesh data in m, one cell is 1 m x 1 m.
        """
        return self._build_cells(self._footprint.extension_cells[extension_index])

    def _build_cells(self, cells: frozenset[tuple[int, int]]) -> MeshData:
        result: MeshData = MeshData()
        height: float = self._floor_offset
        for cell_x, cell_y in sorted(cells):
            result.add_quad(
                (cell_x, cell_y, height),
                (cell_x + 1, cell_y, height),
                (cell_x + 1, cell_y + 1, height),
                (cell_x, cell_y + 1, height),
            )
        return result
