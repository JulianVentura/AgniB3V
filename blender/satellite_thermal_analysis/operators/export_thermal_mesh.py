import bpy

class ExportThermalMesh(bpy.types.Operator):
    bl_idname = "thermal.export_mesh"
    bl_label = "Exportar malla térmica"

    def execute(self, context):
        print("Hello World")
        return {'FINISHED'}
