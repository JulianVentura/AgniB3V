import bpy
import bmesh
import csv

TEMPERATURE_LAYER_ID = "thermal.temperature_layer"

class LoadTemperatureValues(bpy.types.Operator):
    bl_idname = "thermal.load_temperature_values"
    bl_label = "Cargar valores"

    def execute(self, context):
        tool_settings = context.scene.thermal_tool_settings
        mesh_file_path = tool_settings.mesh_file_path

        max_temp = None
        min_temp = None

        with open(mesh_file_path) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')

            obj = bpy.context.active_object
            bpy.ops.object.mode_set(mode="EDIT")
            bm = bmesh.from_edit_mesh(obj.data)
            temperature_layer = bm.verts.layers.float.get(TEMPERATURE_LAYER_ID) or bm.verts.layers.float.new(TEMPERATURE_LAYER_ID)
            bm.verts.ensure_lookup_table()
            for row in csv_reader:
                vertex_index = int(row[0])
                vertex_temperature = float(row[1]) 

                bm.verts[vertex_index][temperature_layer] = vertex_temperature

        return {"FINISHED"}
