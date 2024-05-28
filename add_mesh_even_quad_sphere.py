import bpy
from bpy_extras import object_utils
from itertools import permutations
from math import (
        copysign, pi,
        sqrt, tan,
        )
from bpy.types import Operator
from bpy.props import (
        BoolProperty,
        EnumProperty,
        FloatProperty,
        FloatVectorProperty,
        IntProperty,
        StringProperty,
        )


def even_quad_sphere(slices, size):
    lines = slices + 1
    # totalVerts = 6 * (slices - 1) * (slices - 1) + 12 * (slices - 1) + 8
    # totalEdges = 12 * slices + 6 * 2 * (slices - 1) * slices
    # totalFaces = 6 * slices * slices
    verts = []
    sideVerts = [[None]*lines*lines, [None]*lines*lines, [None]*lines*lines, [None]*lines*lines, [None]*lines*lines, [None]*lines*lines]
    vertIndex = 0

    # Top
    for z in range(0, slices + 1):
        for x in range(0, slices + 1):
            i = x + z * lines
            sideVerts[0][i] = vertIndex
            vertIndex = vertIndex + 1
            verts.append([0.0, 0.0, 0.0])

    # Front
    for y in range(0, slices + 1):
        for x in range(0, slices + 1):
            i = x + y * lines
            if y == slices:
                sideVerts[1][i] = sideVerts[0][x]
            else:
                sideVerts[1][i] = vertIndex
                vertIndex = vertIndex + 1
                verts.append([0.0, 0.0, 0.0])

    # Right
    for y in range(0, slices + 1):
        for z in range(0, slices + 1):
            i = z + y * lines
            if z == 0:
                sideVerts[2][i] = sideVerts[1][i + slices]
            elif y == slices:
                sideVerts[2][i] = sideVerts[0][slices + z * lines]
            else:
                sideVerts[2][i] = vertIndex
                vertIndex = vertIndex + 1
                verts.append([0.0, 0.0, 0.0])

    # Back
    for y in range(0, slices + 1):
        for x in range(0, slices + 1):
            i = x + y * lines
            if x == slices:
                sideVerts [3][i] = sideVerts[2][i]
            elif y == slices:
                sideVerts [3][i] = sideVerts[0][i]
            else:
                sideVerts [3][i] = vertIndex
                vertIndex = vertIndex + 1
                verts.append([0.0, 0.0, 0.0])

    # Left
    for y in range(0, slices + 1):
        for z in range(0, slices + 1):
            i = z + y * lines
            if z == 0:
                sideVerts [4][i] = sideVerts [1][i]
            elif y == slices:
                sideVerts [4][i] = sideVerts [0][z * lines]
            elif z == slices:
                sideVerts [4][i] = sideVerts [3][i - slices]
            else:
                sideVerts [4][i] = vertIndex
                vertIndex = vertIndex + 1
                verts.append([0.0, 0.0, 0.0])

    # Bottom
    for z in range(0, slices + 1):
        for x in range(0, slices + 1):
            i = x + z * lines
            if z == 0:
                sideVerts [5][i] = sideVerts [1][x]
            elif z == slices:
                sideVerts [5][i] = sideVerts [3][x]
            elif x == slices:
                sideVerts [5][i] = sideVerts [2][z]
            elif x == 0:
                sideVerts [5][i] = sideVerts [4][z]
            else:
                sideVerts [5][i] = vertIndex
                vertIndex = vertIndex + 1
                verts.append([0.0, 0.0, 0.0])

    faces = []
    tempVerts = []
    for s in range(0, 6):
        invertedWinding = (s == 3) or (s == 4) or (s == 5)
        for y in range(0, slices):
            for x in range(0, slices):
                i = x + y * lines
                tempVerts.clear()
                if invertedWinding:
                    tempVerts.append(sideVerts[s][i])
                    tempVerts.append(sideVerts[s][i + 1])
                    tempVerts.append(sideVerts[s][i + 1 + lines])
                    tempVerts.append(sideVerts[s][i + lines])
                else:
                    tempVerts.append(sideVerts[s][i])
                    tempVerts.append(sideVerts[s][i + lines])
                    tempVerts.append(sideVerts[s][i + lines + 1])
                    tempVerts.append(sideVerts[s][i + 1])
                faces.append(tuple(tempVerts))

    sides = ((0, 1, 0), (0, 0, -1), (1, 0, 0), (0, 0, 1), (-1, 0, 0), (0, -1, 0))
    xDirections = ((1, 0, 0), (1, 0, 0), (0, 0, 1), (1, 0, 0), (0, 0, 1), (1, 0, 0))
    yDirections = ((0, 0, 1), (0, 1, 0), (0, 1, 0), (0, 1, 0), (0, 1, 0), (0, 0, 1))
    quarterPi = pi / 4
    for s in range(0, 6):
        side = sides[s]
        xDir = xDirections[s]
        yDir = yDirections[s]
        for y in range(0, slices + 1):
            for x in range(0, slices + 1):
                i = x + y * lines

                # Range -1 to 1.
                xLinear = (2 * x - slices) / slices
                yLinear = (2 * y - slices) / slices

                # More even distribution
                xLinear = tan(xLinear * quarterPi)
                yLinear = tan(yLinear * quarterPi)
                
                newPos = [side[i] + xLinear * xDir[i] + yLinear * yDir[i] for i in range(0, 3)]
                newPosLen = (newPos[0]*newPos[0] + newPos[1]*newPos[1] + newPos[2]*newPos[2]) ** (1/2)
                newPos = [newPos[i] / newPosLen for i in range(0, 3)]
                verts[sideVerts[s][i]][0] = newPos[0]
                verts[sideVerts[s][i]][1] = newPos[1]
                verts[sideVerts[s][i]][2] = newPos[2]

    return [(v[0] * size, v[1] * size, v[2] * size) for v in verts], faces

class AddEvenQuadSphere(Operator, object_utils.AddObjectHelper):
    bl_idname = "mesh.primitive_even_quad_sphere_add"
    bl_label = "Add Even Quad Sphere"
    bl_description = ("Create an even quad sphere")
    bl_options = {"REGISTER", "UNDO", "PRESET"}

    slices: IntProperty(name="Slices", description="Amount of quads in each direction", default=8, min=1, soft_min=2, soft_max=128, max=512, step=1)
    size: FloatProperty(name="Size", description="Size multiplier", default=1.0, min=0.000001, soft_min=0.001, soft_max=4096, max=1000000000, step=1)
    change: BoolProperty(name="Change")

    def execute(self, context):
        # turn off 'Enter Edit Mode'
        use_enter_edit_mode = bpy.context.preferences.edit.use_enter_edit_mode
        bpy.context.preferences.edit.use_enter_edit_mode = False

        if bpy.context.mode == "OBJECT":
            if context.selected_objects != [] and context.active_object and \
                (context.active_object.data is not None) and ('EvenQuadSphere' in context.active_object.data.keys()) and \
                (self.change == True):
                obj = context.active_object
                oldmesh = obj.data
                oldmeshname = obj.data.name
                verts, faces = even_quad_sphere(self.slices, self.size)
                mesh = bpy.data.meshes.new('EvenQuadSphere')
                mesh.from_pydata(verts, [], faces)
                obj.data = mesh
                for material in oldmesh.materials:
                    obj.data.materials.append(material)
                bpy.data.meshes.remove(oldmesh)
                obj.data.name = oldmeshname
            else:
                verts, faces = even_quad_sphere(self.slices, self.size)
                mesh = bpy.data.meshes.new('EvenQuadSphere')
                mesh.from_pydata(verts, [], faces)
                obj = object_utils.object_data_add(context, mesh, operator=self)

            obj.data["EvenQuadSphere"] = True
            obj.data["change"] = False
            for prm in EvenQuadSphereParameters():
                obj.data[prm] = getattr(self, prm)

        if bpy.context.mode == "EDIT_MESH":
            active_object = context.active_object
            name_active_object = active_object.name
            bpy.ops.object.mode_set(mode='OBJECT')
            verts, faces = even_quad_sphere(self.slices, self.size)
            mesh = bpy.data.meshes.new('EvenQuadSphere')
            mesh.from_pydata(verts, [], faces)
            obj = object_utils.object_data_add(context, mesh, operator=self)
            obj.select_set(True)
            active_object.select_set(True)
            bpy.context.view_layer.objects.active = active_object
            bpy.ops.object.join()
            context.active_object.name = name_active_object
            bpy.ops.object.mode_set(mode='EDIT')

        if use_enter_edit_mode:
            bpy.ops.object.mode_set(mode = 'EDIT')

        # restore pre operator state
        bpy.context.preferences.edit.use_enter_edit_mode = use_enter_edit_mode

        return {'FINISHED'}

    def invoke(self, context, event):
        return self.execute(context)

    def draw(self, context):
        layout = self.layout

        layout.prop(self, 'slices')
        layout.column().prop(self, 'size', expand=True)

        if self.change == False:
            col = layout.column(align=True)
            col.prop(self, 'align', expand=True)
            col = layout.column(align=True)
            col.prop(self, 'location', expand=True)
            col = layout.column(align=True)
            col.prop(self, 'rotation', expand=True)

def EvenQuadSphereParameters():
    EvenQuadSphereParameters = [
        "slices",
        "size",
        ]
    return EvenQuadSphereParameters
