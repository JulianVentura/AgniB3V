import bpy
import bmesh
import os


class ExportThermalMeshSecond(bpy.types.Operator):
    bl_idname = "thermal.export_mesh_second"
    bl_label = "Exportar malla térmica 2"

    def execute(self, context):
        obj = bpy.context.active_object
        bpy.ops.object.mode_set(mode="EDIT")
        bm = bmesh.from_edit_mesh(obj.data)
        file_verts = open(os.environ["HOME"] + "/" + obj.name + "_verts.csv", "w")
        for v in bm.verts:
            file_verts.write(",".join(map(str,[v.index, v.co.x, v.co.y, v.co.z])) + "\n")
        file_verts.close()

        file_triangles = open(os.environ["HOME"] + "/" + obj.name + "_triangles.csv", "w")
        for f in obj.data.polygons:
            file_triangles.write(",".join(map(str,[f.index] + list(f.vertices))) + "\n")
        file_triangles.close()

        return {"FINISHED"}
