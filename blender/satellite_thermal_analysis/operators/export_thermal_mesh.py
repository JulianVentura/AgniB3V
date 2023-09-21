import bpy
import bmesh
import os


class ExportThermalMesh(bpy.types.Operator):
    bl_idname = "thermal.export_mesh"
    bl_label = "Exportar malla térmica"

    def execute(self, context):
        obj = bpy.context.active_object
        file = open(os.environ["HOME"] + "/" + obj.name + ".csv", "w")
        bpy.ops.object.mode_set(mode="EDIT")
        bm = bmesh.from_edit_mesh(obj.data)
        weights = {}
        for f in obj.data.polygons:
            for v in f.vertices:
                if not v in weights:
                    weights[v] = 0
                weights[v] += f.area / len(f.vertices)

        for v in bm.verts:
            neighbors = []
            for edge in v.link_edges:
                for neighbour_v in edge.verts:
                    if neighbour_v.index != v.index:
                        neighbors.append(neighbour_v.index)
            file.write(
                ",".join(
                    map(
                        str,
                        [v.index, v.co.x, v.co.y, v.co.z]
                        + [weights[v.index]]
                        + [0]
                        + [0]
                        + neighbors,
                    )
                )
                + "\n"
            )
            # Index,x,y,z,area,temperature,heat_flux,neighbors
        return {"FINISHED"}
