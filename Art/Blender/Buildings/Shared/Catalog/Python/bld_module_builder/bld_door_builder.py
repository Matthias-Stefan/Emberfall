# Copyright (c) 2026 Emberfall. All Rights Reserved.

from bld_modules import DoorModule
from bld_geometry import MeshData

from .bld_base_module_builder import BaseModuleBuilder


class DoorBuilder(BaseModuleBuilder):
    """Builds a wall with a door opening from three boxes."""

    def __init__(self, module: DoorModule) -> None:
        """Creates a door builder.

        Args:
            module: Door module providing wall and opening dimensions.

        Returns:
            None.
        """
        super().__init__(module)
        self._door_module: DoorModule = module
        return None

    def build(self) -> MeshData:
        """Builds left side, right side and lintel around the opening.

        Returns:
            Mesh data in m, centered in X and Y, floor at Z = 0.
        """
        door: DoorModule = self._door_module
        result: MeshData = MeshData()

        half_width: float = door.width * 0.5
        half_depth: float = door.depth * 0.5
        opening_left: float = -half_width + door.resolved_opening_offset
        opening_right: float = opening_left + door.opening_width

        # left side, full height
        result.add_box(
            (-half_width, -half_depth, 0.0),
            (opening_left, half_depth, door.height),
        )
        # right side, full height
        result.add_box(
            (opening_right, -half_depth, 0.0),
            (half_width, half_depth, door.height),
        )
        # lintel above the opening
        result.add_box(
            (opening_left, -half_depth, door.head_height),
            (opening_right, half_depth, door.height),
        )
        return result
