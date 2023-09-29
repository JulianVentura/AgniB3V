import bpy
import bmesh
from mathutils.bvhtree import BVHTree
import mathutils

class CalcSolarViewFactor(bpy.types.Operator):
    bl_idname = "thermal.calc_solar_view_factor"
    bl_label = "Calcular factor de vista solar"

    def invoke(self, context, event): # Used for user interaction
        wm = context.window_manager
        return wm.invoke_props_dialog(self)
    
    def execute(self, context):
        obj = bpy.context.active_object
        bpy.ops.object.mode_set(mode='OBJECT')

        depsgraph = bpy.context.evaluated_depsgraph_get()
        bvhtree = BVHTree.FromObject(obj, depsgraph)

        visible_vertices = set()
        tool_settings = context.scene.thermal_tool_settings
        solar_direction_vector = mathutils.Vector(tool_settings.solar_direction_vector)
        if (solar_direction_vector == [0,0,0]):
            solar_direction_vector = (bpy.data.objects['Cube'].location - bpy.data.objects['Sun'].location).normalize()
        print(solar_direction_vector)
        ray_cast_displacement = tool_settings.ray_cast_displacement

        for vert in obj.data.vertices:
            location, normal, index, dist = bvhtree.ray_cast(vert.co -ray_cast_displacement*solar_direction_vector, -solar_direction_vector)
            if not location:
                visible_vertices.add(vert.index)

        bpy.ops.object.mode_set(mode = 'EDIT')

        bm = bmesh.from_edit_mesh(obj.data)
        collayer = bm.verts.layers.float_color.new("Visible")
        for v in bm.verts:
            visible = 1 if v.index in visible_vertices else 0
            v[collayer] = [visible, 0, 1 - visible, 1]

        bpy.ops.object.mode_set(mode = 'VERTEX_PAINT')
        obj.data.attributes.active_color_index = 0
        obj.data.attributes.render_color_index = 0
        return {'FINISHED'}

