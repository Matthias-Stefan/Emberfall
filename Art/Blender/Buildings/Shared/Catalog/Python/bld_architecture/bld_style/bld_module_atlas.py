# Copyright (c) 2026 Emberfall. All Rights Reserved.
"""Collection of the modules an architect may plan with."""

__author__ = "Matthias Stefan"
__version__ = "0.1.0"

from bld_modules import BaseWallModule


class ModuleAtlas:
    """Collection of the modules an architect may plan with."""

    def __init__(self, modules: list[BaseWallModule] | None = None) -> None:
        """Creates an atlas.

        Args:
            modules: Modules to register right away, may be empty.

        Returns:
            None.
        """
        self._modules: dict[str, BaseWallModule] = {}
        for module in modules or []:
            self.register(module)
        return None

    def register(self, module: BaseWallModule) -> None:
        """Adds a module to the atlas.

        Args:
            module: Module to add, its name must be unique.

        Raises:
            ValueError: If a module with the same name is already registered.

        Returns:
            None.
        """
        if module.name in self._modules:
            raise ValueError(f"Module '{module.name}' is already registered")
        self._modules[module.name] = module
        return None

    def modules_of(self, module_type: type[BaseWallModule]) -> list[BaseWallModule]:
        """Returns all modules of one kind, widest first.

        Args:
            module_type: Module class to filter by, e.g. WallModule.

        Returns:
            Matching modules sorted by width, descending.
        """
        matches: list[BaseWallModule] = [
            module for module in self._modules.values() if isinstance(module, module_type)
        ]
        return sorted(matches, key=lambda module: module.width, reverse=True)
