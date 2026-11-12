# Copyright (c) 2026 Emberfall. All Rights Reserved.
"""Writes BMeshes as objects into one Blender collection."""

__author__ = "Matthias Stefan"
__version__ = "0.1.0"

import bmesh
import bpy


class MeshWriter:
    """Writes BMeshes as objects into one Blender collection."""

    def __init__(self, collection: bpy.types.Collection) -> None:
        """Creates a mesh writer.

        Args:
            collection: Collection the written objects are linked into.

        Returns:
            None.
        """
        self._collection: bpy.types.Collection = collection
        return None

    def write(
        self,
        name: str,
        bm: bmesh.types.BMesh,
        color: tuple[float, float, float, float] | None = None,
    ) -> bpy.types.Object:
        """Writes a BMesh as a new object and frees it.

        Args:
            name: Name for the object and its mesh.
            bm: Geometry to write, freed by this call, do not use it afterwards.
            color: Viewport object color as RGBA in 0..1, None keeps the default.

        Returns:
            The newly created object.
        """
        mesh: bpy.types.Mesh = bpy.data.meshes.new(name)
        try:
            bm.to_mesh(mesh)
        finally:
            bm.free()

        mesh_object: bpy.types.Object = bpy.data.objects.new(name, mesh)
        if color is not None:
            mesh_object.color = color  # type: ignore[assignment]
        self._collection.objects.link(mesh_object)
        return mesh_object