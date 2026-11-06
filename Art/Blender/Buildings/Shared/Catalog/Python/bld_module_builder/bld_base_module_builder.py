# Copyright (c) 2026 Emberfall. All Rights Reserved.

from bld_modules import BaseModule

from abc import ABCMeta


class BaseModuleBuilder(metaclass=ABCMeta):
    """Builds geometry for one module."""

    def __init__(self, module: BaseModule) -> None:
        self._module: BaseModule = module
