import bpy

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
        column.label(text="Factor de vista solar")
        column.operator("thermal.calc_solar_view_factor", text="Calcular")
