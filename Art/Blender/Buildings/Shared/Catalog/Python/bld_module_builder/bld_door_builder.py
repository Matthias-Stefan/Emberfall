# Copyright (c) 2026 Emberfall. All Rights Reserved.
"""Builds the mesh of a door module."""

__author__ = "Matthias Stefan"
__version__ = "0.1.0"

import bmesh

from bld_modules import TOLERANCE, DoorModule

from .bld_base_module_builder import BaseModuleBuilder


class DoorBuilder(BaseModuleBuilder):
    """Builds a wall with a door opening as a quad grid with reveals."""

    def __init__(
        self,
        module: DoorModule,
        close_top: bool = False,
        close_bottom: bool = False,
        close_ends: bool = False,
    ) -> None:
        """Creates a door builder.

        Args:
            module: Door module providing wall and opening dimensions.
            close_top: Whether the top faces are generated.
            close_bottom: Whether the bottom faces are generated.
            close_ends: Whether the faces on both module ends are generated.

        Returns:
            None.
        """
        super().__init__(module, close_top, close_bottom, close_ends)
        self._door_module: DoorModule = module

    def build(self) -> bmesh.types.BMesh:
        """Builds front and back cells around the opening plus its reveals.

        Returns:
            A new BMesh in m, centered in X and Y, floor at Z = 0.
            The caller owns it and must call free() on it.
        """
        door: DoorModule = self._door_module
        bm: bmesh.types.BMesh = bmesh.new()

        half_width: float = door.width * 0.5
        half_depth: float = door.depth * 0.5
        opening_left: float = -half_width + door.resolved_opening_offset
        opening_right: float = opening_left + door.opening_width
        head_height: float = door.head_height

        # grid lines, the opening edges run through the whole wall like loop cuts
        columns: list[float] = [opening_left, opening_right]
        if opening_left + half_width > TOLERANCE:
            columns.insert(0, -half_width)
        if half_width - opening_right > TOLERANCE:
            columns.append(half_width)
        rows: list[float] = [0.0, head_height, door.height]

        opening_column: int = columns.index(opening_left)
        last_column: int = len(columns) - 2
        last_row: int = len(rows) - 2

        for column in range(len(columns) - 1):
            for row in range(len(rows) - 1):
                if column == opening_column and row == 0:
                    continue  # the opening itself
                self._add_cell(
                    bm, columns[column], columns[column + 1], rows[row], rows[row + 1], half_depth,
                    is_top_row=row == last_row,
                    is_bottom_row=row == 0,
                    is_left_column=column == 0,
                    is_right_column=column == last_column,
                )

        # reveal on the left side of the opening, faces +X
        if opening_column > 0:
            self._add_face(bm, [
                (opening_left, -half_depth, 0.0),
                (opening_left, half_depth, 0.0),
                (opening_left, half_depth, head_height),
                (opening_left, -half_depth, head_height),
            ])
        # reveal on the right side of the opening, faces -X
        if opening_column + 2 < len(columns):
            self._add_face(bm, [
                (opening_right, -half_depth, 0.0),
                (opening_right, -half_depth, head_height),
                (opening_right, half_depth, head_height),
                (opening_right, half_depth, 0.0),
            ])
        # reveal above the opening, the underside of the lintel, faces -Z
        self._add_face(bm, [
            (opening_left, -half_depth, head_height),
            (opening_left, half_depth, head_height),
            (opening_right, half_depth, head_height),
            (opening_right, -half_depth, head_height),
        ])

        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=TOLERANCE)
        return bm
