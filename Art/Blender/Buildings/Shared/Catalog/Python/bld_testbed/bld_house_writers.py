# Copyright (c) 2026 Emberfall. All Rights Reserved.
"""One collection per house with one sub collection per part, and the writers for them."""

__author__ = "Matthias Stefan"
__version__ = "0.1.0"

import bpy

from bld_blender import MeshWriter, SharedMeshCache

from .bld_house_part import HousePart


class HouseWriters:
    """Owns the collection of one house and a writer for each of its parts."""

    def __init__(
        self,
        parent: bpy.types.Collection,
        house_name: str,
        cache: SharedMeshCache,
    ) -> None:
        """Creates the house collection with one sub collection per part.

        Args:
            parent: Collection the house collection is linked into.
            house_name: Name of the house collection, the part collections are prefixed with it.
            cache: Cache the writers share, so equal modules share meshes across all houses.

        Returns:
            None.
        """
        self._collection: bpy.types.Collection = bpy.data.collections.new(house_name)
        parent.children.link(self._collection)

        self._part_collections: dict[HousePart, bpy.types.Collection] = {}
        self._writers: dict[HousePart, MeshWriter] = {}
        for part in HousePart:
            part_collection: bpy.types.Collection = bpy.data.collections.new(
                f"{house_name}_{part.value}"
            )
            self._collection.children.link(part_collection)
            self._part_collections[part] = part_collection
            self._writers[part] = MeshWriter(part_collection, cache)
        return None

    def writer_for(self, part: HousePart) -> MeshWriter:
        """Returns the writer of a part.

        Args:
            part is the part the objects belong to.

        Returns:
            Writer that links its objects into the collection of that part.
        """
        return self._writers[part]

    def remove_empty_parts(self) -> None:
        """Deletes the part collections that stayed empty, e.g. no stairs without a foundation.

        Returns:
            None.
        """
        for part_collection in self._part_collections.values():
            if not part_collection.objects:
                bpy.data.collections.remove(part_collection)
        return None
