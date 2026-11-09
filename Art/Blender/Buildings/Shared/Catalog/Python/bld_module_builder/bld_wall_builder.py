# Copyright (c) 2026 Emberfall. All Rights Reserved.

from bld_modules import WallModule
from bld_geometry import (
    BoxFace,
    MeshData,
)
from .bld_base_module_builder import BaseModuleBuilder


class WallBuilder(BaseModuleBuilder):
    """Builds a plain closed box wall."""

    def __init__(self, module: WallModule) -> None:
        """Creates a standard wall builder.

        Args:
            module: Wall module providing the box dimensions.

        Returns:
            None.
        """
        super().__init__(module)
        self._wall_module: WallModule = module
        return None

    def build(self) -> MeshData:
        """Builds a closed box from the wall module dimensions.

        Returns:
            Mesh data in m, centered in X and Y, floor at Z = 0.
        """
        result: MeshData = MeshData()

        half_width: float = self._wall_module.width * 0.5
        half_depth: float = self._wall_module.depth * 0.5

        result.add_box(
            (-half_width, -half_depth, 0.0),
            (half_width, half_depth, self._wall_module.height),
            #omit=frozenset({BoxFace.TOP, BoxFace.BOTTOM, BoxFace.LEFT, BoxFace.RIGHT}),
        )
        return result
