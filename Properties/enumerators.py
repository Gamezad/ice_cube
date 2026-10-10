import bpy
from bpy.props import (
    EnumProperty,
)

#-------------------------------------------------#
#                     Updates
#-------------------------------------------------#
def generic_update(self, context):
    pass


# Arm Types
bpy.types.Object.arm_type = EnumProperty(
    name = "Arm Type Selection",
    default='1',
    items=[
        ('1', 'Steve', '4x4 Arms'),
        ('2', 'Alex', '4x3 Arms'),
        ('3', 'Thin', '3x3 Arms')
    ],
    update=generic_update,
    override={"LIBRARY_OVERRIDABLE"}
)

bpy.types.Object.left_arm_IK_parent = EnumProperty(
    name = "Left Arm IK Parent",
    default='root',
    items = [
        ('root','Root','Parents the IK controller to the root bone'),
        ('waist','Waist','Parents the IK controller to the waist bone'),
        ('body','Body','Parents the IK controller to the body bone'),
        ('local','Local','Treats the IK controller as just another control method'),
        ('world','World','Lets the IK controller free-float, useful for custom parenting')
    ]
)

bpy.types.Object.right_arm_IK_parent = EnumProperty(
    name = "Right Arm IK Parent",
    default='root',
    items = [
        ('root','Root','Parents the IK controller to the root bone'),
        ('waist','Waist','Parents the IK controller to the waist bone'),
        ('body','Body','Parents the IK controller to the body bone'),
        ('local','Local','Treats the IK controller as just another control method'),
        ('world','World','Lets the IK controller free-float, useful for custom parenting')
    ]
)

bpy.types.Object.left_leg_IK_parent = EnumProperty(
    name = "Left Leg IK Parent",
    default='root',
    items = [
        ('root','Root','Parents the IK controller to the root bone'),
        ('waist','Waist','Parents the IK controller to the waist bone'),
        ('body','Body','Parents the IK controller to the body bone'),
        ('world','World','Lets the IK controller free-float, useful for custom parenting')
    ]
)

bpy.types.Object.right_leg_IK_parent = EnumProperty(
    name = "Right Leg IK Parent",
    default='root',
    items = [
        ('root','Root','Parents the IK controller to the root bone'),
        ('waist','Waist','Parents the IK controller to the waist bone'),
        ('body','Body','Parents the IK controller to the body bone'),
        ('world','World','Lets the IK controller free-float, useful for custom parenting')
    ]
)


# Enums whose items are generated at runtime have to use the item *index* as default
# (Blender doesn't accept an identifier string there), so "0" = the first item = "None".
# Operators/reset_all.py has a matching fallback because prop.default can't report it.
EYELASH_DEFAULT = 0
EYELASH_DEFAULT_IDENTIFIER = '1'

def eyelash_type_items(self, context):
    """
    Built in styles + every custom "ice_cube.eyelashes_*" collection found on the rig,
    so a new style only has to be added to the .blend (see dev/add_eyelash_style.py).
    """
    from ..ice_cube_selectors import BUILTIN_EYELASH_STYLES, GetEyelashStyles
    try:
        return [(identifier, label, description) for identifier, label, description, _ in GetEyelashStyles(self)]
    except Exception:
        return [(identifier, label, description) for identifier, label, description, _ in BUILTIN_EYELASH_STYLES]

bpy.types.Object.eyelashes = EnumProperty(
    name = "Eyelash Type",
    default=EYELASH_DEFAULT,
    items=eyelash_type_items,
    override={"LIBRARY_OVERRIDABLE"}
)

bpy.types.Object.eyelashes_lower = EnumProperty(
    name = "Eyelash Lower Type",
    default='1',
    items=[
        ('1', 'None', 'No Eyelashes'),
        ('2', 'Standard', 'Standard Ice Cube Eyelashes'),
        ('3', 'Bushy', 'Bushy Eyelashes')
    ],
    override={"LIBRARY_OVERRIDABLE"}
)

bpy.types.Object.performance_mode = EnumProperty(
    name="Animation Mode",
    default='2',
    items=[
        ('1', 'Performance','Displays graybox meshes ONLY'),
        ('2', 'High Quality','Full quality mesh display')
    ],
    override={"LIBRARY_OVERRIDABLE"}
)

bpy.types.Object.emotion_eye_shape = EnumProperty(
    name="Eye Shape",
    default='0',
    items=[
        ('0', 'None','No eyeshape'),
        ('1', 'Dizzy','Dizzy Eyeshape'),
        ('2', 'X','X Eyeshape'),
        ('3', 'Happy','Happy Eyeshape'),
        ('4', 'Money','Dollar Eyeshape'),
        ('5', 'Star','Star Eyeshape'),
        ('6', 'Heart','Heart Eyeshape')
    ],
    override={"LIBRARY_OVERRIDABLE"}
)