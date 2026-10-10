import bpy

def GetMaterialHolder(rig):
    try:
        for obj in rig.children:
            try:
                if obj.data['ice_cube_material_holder']:
                    return obj
            except: continue
    except (AttributeError, KeyError, TypeError):
        return None

def GetMaterial(context, mat_id):
        
        materials = GetMaterialHolder(context.object).data.materials
        for mat in materials:
            try:
                if mat['ice_cube_material'] == mat_id:
                    return mat
            except:
                continue

def GetBone(rig, bone_id):
    bones = rig.pose.bones
    try:
        return bones[bone_id]
    except:
        for bone in bones:
            if 'ice_cube_bone_id' in bone and bone['ice_cube_bone_id'] == bone_id:
                return bone

def GetBoneCollection(collections, target):
        for collection in collections:
            try:
                if collection['ice_cube_layer_id'] == target:
                    return collection
            except:
                pass
        return None

def GetCollection(collections, target):
    for collection in collections:
        try:
            if collection['ice_cube_collection_id'] == target:
                return collection
        except:
            pass

def GetLattice(rig, lattice_id):
    child_objects = rig.children_recursive
    for obj in child_objects:
        if obj.type == 'LATTICE':
            if 'ice_cube.lattice_id' in obj and obj['ice_cube.lattice_id'] == lattice_id:
                return obj

#-------------------------------------------------#
#                    Eyelashes
#-------------------------------------------------#
# Every eyelash style is a mesh inside its own collection under "ice_cube.face".
# The collection carries the custom prop "ice_cube_collection_id" = "ice_cube.eyelashes_<id>"
# and, for custom styles, "ice_cube_eyelash_index" = the index its Weld driver uses.

EYELASH_PREFIX = "ice_cube.eyelashes_"

# identifier, label, description, collection_id - these four never change order,
# custom styles are appended behind them (see GetEyelashStyles)
BUILTIN_EYELASH_STYLES = (
    ("1", "None", "No Eyelashes", None),
    ("2", "Standard", "Standard Ice Cube Eyelashes", "ice_cube.eyelashes_default"),
    ("3", "Andromeda", "Andromeda Styled Eyelashes", "ice_cube.eyelashes_andromeda"),
    ("4", "Bushy", "Bushy Eyelashes", "ice_cube.eyelashes_bushy"),
)

def GetRigCollections(rig):
    """main collection of the rig plus every child collection (what the addon searches through)"""
    try:
        for collection in rig.users_collection:
            if collection.get('ice_cube_collection_id') == 'ice_cube.main':
                return [collection] + list(collection.children_recursive)
    except (AttributeError, TypeError):
        pass
    try:
        return list(rig.users_collection)
    except (AttributeError, TypeError):
        return []

def GetEyelashStyles(rig):
    """
    Returns every eyelash style of this rig as (identifier, label, description, collection_id).

    The four built-in styles are always first so the stored values of existing files stay
    valid, then every custom collection whose id starts with "ice_cube.eyelashes_" is added,
    ordered by its "ice_cube_eyelash_index" custom prop (fallback: alphabetically by id).

    NOTE: the identifier is the position in this list, and drivers in the .blend compare
    against (identifier - 1) - enums are read as their 0 based index inside drivers.
    """
    styles = [tuple(style) for style in BUILTIN_EYELASH_STYLES]

    builtin_ids = {style[3] for style in BUILTIN_EYELASH_STYLES}
    extras = []

    for collection in GetRigCollections(rig):
        collection_id = collection.get('ice_cube_collection_id')
        if not isinstance(collection_id, str):
            continue
        if not collection_id.startswith(EYELASH_PREFIX) or collection_id in builtin_ids:
            continue

        label = collection.get('ice_cube_eyelash_label')
        if not isinstance(label, str) or not label:
            label = collection.name
            if label.lower().startswith("eyelashes"):
                label = label[len("eyelashes"):]
            label = label.replace("_", " ").strip().title() or collection_id

        try:
            order = int(collection['ice_cube_eyelash_index'])
        except (KeyError, TypeError, ValueError):
            order = 9999

        extras.append((order, collection_id, label))

    extras.sort()
    for position, (_, collection_id, label) in enumerate(extras, start=len(styles) + 1):
        styles.append((str(position), label, f"Custom eyelash style: {label}", collection_id))

    return styles