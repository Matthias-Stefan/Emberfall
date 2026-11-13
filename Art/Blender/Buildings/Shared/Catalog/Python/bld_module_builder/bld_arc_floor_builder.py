# Copyright (c) 2026 Emberfall. All Rights Reserved.
"""Builds the mesh of a slab in the shape of a circular segment."""

__author__ = "Matthias Stefan"
__version__ = "0.1.0"

import math

import bmesh

from bld_modules import ArcFloorModule

from .bld_base_module_builder import BaseModuleBuilder


class ArcFloorBuilder(BaseModuleBuilder):
    """Builds a closed slab between a chord and an arc."""

    def __init__(self, module: ArcFloorModule) -> None:
        """Creates an arc floor builder.

        Args:
            module: Arc floor module providing the dimensions.

        Returns:
            None.
        """
        super().__init__(module)
        self._arc_floor: ArcFloorModule = module
        return None

    def build(self) -> bmesh.types.BMesh:
        """Builds the outline of the segment and extrudes it to the slab thickness.

        Returns:
            A new BMesh in m, centered in X and Y, bottom at Z = 0, top at the thickness.
            The chord runs along the back (+Y) and the arc bulges toward the front (-Y).
            The caller owns it and must call free() on it.
        """
        floor: ArcFloorModule = self._arc_floor
        bm: bmesh.types.BMesh = bmesh.new()

        half_width: float = floor.width * 0.5
        bulge: float = floor.depth
        radius: float = (half_width * half_width + bulge * bulge) / (2.0 * bulge)
        max_angle: float = math.asin(min(1.0, half_width / radius))

        # from the back left corner along the chord to the right, then back along the arc
        back: float = bulge * 0.5
        outline: list[tuple[float, float]] = [(-half_width, back), (half_width, back)]
        for step in range(1, floor.segments):
            angle: float = max_angle - 2.0 * max_angle * step / floor.segments
            outline.append((radius * math.sin(angle), (radius - bulge) - radius * math.cos(angle) + back - 0.0 * bulge))
        bottom = bm.faces.new([bm.verts.new((x, y, 0.0)) for x, y in outline])
        extruded: dict = bmesh.ops.extrude_face_region(bm, geom=[bottom])
        top_vertices = [item for item in extruded["geom"] if isinstance(item, bmesh.types.BMVert)]
        bmesh.ops.translate(bm, vec=(0.0, 0.0, floor.height), verts=top_vertices)
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        return bm
