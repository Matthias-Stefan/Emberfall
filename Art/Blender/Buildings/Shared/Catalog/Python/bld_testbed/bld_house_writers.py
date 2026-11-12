# Copyright (c) 2026 Emberfall. All Rights Reserved.
"""One collection per house with one sub collection per part, and the writers for them."""

__author__ = "Matthias Stefan"
__version__ = "0.1.0"

import bpy

from bld_blender import MeshWriter, SharedMeshCache

from .bld_house_part import HousePart


class HouseWriters:
    """Owns the collection of one house and a writer for each of its parts on each level."""

    def __init__(
        self,
        parent: bpy.types.Collection,
        house_name: str,
        cache: SharedMeshCache,
    ) -> None:
        """Creates the house collection with one sub collection per part of the ground level.

        Args:
            parent: Collection the house collection is linked into.
            house_name: Name of the house collection, the part collections are prefixed with it.
            cache: Cache the writers share, so equal modules share meshes across all houses.

        Returns:
            None.
        """
        self._house_name: str = house_name
        self._cache: SharedMeshCache = cache
        self._collection: bpy.types.Collection = bpy.data.collections.new(house_name)
        parent.children.link(self._collection)

        self._part_collections: dict[tuple[int, HousePart], bpy.types.Collection] = {}
        self._writers: dict[tuple[int, HousePart], MeshWriter] = {}
        for part in HousePart:
            self._create_part(0, part)
        return None

    def writer_for(self, part: HousePart, level: int = 0) -> MeshWriter:
        """Returns the writer of a part on a level, the collection of an upper level is made on demand.

        Args:
            part is the part the objects belong to.
            level is the level the objects belong to, 0 is the ground level.

        Returns:
            Writer that links its objects into the collection of that part and level.
        """
        if (level, part) not in self._writers:
            self._create_part(level, part)
        return self._writers[(level, part)]

    def remove_empty_parts(self) -> None:
        """Deletes the part collections that stayed empty, e.g. no stairs without a foundation.

        Returns:
            None.
        """
        for part_collection in self._part_collections.values():
            if not part_collection.objects:
                bpy.data.collections.remove(part_collection)
        return None

    def _create_part(self, level: int, part: HousePart) -> None:
        """Creates the collection and the writer of one part on one level.

        Args:
            level is the level, 0 is the ground level whose names carry no level.
            part is the part.

        Returns:
            None.
        """
        level_tag: str = "" if level == 0 else f"_l{level}"
        part_collection: bpy.types.Collection = bpy.data.collections.new(
            f"{self._house_name}{level_tag}_{part.value}"
        )
        self._collection.children.link(part_collection)
        self._part_collections[(level, part)] = part_collection
        self._writers[(level, part)] = MeshWriter(part_collection, self._cache)
        return None
