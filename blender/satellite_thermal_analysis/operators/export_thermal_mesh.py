import bpy
import bmesh
import os

class ExportThermalMesh(bpy.types.Operator):
    bl_idname = "thermal.export_mesh"
    bl_label = "Exportar malla térmica"

    def execute(self, context):
        obj = bpy.context.active_object
        f = open(os.environ["HOME"] + "/" + obj.name + ".csv", "w")
        bpy.ops.object.mode_set(mode = 'EDIT')
        bm = bmesh.from_edit_mesh(obj.data)
        for v in bm.verts:
            neighbors = []
            for edge in v.link_edges:
                for neighbour_v in edge.verts:
                    if neighbour_v.index != v.index:
                        neighbors.append(neighbour_v.index)
            f.write(",".join(map(str, [v.index, v.co.x, v.co.y, v.co.z] + neighbors)) + "\n")
        return {'FINISHED'}
