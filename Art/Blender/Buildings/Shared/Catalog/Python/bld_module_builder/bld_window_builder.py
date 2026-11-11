# Copyright (c) 2026 Emberfall. All Rights Reserved.

import bmesh

from bld_modules import WindowModule, TOLERANCE

from .bld_base_module_builder import BaseModuleBuilder


class WindowBuilder(BaseModuleBuilder):
    """Builds a wall with a window opening as a quad grid with reveals."""

    def __init__(
        self,
        module: WindowModule,
        close_top: bool = False,
        close_bottom: bool = False,
        close_ends: bool = False,
    ) -> None:
        """Creates a window builder.

        Args:
            module: Window module providing wall and opening dimensions.
            close_top: Whether the top faces are generated.
            close_bottom: Whether the bottom faces are generated.
            close_ends: Whether the faces on both module ends are generated.

        Returns:
            None.
        """
        super().__init__(module, close_top, close_bottom, close_ends)
        self._window_module: WindowModule = module
        return None

    def build(self) -> bmesh.types.BMesh:
        """Builds front and back cells around the opening plus its reveals.

        Returns:
            A new BMesh in m, centered in X and Y, floor at Z = 0.
            The caller owns it and must call free() on it.
        """
        window: WindowModule = self._window_module
        bm: bmesh.types.BMesh = bmesh.new()

        half_width: float = window.width * 0.5
        half_depth: float = window.depth * 0.5
        opening_left: float = -half_width + window.resolved_opening_offset
        opening_right: float = opening_left + window.opening_width
        sill_height: float = window.sill_height
        head_height: float = window.head_height

        # grid lines, the opening edges run through the whole wall like loop cuts
        columns: list[float] = [opening_left, opening_right]
        if opening_left + half_width > TOLERANCE:
            columns.insert(0, -half_width)
        if half_width - opening_right > TOLERANCE:
            columns.append(half_width)
        # row 0 is the wall below the sill, row 1 the opening, row 2 the lintel
        rows: list[float] = [0.0, sill_height, head_height, window.height]

        opening_column: int = columns.index(opening_left)
        last_column: int = len(columns) - 2
        last_row: int = len(rows) - 2

        for column in range(len(columns) - 1):
            for row in range(len(rows) - 1):
                if column == opening_column and row == 1:
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
                (opening_left, -half_depth, sill_height),
                (opening_left, half_depth, sill_height),
                (opening_left, half_depth, head_height),
                (opening_left, -half_depth, head_height),
            ])
        # reveal on the right side of the opening, faces -X
        if opening_column + 2 < len(columns):
            self._add_face(bm, [
                (opening_right, -half_depth, sill_height),
                (opening_right, -half_depth, head_height),
                (opening_right, half_depth, head_height),
                (opening_right, half_depth, sill_height),
            ])
        # reveal above the opening, the underside of the lintel, faces -Z
        self._add_face(bm, [
            (opening_left, -half_depth, head_height),
            (opening_left, half_depth, head_height),
            (opening_right, half_depth, head_height),
            (opening_right, -half_depth, head_height),
        ])
        # reveal below the opening, the window sill, faces +Z
        self._add_face(bm, [
            (opening_left, -half_depth, sill_height),
            (opening_right, -half_depth, sill_height),
            (opening_right, half_depth, sill_height),
            (opening_left, half_depth, sill_height),
        ])

        # every face has its own vertices so far, this welds the shared ones
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=TOLERANCE)
        return bm