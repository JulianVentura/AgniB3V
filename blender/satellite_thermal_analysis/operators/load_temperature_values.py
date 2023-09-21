import bpy
import bmesh
import csv

class LoadTemperatureValues(bpy.types.Operator):
    bl_idname = "thermal.load_temperature_values"
    bl_label = "Cargar valores"

    def execute(self, context):
        tool_settings = context.scene.thermal_tool_settings
        mesh_file_path = tool_settings.mesh_file_path
        with open(mesh_file_path) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')

            obj = bpy.context.active_object
            bpy.ops.object.mode_set(mode="EDIT")
            bm = bmesh.from_edit_mesh(obj.data)
            temperature_layer = bm.verts.layers.float.new("Temperatura")
            bm.verts.ensure_lookup_table()
            for row in csv_reader:
                vertex_index = int(row[0])
                vertex_temperature = float(row[1]) 
                bm.verts[vertex_index][temperature_layer] = vertex_temperature

        return {"FINISHED"}
