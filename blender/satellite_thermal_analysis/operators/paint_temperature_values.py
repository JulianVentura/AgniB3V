import bpy
import bmesh

class PaintTemperatureValues(bpy.types.Operator):
    bl_idname = "thermal.paint_temperature_values"
    bl_label = "Representar valores"

    def execute(self, context):
        bpy.ops.object.mode_set(mode = 'EDIT')
        MAX_TEMP = 300
        obj = bpy.context.active_object
        bm = bmesh.from_edit_mesh(obj.data)
        temperature_layer = bm.verts.layers.float.active
        color_layer = bm.verts.layers.float_color.new("Temperatura")
        for v in bm.verts:
            temperature = v[temperature_layer]/MAX_TEMP
            v[color_layer] = [temperature, 0, 1 - temperature, 1]

        bpy.ops.object.mode_set(mode = 'VERTEX_PAINT')
        obj.data.attributes.active_color_index = 0
        obj.data.attributes.render_color_index = 0

        return {"FINISHED"}
