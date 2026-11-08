# Copyright (c) 2026 Emberfall. All Rights Reserved.

from bld_modules import DoorModule
from bld_geometry import MeshData

from .bld_base_module_builder import BaseModuleBuilder


class DoorBuilder(BaseModuleBuilder):
    """Builds a wall with a centered door opening from three boxes."""

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

        if door.opening_width >= door.width or door.opening_height >= door.height:
            raise ValueError(f"Opening does not fit into module '{door.name}'")

        result: MeshData = MeshData()

        half_width: float = door.width * 0.5
        half_depth: float = door.depth * 0.5
        half_opening: float = door.opening_width * 0.5

        # left side, full height
        result.add_box(
            (-half_width, -half_depth, 0.0),
            (-half_opening, half_depth, door.height),
        )
        # right side, full height
        result.add_box(
            (half_opening, -half_depth, 0.0),
            (half_width, half_depth, door.height),
        )
        # lintel above the opening
        result.add_box(
            (-half_opening, -half_depth, door.opening_height),
            (half_opening, half_depth, door.height),
        )
        return result
