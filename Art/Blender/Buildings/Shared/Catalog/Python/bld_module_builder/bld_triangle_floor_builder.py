# Copyright (c) 2026 Emberfall. All Rights Reserved.
"""Builds the mesh of a triangular slab."""

__author__ = "Matthias Stefan"
__version__ = "0.1.0"

import bmesh

from bld_modules import TriangleFloorModule

from .bld_base_module_builder import BaseModuleBuilder


class TriangleFloorBuilder(BaseModuleBuilder):
    """Builds a closed slab in the shape of a right triangle."""

    def __init__(self, module: TriangleFloorModule) -> None:
        """Creates a triangle floor builder.

        Args:
            module: Triangle floor module providing the dimensions.

        Returns:
            None.
        """
        super().__init__(module)
        self._triangle: TriangleFloorModule = module
        return None

    def build(self) -> bmesh.types.BMesh:
        """Builds the triangle and extrudes it to the slab thickness.

        Returns:
            A new BMesh in m, centered in X and Y, bottom at Z = 0, top at the thickness.
            The right angle lies in the north-west corner.
            The caller owns it and must call free() on it.
        """
        floor: TriangleFloorModule = self._triangle
        half_width: float = floor.width * 0.5
        half_depth: float = floor.depth * 0.5
        bm: bmesh.types.BMesh = bmesh.new()
        outline: list[tuple[float, float]] = [
            (-half_width, -half_depth),
            (half_width, half_depth),
            (-half_width, half_depth),
        ]
        bottom = bm.faces.new([bm.verts.new((x, y, 0.0)) for x, y in outline])
        extruded: dict = bmesh.ops.extrude_face_region(bm, geom=[bottom])
        top_vertices = [item for item in extruded["geom"] if isinstance(item, bmesh.types.BMVert)]
        bmesh.ops.translate(bm, vec=(0.0, 0.0, floor.height), verts=top_vertices)
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        return bm
