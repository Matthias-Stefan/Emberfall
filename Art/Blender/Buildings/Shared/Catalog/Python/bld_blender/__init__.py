# Copyright (c) 2026 Emberfall. All Rights Reserved.
"""Blender-side writers that turn BMeshes into scene objects."""

__author__ = "Matthias Stefan"
__version__ = "0.1.0"

from .bld_mesh_writer import (
    MeshWriter
)

__all__: list[str] = [
    "MeshWriter",
]
