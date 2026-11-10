# Copyright (c) 2026 Emberfall. All Rights Reserved.

from bld_modules import WindowModule
from bld_geometry import MeshData

from .bld_base_module_builder import BaseModuleBuilder


class WindowBuilder(BaseModuleBuilder):

    def __init__(self, module: WindowModule):
        super().__init__(module)
        self._window_module: WindowModule = module
        return None

    def build(self) -> MeshData:
        window: WindowModule = self._window_module
        result: MeshData = MeshData()

        return result
