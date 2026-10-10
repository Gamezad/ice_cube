import bpy

from ..ice_cube_selectors import GetCollection, GetEyelashStyles

class ICECUBE_BAKE_RIG(bpy.types.Operator):
    bl_options = {'REGISTER', 'UNDO'}
    bl_idname = 'ice_cube.bake_rig'
    bl_label = "Bake Rig"

    def execute(self, context):
        rig = context.object
        rig_collections = rig.users_collection
        collections = GetCollection(rig_collections,"ice_cube.main").children_recursive
        
        delete_collections = []
        search_collections = []

        if rig.arm_type == '1':
            delete_collections.extend(['ice_cube.alex_l','ice_cube.alex_r','ice_cube.thin_l','ice_cube.thin_r'])
            search_collections.extend(['ice_cube.steve_l','ice_cube.steve_r'])
        
        if rig.arm_type == '2':
            delete_collections.extend(['ice_cube.steve_l','ice_cube.steve_r','ice_cube.thin_l','ice_cube.thin_r'])
            search_collections.extend(['ice_cube.alex_l','ice_cube.alex_r'])
        
        if rig.arm_type == '3':
            delete_collections.extend(['ice_cube.steve_l','ice_cube.steve_r','ice_cube.alex_l','ice_cube.alex_r'])
            search_collections.extend(['ice_cube.thin_l','ice_cube.thin_r'])

        # eyelashes: keep the selected style, delete every other one.
        # Works for custom styles too since the list is generated from the rig's collections.
        selected_eyelash_collection = None
        for identifier, label, description, collection_id in GetEyelashStyles(rig):
            if identifier == rig.eyelashes:
                selected_eyelash_collection = collection_id

        for identifier, label, description, collection_id in GetEyelashStyles(rig):
            if collection_id and collection_id != selected_eyelash_collection:
                delete_collections.append(collection_id)
        
        search_collections.extend(['ice_cube.head','ice_cube.body','ice_cube.face'])
        
        for collection in delete_collections:
            target_collection = GetCollection(collections,collection)
            if not target_collection:
                continue
            for mesh in target_collection.objects:
                bpy.data.objects.remove(mesh,do_unlink=True)
        
        ModifiersToApply = ["Cosmetic Lattice","Cosmetic Lattice Finger"]

        for collection in search_collections:
            for mesh in GetCollection(collections,collection).objects:
                for modifier in ModifiersToApply:
                    self.apply_modifier(mesh,modifier)

        return {'FINISHED'}
    
    def apply_modifier(self,mesh,modifier):
        context_override = {'object':mesh}
        try:
            with bpy.context.temp_override(**context_override):
                bpy.ops.object.modifier_apply(modifier=modifier)
        except RuntimeError:
            print(f"Could not apply modifiers for {mesh.name} because it has shape keys!")
    
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self,title="Bake rig confirmation?",confirm_text="Bake")