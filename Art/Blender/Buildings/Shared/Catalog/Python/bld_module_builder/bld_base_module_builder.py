# Copyright (c) 2026 Emberfall. All Rights Reserved.
"""Base class of all module builders, with the shared face and cell helpers."""

__author__ = "Matthias Stefan"
__version__ = "0.1.0"

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

    @abstractmethod
    def build(self) -> bmesh.types.BMesh:
        """Builds the module geometry.

        Returns:
            A new BMesh in m, centered in X and Y, floor at Z = 0.
            The caller owns it and must call free() on it.
        """

    @staticmethod
    def _add_box(
        bm: bmesh.types.BMesh,
        minimum: tuple[float, float, float],
        maximum: tuple[float, float, float],
    ) -> None:
        """Adds one closed box with outward faces.

        Args:
            bm: BMesh to add the box to.
            minimum: Corner with the smallest coordinates in m.
            maximum: Corner with the largest coordinates in m.

        Returns:
            None.
        """
        created: dict = bmesh.ops.create_cube(bm, size=1.0)
        corners: list[bmesh.types.BMVert] = created["verts"]
        bmesh.ops.scale(
            bm,
            vec=(maximum[0] - minimum[0], maximum[1] - minimum[1], maximum[2] - minimum[2]),
            verts=corners,
        )
        bmesh.ops.translate(
            bm,
            vec=(
                (minimum[0] + maximum[0]) * 0.5,
                (minimum[1] + maximum[1]) * 0.5,
                (minimum[2] + maximum[2]) * 0.5,
            ),
            verts=corners,
        )
        return None

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
