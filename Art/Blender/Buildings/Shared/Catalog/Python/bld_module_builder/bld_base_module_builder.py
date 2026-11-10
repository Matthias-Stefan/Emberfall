# Copyright (c) 2026 Emberfall. All Rights Reserved.

from abc import ABCMeta, abstractmethod
import bmesh

from bld_modules import BaseModule
from bld_geometry import MeshData


class BaseModuleBuilder(metaclass=ABCMeta):
    """Builds geometry for one module."""

    def __init__(self, module: BaseModule) -> None:
        """Creates a builder.

        Args:
            module: Module to build the geometry for.

        Returns:
            None.
        """
        self._module: BaseModule = module
        return None

    @abstractmethod
    def build(self) -> bmesh.types.BMesh:
        """Builds the module geometry.

        Returns:
            A new BMesh in m, centered in X and Y, floor at Z = 0.
        """
