# Copyright (c) 2026 Emberfall. All Rights Reserved.
"""Builds the mesh of a rail module."""

__author__ = "Matthias Stefan"
__version__ = "0.1.0"

import bmesh

from bld_modules import RailModule
from .bld_base_module_builder import BaseModuleBuilder


class RailBuilder(BaseModuleBuilder):
    """Builds two end posts, a top rail and a middle rail."""

    def __init__(
        self,
        module: RailModule,
        rail_thickness: float = 0.05,
        top_rail_height: float = 0.06,
        middle_rail_height: float = 0.04,
        middle_rail_position: float = 0.45,
    ) -> None:
        """Creates a rail builder.

        Args:
            module: Rail module providing span, post thickness and railing height.
            rail_thickness: Depth of the rails in m, thinner than the posts.
            top_rail_height: Vertical size of the top rail in m, its top is flush with the posts.
            middle_rail_height: Vertical size of the middle rail in m.
            middle_rail_position: Height of the middle rail center as a fraction of the module
                height, 0 is the floor and 1 the top.

        Returns:
            None.
        """
        super().__init__(module)
        self._rail_module: RailModule = module
        self._rail_thickness: float = rail_thickness
        self._top_rail_height: float = top_rail_height
        self._middle_rail_height: float = middle_rail_height
        self._middle_rail_position: float = middle_rail_position
        return None

    def build(self) -> bmesh.types.BMesh:
        """Builds the posts and rails as closed boxes.

        Returns:
            A new BMesh in m, centered in X and Y, floor at Z = 0.
            The caller owns it and must call free() on it.
        """
        rail: RailModule = self._rail_module
        bm: bmesh.types.BMesh = bmesh.new()
        half_span: float = rail.width * 0.5
        half_post: float = rail.depth * 0.5
        half_rail: float = self._rail_thickness * 0.5

        # posts are centered on the span ends, so they stick out half a post past the module
        for post_x in (-half_span, half_span):
            self._add_box(
                bm,
                (post_x - half_post, -half_post, 0.0),
                (post_x + half_post, half_post, rail.height),
            )

        self._add_box(
            bm,
            (-half_span, -half_rail, rail.height - self._top_rail_height),
            (half_span, half_rail, rail.height),
        )
        middle_center: float = rail.height * self._middle_rail_position
        self._add_box(
            bm,
            (-half_span, -half_rail, middle_center - self._middle_rail_height * 0.5),
            (half_span, half_rail, middle_center + self._middle_rail_height * 0.5),
        )
        return bm
