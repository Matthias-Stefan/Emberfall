# Copyright (c) 2026 Emberfall. All Rights Reserved.
# bld_module_builder/bld_base_module_builder.py

from abc import ABCMeta, abstractmethod

import bmesh

from bld_modules import BaseModule


class BaseModuleBuilder(metaclass=ABCMeta):
    """Builds geometry for one module."""

    def __init__(
        self,
        module: BaseModule,
        close_top: bool = False,
        close_bottom: bool = False,
        close_ends: bool = False,
    ) -> None:
        """Creates a builder.

        Args:
            module: Module to build the geometry for.
            close_top: Whether the top faces are generated.
            close_bottom: Whether the bottom faces are generated.
            close_ends: Whether the faces on the left and right module end are generated.

        Returns:
            None.
        """
        self._module: BaseModule = module
        self._close_top: bool = close_top
        self._close_bottom: bool = close_bottom
        self._close_ends: bool = close_ends
        return None

    @abstractmethod
    def build(self) -> bmesh.types.BMesh:
        """Builds the module geometry.

        Returns:
            A new BMesh in m, centered in X and Y, floor at Z = 0.
            The caller owns it and must call free() on it.
        """

    @staticmethod
    def _add_face(bm: bmesh.types.BMesh, points: list[tuple[float, float, float]]) -> None:
        """Adds one face from loose points, counter-clockwise seen from outside.

        Args:
            bm: BMesh to add the face to.
            points: Corner positions in m.

        Returns:
            None.
        """
        bm.faces.new([bm.verts.new(point) for point in points])
        return None

    def _add_cell(
        self,
        bm: bmesh.types.BMesh,
        x_min: float,
        x_max: float,
        z_min: float,
        z_max: float,
        half_depth: float,
        is_top_row: bool,
        is_bottom_row: bool,
        is_left_column: bool,
        is_right_column: bool,
    ) -> None:
        """Adds front and back of one grid cell, plus the faces the close flags ask for.

        Args:
            bm: BMesh to add the faces to.
            x_min: Left cell edge in m.
            x_max: Right cell edge in m.
            z_min: Bottom cell edge in m.
            z_max: Top cell edge in m.
            half_depth: Half of the wall thickness in m.
            is_top_row: Whether the cell touches the top of the module.
            is_bottom_row: Whether the cell touches the floor.
            is_left_column: Whether the cell touches the left module end.
            is_right_column: Whether the cell touches the right module end.

        Returns:
            None.
        """
        # front face, normal -Y
        self._add_face(bm, [
            (x_min, -half_depth, z_min),
            (x_max, -half_depth, z_min),
            (x_max, -half_depth, z_max),
            (x_min, -half_depth, z_max),
        ])
        # back face, normal +Y
        self._add_face(bm, [
            (x_min, half_depth, z_min),
            (x_min, half_depth, z_max),
            (x_max, half_depth, z_max),
            (x_max, half_depth, z_min),
        ])
        if is_top_row and self._close_top:  # normal +Z
            self._add_face(bm, [
                (x_min, -half_depth, z_max),
                (x_max, -half_depth, z_max),
                (x_max, half_depth, z_max),
                (x_min, half_depth, z_max),
            ])
        if is_bottom_row and self._close_bottom:  # normal -Z
            self._add_face(bm, [
                (x_min, -half_depth, z_min),
                (x_min, half_depth, z_min),
                (x_max, half_depth, z_min),
                (x_max, -half_depth, z_min),
            ])
        if is_left_column and self._close_ends:  # normal -X
            self._add_face(bm, [
                (x_min, half_depth, z_min),
                (x_min, -half_depth, z_min),
                (x_min, -half_depth, z_max),
                (x_min, half_depth, z_max),
            ])
        if is_right_column and self._close_ends:  # normal +X
            self._add_face(bm, [
                (x_max, -half_depth, z_min),
                (x_max, half_depth, z_min),
                (x_max, half_depth, z_max),
                (x_max, -half_depth, z_max),
            ])
        return None