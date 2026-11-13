# Copyright (c) 2026 Emberfall. All Rights Reserved.
"""Builds the mesh of a curved wall or window module by bending a straight one."""

__author__ = "Matthias Stefan"
__version__ = "0.1.0"

import math

import bmesh

from bld_modules import TOLERANCE, ArcWallModule, ArcWindowModule, WallModule, WindowModule

from .bld_base_module_builder import BaseModuleBuilder
from .bld_wall_builder import WallBuilder
from .bld_window_builder import WindowBuilder


class ArcWallBuilder(BaseModuleBuilder):
    """Builds a straight wall or window, cuts it into pieces along X and bends it onto an arc."""

    def __init__(
        self,
        module: ArcWallModule,
        close_top: bool = False,
        close_bottom: bool = False,
        close_ends: bool = False,
    ) -> None:
        """Creates an arc wall builder.

        Args:
            module: Curved wall or window module providing the dimensions.
            close_top: Whether the top faces are generated.
            close_bottom: Whether the bottom faces are generated.
            close_ends: Whether the faces on both module ends are generated.

        Returns:
            None.
        """
        super().__init__(module, close_top, close_bottom, close_ends)
        self._arc_module: ArcWallModule = module

    def build(self) -> bmesh.types.BMesh:
        """Builds the straight module and bends it.

        Returns:
            A new BMesh in m, the origin in the middle of the chord on the wall line, floor at Z = 0.
            The caller owns it and must call free() on it.
        """
        module: ArcWallModule = self._arc_module
        sections: int = module.opening_count if isinstance(module, ArcWindowModule) else 1
        bm: bmesh.types.BMesh = bmesh.new()
        for section in range(sections):
            section_bm: bmesh.types.BMesh = self._straight_section(module, sections).build()
            offset: float = (section - (sections - 1) * 0.5) * module.width / sections
            vertex_map: dict[bmesh.types.BMVert, bmesh.types.BMVert] = {
                vertex: bm.verts.new((vertex.co.x + offset, vertex.co.y, vertex.co.z))
                for vertex in section_bm.verts
            }
            for face in section_bm.faces:
                bm.faces.new([vertex_map[vertex] for vertex in face.verts])
            section_bm.free()
        if sections > 1:
            bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=TOLERANCE)

        # cut every edge that runs along X, so the bend has vertices to move
        along_x: list[bmesh.types.BMEdge] = [
            edge
            for edge in bm.edges
            if abs(edge.verts[0].co.x - edge.verts[1].co.x) > TOLERANCE
            and abs(edge.verts[0].co.y - edge.verts[1].co.y) <= TOLERANCE
            and abs(edge.verts[0].co.z - edge.verts[1].co.z) <= TOLERANCE
        ]
        cuts: int = max(1, -(-module.segments // sections) - 1)
        bmesh.ops.subdivide_edges(bm, edges=along_x, cuts=cuts, use_grid_fill=True)
        self._bend(bm, module.width * 0.5, module.bulge)
        return bm

    def _straight_section(self, module: ArcWallModule, sections: int) -> BaseModuleBuilder:
        """Creates the builder of one straight section of the wall.

        Args:
            module is the curved module.
            sections is the number of equal sections along the chord.

        Returns:
            A window builder if the module has openings, otherwise a wall builder, ends are only
            closed if the module is one section.
        """
        close_ends: bool = self._close_ends and sections == 1
        if isinstance(module, ArcWindowModule):
            return WindowBuilder(
                WindowModule(
                    width=module.width / sections,
                    height=module.height,
                    depth=module.depth,
                    opening_width=module.opening_width,
                    opening_height=module.opening_height,
                    sill_height=module.sill_height,
                ),
                self._close_top,
                self._close_bottom,
                close_ends,
            )
        return WallBuilder(
            WallModule(width=module.width, height=module.height, depth=module.depth),
            self._close_top,
            self._close_bottom,
            close_ends,
        )

    @staticmethod
    def _bend(bm: bmesh.types.BMesh, half_width: float, bulge: float) -> None:
        """Moves every vertex of a straight wall onto the arc.

        The distance along the wall becomes the angle on the arc, the thickness becomes the
        distance from the arc, the front faces away from the center.

        Args:
            bm is the straight wall, centered in X and Y, edited in place.
            half_width is half the chord in m.
            bulge is the distance from the chord to the middle of the arc in m.

        Returns:
            None.
        """
        radius: float = (half_width * half_width + bulge * bulge) / (2.0 * bulge)
        max_angle: float = math.asin(min(1.0, half_width / radius))
        center_y: float = radius - bulge
        for vertex in bm.verts:
            angle: float = vertex.co.x / half_width * max_angle
            distance: float = radius - vertex.co.y
            vertex.co.x = distance * math.sin(angle)
            vertex.co.y = center_y - distance * math.cos(angle)
        return None
