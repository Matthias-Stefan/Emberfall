# Copyright (c) 2026 Emberfall. All Rights Reserved.

from bld_geometry import MeshData
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

    def build(self) -> MeshData:
        """Builds a box from the post dimensions.

        Returns:
            Mesh data in m, centered in X and Y, floor at Z = 0.
        """
        result: MeshData = MeshData()
        half_width: float = self._post_module.width * 0.5
        half_depth: float = self._post_module.depth * 0.5
        result.add_box(
            (-half_width, -half_depth, 0.0),
            (half_width, half_depth, self._post_module.height),
        )
        return result
