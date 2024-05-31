bl_info = {
    "name": "Even Quad Sphere",
    "description": "Special case of quad sphere which maximizes equality of edge lengths",
    "author": "Zyl",
    "version": (1, 1),
    "blender": (2, 93, 0),
    "category": "Add Mesh"
}

if "bpy" in locals():
    import importlib
    importlib.reload(add_mesh_even_quad_sphere)
else:
    from . import add_mesh_even_quad_sphere

import bpy

addonClasses = [
    add_mesh_even_quad_sphere.AddEvenQuadSphere,
]

def menu_func(self, context):
    layout = self.layout
    layout.operator("mesh.primitive_even_quad_sphere_add",
        text="Even Quad Sphere", icon="SPHERE")
    pass

def register():
    for addonClass in addonClasses:
        bpy.utils.register_class(addonClass)
    bpy.types.VIEW3D_MT_mesh_add.append(menu_func)


def unregister():
    bpy.types.VIEW3D_MT_mesh_add.remove(menu_func)
    for addonClass in reversed(addonClasses):
        bpy.utils.unregister_class(addonClass)
