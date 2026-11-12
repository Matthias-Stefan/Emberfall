# Copyright (c) 2026 Emberfall. All Rights Reserved.
"""Writes BMeshes as objects into one Blender collection."""

__author__ = "Matthias Stefan"
__version__ = "0.1.0"

from collections.abc import Callable

import bmesh
import bpy

from .bld_shared_mesh_cache import SharedMeshCache


class MeshWriter:
    """Writes BMeshes as objects into one Blender collection."""

    def __init__(
        self, collection: bpy.types.Collection, cache: SharedMeshCache | None = None
    ) -> None:
        """Creates a mesh writer.

        Args:
            collection: Collection the written objects are linked into.
            cache: Cache for the shared meshes, writers that share a cache share their meshes,
                None gives this writer a cache of its own.

        Returns:
            None.
        """
        self._collection: bpy.types.Collection = collection
        self._cache: SharedMeshCache = cache if cache is not None else SharedMeshCache()
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
        return self._create_object(name, self._create_mesh(name, bm), color)

    def write_shared(
        self,
        name: str,
        shared_key: str,
        build: Callable[[], bmesh.types.BMesh],
        color: tuple[float, float, float, float] | None = None,
    ) -> bpy.types.Object:
        """Writes a new object that shares its mesh with all other objects of the same key.

        The geometry is built only for the first object of a key, every further object links
        the same mesh, so repeated modules cost neither build time nor memory.

        Args:
            name: Name for the object.
            shared_key: Key of the shared mesh, it is also the mesh name. Objects with the same
                key must have identical geometry.
            build: Builds the geometry, only called if the key is new, the result is freed here.
            color: Viewport object color as RGBA in 0..1, None keeps the default. The color is
                stored on the object, so shared meshes can still differ in color.

        Returns:
            The newly created object.
        """
        return self._create_object(name, self._cache.get_or_create(shared_key, build), color)

    @staticmethod
    def _create_mesh(name: str, bm: bmesh.types.BMesh) -> bpy.types.Mesh:
        """Copies a BMesh into a new mesh and frees it.

        Args:
            name is the name of the mesh.
            bm is the geometry, freed by this call, do not use it afterwards.

        Returns:
            The new mesh.
        """
        mesh: bpy.types.Mesh = bpy.data.meshes.new(name)
        try:
            bm.to_mesh(mesh)
        finally:
            bm.free()
        return mesh

    def _create_object(
        self,
        name: str,
        mesh: bpy.types.Mesh,
        color: tuple[float, float, float, float] | None,
    ) -> bpy.types.Object:
        """Creates an object for a mesh and links it into the collection.

        Args:
            name is the name of the object.
            mesh is the mesh the object uses.
            color is the viewport object color, None keeps the default.

        Returns:
            The newly created object.
        """
        mesh_object: bpy.types.Object = bpy.data.objects.new(name, mesh)
        if color is not None:
            mesh_object.color = color  # type: ignore[assignment]
        self._collection.objects.link(mesh_object)
        return mesh_object
