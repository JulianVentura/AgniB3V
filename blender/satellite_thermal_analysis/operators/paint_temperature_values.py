import bpy
import bmesh

class PaintTemperatureValues(bpy.types.Operator):
    bl_idname = "thermal.paint_temperature_values"
    bl_label = "Representar valores"

    def execute(self, context):
        bpy.ops.object.mode_set(mode = 'EDIT')
        obj = bpy.context.active_object
        bm = bmesh.from_edit_mesh(obj.data)
        temperature_layer = bm.verts.layers.float.get("thermal.temperature_layer")
        color_layer = bm.verts.layers.float_color.new("Temperatura")

        max_temp = None
        min_temp = None
        for v in bm.verts:
            temperature = v[temperature_layer]
            if not max_temp or temperature > max_temp:
                max_temp = temperature
            if not min_temp or temperature < min_temp:
                min_temp = temperature

        if (min_temp == max_temp):
            min_temp = 0
        
        for v in bm.verts:
            temperature = (v[temperature_layer] - min_temp)/(max_temp - min_temp)
            v[color_layer] = [temperature, 0, 1 - temperature, 1]

        bpy.ops.object.mode_set(mode = 'VERTEX_PAINT')
        obj.data.attributes.active_color_index = 0
        obj.data.attributes.render_color_index = 0

        return {"FINISHED"}
