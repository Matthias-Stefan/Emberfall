# Copyright (c) 2026 Emberfall. All Rights Reserved.
"""Builds the mesh of a bracket module."""

__author__ = "Matthias Stefan"
__version__ = "0.1.0"

import bmesh

from bld_modules import BracketModule

from .bld_base_module_builder import BaseModuleBuilder


class BracketBuilder(BaseModuleBuilder):
    """Builds a diagonal beam that runs from the bottom of the low end to the top of the high end."""

    def __init__(self, module: BracketModule, beam_ratio: float = 0.3) -> None:
        """Creates a bracket builder.

        Args:
            module: Bracket module providing the dimensions.
            beam_ratio: Beam width measured across the strut, as a share of the module height.

        Returns:
            None.
        """
        super().__init__(module)
        self._bracket: BracketModule = module
        self._beam_ratio: float = beam_ratio

    def build(self) -> bmesh.types.BMesh:
        """Builds the strut as a slanted prism.

        Returns:
            A new BMesh in m, centered in X and Y, floor at Z = 0.
            The caller owns it and must call free() on it.
        """
        bracket: BracketModule = self._bracket
        beam: float = bracket.height * self._beam_ratio
        half_width: float = bracket.width * 0.5
        half_depth: float = bracket.depth * 0.5

        bm: bmesh.types.BMesh = bmesh.new()
        outline: list[tuple[float, float]] = [
            (-half_width, 0.0),
            (-half_width + beam, 0.0),
            (half_width, bracket.height - beam),
            (half_width, bracket.height),
            (half_width - beam, bracket.height),
            (-half_width, beam),
        ]
        front = bm.faces.new([bm.verts.new((x, -half_depth, z)) for x, z in outline])
        extruded: dict = bmesh.ops.extrude_face_region(bm, geom=[front])
        moved = [item for item in extruded["geom"] if isinstance(item, bmesh.types.BMVert)]
        bmesh.ops.translate(bm, vec=(0.0, bracket.depth, 0.0), verts=moved)
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        return bm
