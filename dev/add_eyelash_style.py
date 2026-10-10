"""
Ice Cube Rig - Add a new eyelash style to a rig .blend
======================================================

This is a *development* helper (it is not part of the addon UI). It automates the
blend-side work needed to add a brand new eyelash style to the Ice Cube rig:

  1. duplicates an existing eyelash mesh (so all vertex groups / modifiers / materials match)
  2. puts it in its own collection named "Eyelashes <Label>" with the id
     `ice_cube.eyelashes_<id>` (the id is what the addon looks for)
  3. re-creates the two Weld drivers that are used as the on/off switch, using the
     correct style index
  4. saves the .blend (uncompressed, like the shipped files)

After running it, the new style shows up in the addon's "Eyelashes" dropdown
automatically (the `eyelashes` enum is generated from the rig's collections).


How the system works
--------------------
* Every eyelash style is ONE mesh inside its OWN collection under `ice_cube.face`.
  Collection name : "Eyelashes Wispy"
  Collection id   : `ice_cube.eyelashes_wispy`   (custom prop `ice_cube_collection_id`)
* The mesh is never really hidden - its **Weld** modifier is what hides it.
  Two drivers (show_viewport + show_render) use this expression:

      (0 if eyelashes == INDEX else 1) + (1-face_rig) + emotion_eye_shape

  -> 0  = Weld OFF = mesh VISIBLE
  -> 1+ = Weld ON  = all verts collapse = mesh invisible
  So "0" happens only when the selected style matches INDEX. `face_rig` off, or any
  emotion eye shape, adds 1 and hides every style.
* IMPORTANT: enum properties are read as their **0-based integer index** inside
  driver expressions, NOT as the string identifier you see in Python.
      '1' -> 0 (None), '2' -> 1 (Standard), '3' -> 2 (Andromeda), '4' -> 3 (Bushy)
  so a *new* upper style is index 4 (identifier '5'), the next one 5 ('6'), ...
  The order of custom styles is taken from the custom prop
  `ice_cube_eyelash_index` on the collection (fallback: alphabetical by id).
* Lower eyelashes are separate: they live directly inside `ice_cube.face` (the
  shipped ones are literally named "Plane" / "Plane.001"), their driver variable
  reads `eyelashes_lower`, and that enum is still hardcoded in
  `Properties/enumerators.py` - so for a lower style you also add one line there
  (this script prints the exact line for you).


Usage (command line - recommended)
----------------------------------
    blender Assets/ice_cube.blend --background --python dev/add_eyelash_style.py -- \
        --id wispy --label "Wispy" --source "Eyelashes"

    --id       snake_case id, becomes `ice_cube.eyelashes_<id>`      (required)
    --label    name shown in the UI dropdown                          (default: title-cased id)
    --source   mesh to duplicate: object name of an existing style    (default: "Eyelashes")
               upper lashes : "Eyelashes" / "Eyelashes Andromeda" / "Eyelashes Bushy"
               lower lashes : "Plane" (standard) / "Plane.001" (bushy)
    --lower    create a LOWER eyelash style (driver reads `eyelashes_lower`)
    --index    force the style index (default: next free one)
    --no-save  don't write the file, just do the scene edits
    --list     print the styles that already exist and exit

Run it once per rig variant:
    Assets/ice_cube.blend  Assets/ice_cube_14px.blend  Assets/ice_cube_10px.blend


Usage (inside Blender)
----------------------
Open the rig .blend, load this file into the Text editor, edit the SETTINGS block
below and press Run Script.
"""

import bpy
import re
import sys

# ---------------------------------------------------------------------------
# SETTINGS (only used when running from Blender's Text editor)
# ---------------------------------------------------------------------------
SETTINGS = {
    "id": "",            # e.g. "wispy"
    "label": "",         # e.g. "Wispy"
    "source": "Eyelashes",
    "lower": False,
    "index": None,
    "save": True,        # when run from the Text editor it saves right away
    "list": False,
}

RIG_ID = "Ice_Cube_v2_Remake"
FACE_ID = "ice_cube.face"
EYELASH_ID_PREFIX = "ice_cube.eyelashes_"
BUILTIN_IDS = (
    "ice_cube.eyelashes_default",
    "ice_cube.eyelashes_andromeda",
    "ice_cube.eyelashes_bushy",
)
DRIVER_EXPRESSION = "(0 if eyelashes == {index} else 1) + (1-face_rig) + emotion_eye_shape"


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
def parse_args(settings):
    argv = sys.argv
    if "--" not in argv:
        return False
    args = argv[argv.index("--") + 1:]
    i = 0
    while i < len(args):
        arg = args[i]
        if arg == "--id":
            settings["id"] = args[i + 1]; i += 1
        elif arg == "--label":
            settings["label"] = args[i + 1]; i += 1
        elif arg == "--source":
            settings["source"] = args[i + 1]; i += 1
        elif arg == "--index":
            settings["index"] = int(args[i + 1]); i += 1
        elif arg == "--lower":
            settings["lower"] = True
        elif arg == "--save":
            settings["save"] = True
        elif arg == "--no-save":
            settings["save"] = False
        elif arg == "--list":
            settings["list"] = True
        i += 1
    return True


def snake_case(name):
    name = re.sub(r"[^0-9a-zA-Z]+", "_", name.strip()).strip("_").lower()
    return re.sub(r"_+", "_", name)


def get_rig():
    for obj in bpy.data.objects:
        if obj.type == "ARMATURE" and obj.data.get("rig_id") == RIG_ID:
            return obj
    return bpy.data.objects.get("Ice Cube")


def get_rig_collections(rig):
    """main collection + every child, same lookup the addon uses"""
    for collection in rig.users_collection:
        if collection.get("ice_cube_collection_id") == "ice_cube.main":
            return [collection] + list(collection.children_recursive)
    return list(rig.users_collection)


def get_face_collection(rig):
    for collection in get_rig_collections(rig):
        if collection.get("ice_cube_collection_id") == FACE_ID:
            return collection
    return None


def get_weld_driver_index(obj):
    """returns (index, property_path) of the style this object belongs to, or None"""
    if not obj.animation_data:
        return None
    for fcurve in obj.animation_data.drivers:
        if "modifiers[\"Weld\"]" not in fcurve.data_path:
            continue
        match = re.search(r"eyelashes\s*==\s*(\d+)", fcurve.driver.expression or "")
        if not match:
            continue
        prop_path = None
        for variable in fcurve.driver.variables:
            if variable.name == "eyelashes":
                prop_path = variable.targets[0].data_path
        return int(match.group(1)), prop_path
    return None


def find_existing_styles(rig):
    """(index, prop_path, obj_or_collection_id, label) for every style in the file"""
    face = get_face_collection(rig)
    styles = []
    if not face:
        return styles
    for collection in [face] + list(face.children_recursive):
        for obj in collection.objects:
            found = get_weld_driver_index(obj)
            if not found:
                continue
            index, prop_path = found
            if obj.users_collection:
                collection_id = obj.users_collection[0].get("ice_cube_collection_id")
            else:
                collection_id = None
            label = obj.name
            if collection_id and collection_id.startswith(EYELASH_ID_PREFIX):
                label = collection_id[len(EYELASH_ID_PREFIX):].replace("_", " ").title()
            styles.append((index, prop_path, collection_id, label))
    return sorted(styles)


def print_styles(styles):
    print("\n--- eyelash styles in this file ---")
    for index, prop_path, collection_id, label in styles:
        kind = "lower" if prop_path == "eyelashes_lower" else "upper"
        print(f"  index {index:<2} ({kind:<5}) {label:<20} {collection_id or '(no collection)'}")
    print()


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------
def add_eyelash_style(style_id, label, source_name, lower=False, index=None):
    rig = get_rig()
    if rig is None:
        raise RuntimeError("No Ice Cube rig found - is this the ice_cube .blend?")

    face = get_face_collection(rig)
    if face is None:
        raise RuntimeError("Collection 'ice_cube.face' not found")

    source = bpy.data.objects.get(source_name)
    if source is None:
        raise RuntimeError(f"Source object '{source_name}' not found")

    style_id = snake_case(style_id)
    if not style_id:
        raise RuntimeError("A --id is required (e.g. --id wispy)")
    label = label or style_id.replace("_", " ").title()

    prop_path = "eyelashes_lower" if lower else "eyelashes"
    styles = find_existing_styles(rig)
    print_styles(styles)

    # figure out the index: next free one for this (upper/lower) group
    used = {s[0] for s in styles if s[1] == prop_path or (s[1] is None and not lower)}
    if index is None:
        index = max(used) + 1 if used else (3 if lower else 4)
    if index in used:
        raise RuntimeError(f"Index {index} is already taken by another {prop_path} style")

    object_name = f"Eyelashes Lower {label}" if lower else f"Eyelashes {label}"
    if object_name in bpy.data.objects:
        raise RuntimeError(f"Object '{object_name}' already exists")

    # 1. duplicate the source mesh (unique data so editing it won't touch the original)
    new_obj = source.copy()
    new_obj.data = source.data.copy()
    new_obj.name = object_name
    new_obj.data.name = object_name
    new_obj.animation_data_clear()
    for collection in list(new_obj.users_collection):
        collection.objects.unlink(new_obj)

    # 2. collection + custom props
    if lower:
        # lower styles live directly inside ice_cube.face, exactly like the shipped ones
        face.objects.link(new_obj)
        collection = face
        collection_id = None
    else:
        collection = bpy.data.collections.new(object_name)
        collection["ice_cube_collection_id"] = f"{EYELASH_ID_PREFIX}{style_id}"
        collection["ice_cube_eyelash_index"] = index
        face.children.link(collection)
        collection.objects.link(new_obj)
        collection_id = collection["ice_cube_collection_id"]

    # 3. transform / parenting (keep the source's placement)
    new_obj.parent = source.parent
    new_obj.matrix_parent_inverse = source.matrix_parent_inverse.copy()
    new_obj.matrix_world = source.matrix_world.copy()
    if "ice_cube.parented" in source:
        new_obj["ice_cube.parented"] = True

    # 4. the Weld modifier is the on/off switch - give it fresh drivers
    expression = DRIVER_EXPRESSION.format(index=index)
    for data_path in ('modifiers["Weld"].show_viewport', 'modifiers["Weld"].show_render'):
        fcurve = new_obj.driver_add(data_path)
        driver = fcurve.driver
        driver.type = "SCRIPTED"
        driver.expression = expression
        for variable_name, variable_path in (
            ("eyelashes", prop_path),
            ("face_rig", "face_rig"),
            ("emotion_eye_shape", "emotion_eye_shape"),
        ):
            variable = driver.variables.new()
            variable.name = variable_name
            variable.type = "SINGLE_PROP"
            variable.targets[0].id = rig
            variable.targets[0].data_path = variable_path

    print(f"created '{object_name}'")
    print(f"  collection    : {collection.name} ({collection_id or 'inside ice_cube.face'})")
    print(f"  style index   : {index}")
    print(f"  driver        : {expression}")
    print(f"  driver var    : {prop_path}")

    if lower:
        print("\nLower styles are still hardcoded in the addon - add this item to")
        print("bpy.types.Object.eyelashes_lower in Properties/enumerators.py:")
        print(f"        ('{index + 1}', {label!r}, '{label} Eyelashes'),")
    else:
        print("\nNothing to change in the addon: the 'Eyelashes' dropdown is generated")
        print("from the rig's collections and will list this style automatically.")

    return new_obj


def main():
    settings = dict(SETTINGS)
    from_cli = parse_args(settings)

    rig = get_rig()
    if settings["list"]:
        print_styles(find_existing_styles(rig))
        return

    if not settings["id"]:
        print("Nothing to do: pass --id <style_id> (e.g. --id wispy)")
        return

    add_eyelash_style(
        settings["id"],
        settings["label"],
        settings["source"],
        lower=settings["lower"],
        index=settings["index"],
    )

    if settings["save"]:
        bpy.ops.wm.save_mainfile(compress=False)
        print(f"\nsaved {bpy.data.filepath}")
    elif from_cli:
        print("\n(--no-save: the file was NOT written)")


if __name__ == "__main__":
    main()
