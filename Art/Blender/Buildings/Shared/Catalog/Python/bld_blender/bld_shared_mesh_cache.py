# Copyright (c) 2026 Emberfall. All Rights Reserved.
"""Keeps one Blender mesh per key so many objects can share the same geometry."""

__author__ = "Matthias Stefan"
__version__ = "0.1.0"

from collections.abc import Callable

import bmesh
import bpy


class SharedMeshCache:
    """Builds the mesh of a key once and hands out the same mesh afterwards."""

    def __init__(self) -> None:
        """Creates an empty cache.

        Returns:
            None.
        """
        self._meshes: dict[str, bpy.types.Mesh] = {}
        return None

    def get_or_create(
        self, key: str, build: Callable[[], bmesh.types.BMesh]
    ) -> bpy.types.Mesh:
        """Returns the mesh of a key, building it on first use.

        Args:
            key: Key and mesh name, equal keys must mean identical geometry.
            build: Builds the geometry, only called if the key is new, the result is freed here.

        Returns:
            The shared mesh.
        """
        mesh: bpy.types.Mesh | None = self._meshes.get(key)
        if mesh is None:
            mesh = bpy.data.meshes.new(key)
            bm: bmesh.types.BMesh = build()
            try:
                bm.to_mesh(mesh)
            finally:
                bm.free()
            self._meshes[key] = mesh
        return mesh
