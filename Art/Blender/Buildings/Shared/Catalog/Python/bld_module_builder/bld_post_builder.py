# Copyright (c) 2026 Emberfall. All Rights Reserved.

import bmesh

from bld_modules import PostModule
from .bld_base_module_builder import BaseModuleBuilder


class PostBuilder(BaseModuleBuilder):
    """Builds a plain box post."""

    def __init__(self, module: PostModule) -> None:
        """Creates a post builder.

        Args:
            module: Post module providing the box dimensions.

        Returns:
            None.
        """
        super().__init__(module)
        self._post_module: PostModule = module
        return None

    def build(self) -> bmesh.types.BMesh:
        """Builds a closed box from the post dimensions.

        Returns:
            A new BMesh in m, centered in X and Y, floor at Z = 0.
            The caller owns it and must call free() on it.
        """
        post: PostModule = self._post_module
        bm: bmesh.types.BMesh = bmesh.new()

        # unit cube around the origin, scaled to size, then lifted so the floor sits at Z = 0
        bmesh.ops.create_cube(bm, size=1.0)
        bmesh.ops.scale(bm, vec=(post.width, post.depth, post.height), verts=bm.verts)
        bmesh.ops.translate(bm, vec=(0.0, 0.0, post.height * 0.5), verts=bm.verts)
        return bm