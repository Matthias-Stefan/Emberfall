# Copyright (c) 2026 Emberfall. All Rights Reserved.

import bpy

from bld_geometry import MeshData


class MeshWriter:
    """Writes mesh data as objects into one Blender collection."""

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
        mesh_data: MeshData,
        color: tuple[float, float, float, float] | None = None,
    ) -> bpy.types.Object:
        """Writes mesh data as a new object.

        Args:
            name: Name for the object and its mesh.
            mesh_data: Geometry to write.
            color: Viewport object color as RGBA in 0..1, None keeps the default.

        Returns:
            The newly created object.
        """
        mesh: bpy.types.Mesh = bpy.data.meshes.new(name)
        mesh.from_pydata(mesh_data.vertices, [], mesh_data.faces)
        mesh.update()

        mesh_object: bpy.types.Object = bpy.data.objects.new(name, mesh)
        if color is not None:
            mesh_object.color = color
        self._collection.objects.link(mesh_object)
        return mesh_object
