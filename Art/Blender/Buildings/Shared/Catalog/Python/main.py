# Copyright (c) 2026 Emberfall. All Rights Reserved.

# exec(bpy.data.texts["main.py"].as_string())


import bpy

GEN_MODULES_COLLECTION: str = "GenModules"


def recreate_collection(name: str) -> bpy.types.Collection:
    """Deletes the named collection with all its content and creates it anew.

    Args:
        name: Collection name.

    Returns:
        The fresh, empty collection linked to the scene root.
    """
    existing: bpy.types.Collection | None = bpy.data.collections.get(name)
    if existing is not None:
        for stale_object in list(existing.all_objects):
            stale_data: bpy.types.ID | None = stale_object.data
            bpy.data.objects.remove(stale_object, do_unlink=True)
            if isinstance(stale_data, bpy.types.Mesh) and stale_data.users == 0:
                bpy.data.meshes.remove(stale_data)
        bpy.data.collections.remove(existing)

    collection: bpy.types.Collection = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(collection)
    return collection


def main() -> None:
    """Rebuilds everything generated from scratch.

    Returns:
        None.
    """
    gen_collection: bpy.types.Collection = recreate_collection(GEN_MODULES_COLLECTION)
    print(f"main: '{gen_collection.name}' recreated")
    return None


if __name__ == "__main__":
    main()