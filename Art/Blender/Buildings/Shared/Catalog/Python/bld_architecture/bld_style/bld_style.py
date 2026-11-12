# Copyright (c) 2026 Emberfall. All Rights Reserved.
"""Bundles everything an architect needs to plan in one look."""

__author__ = "Matthias Stefan"
__version__ = "0.1.0"

from dataclasses import dataclass

from bld_modules import TOLERANCE, OpeningWallModule, WallModule

from .bld_module_atlas import ModuleAtlas


@dataclass(frozen=True)
class Style:
    """Look of a building: which modules it may use and how thick and high its walls are."""

    name: str
    """Display name of the style."""

    atlas: ModuleAtlas
    """Modules the architect may plan with."""

    wall_depth: float = 0.30
    """Wall thickness in m, shared by all walls, doors and windows."""

    wall_height: float = 2.60
    """Wall height in m, shared by all walls, doors and windows."""

    def __post_init__(self) -> None:
        """Validates that every wall, door and window of the atlas has the style's size.

        Raises:
            ValueError: If a module differs in depth or height.
        """
        for module_type in (WallModule, OpeningWallModule):
            for module in self.atlas.modules_of(module_type):
                if (
                    abs(module.depth - self.wall_depth) > TOLERANCE
                    or abs(module.height - self.wall_height) > TOLERANCE
                ):
                    raise ValueError(
                        f"Module '{module.name}' is {module.depth} m thick and {module.height} m high, "
                        f"style '{self.name}' expects {self.wall_depth} m and {self.wall_height} m"
                    )
