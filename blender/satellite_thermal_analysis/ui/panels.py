import bpy
import bmesh

class ThermalAnalysisPanel(bpy.types.Panel):
    bl_label = "Analisis Termico"
    bl_idname = "OBJECT_PT_ThermalAnalysis"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

    def draw(self, context):
        layout = self.layout
        obj = context.object

        column = layout.column()
        column.label(text="Configuración")
        column.prop(context.scene.thermal_tool_settings, "solar_direction_vector")
        column.prop(context.scene.thermal_tool_settings, "ray_cast_displacement", text="Desplazamiento", slider=True)
        column.label(text="Malla")
        column.operator("thermal.export_mesh", text="Exportar")
        column.operator("thermal.export_mesh_second", text="Exportar 2")
        column.label(text="Factor de vista solar")
        column.operator("thermal.calc_solar_view_factor", text="Calcular")
        column.label(text="Resultados")
        column.prop(context.scene.thermal_tool_settings, "mesh_file_path", text="")
        column.operator("thermal.load_temperature_values", text="Cargar")
        column.operator("thermal.paint_temperature_values", text="Pintar")

        if (bpy.context.object.mode != 'EDIT'):
            return

        bm = bmesh.from_edit_mesh(obj.data)
        temperature_layer = bm.verts.layers.float.active
        if(temperature_layer):
            selected_vertices = []
            for v in bm.verts:
                if v.select:
                    selected_vertices.append(v)
            if len(selected_vertices) == 0:
                return
            t_prom = sum(map(lambda v: v[temperature_layer], selected_vertices))/len(selected_vertices)
            column.label(text="T. promedio: {:10.4f}".format(t_prom))
