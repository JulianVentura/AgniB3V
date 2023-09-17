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

        row = layout.row()
        row.prop(context.scene.thermal_tool_settings, "solar_direction_vector")
        row.prop(context.scene.thermal_tool_settings, "ray_cast_displacement")
        
        row = layout.row()
        row.operator("thermal.export_mesh")
        
        row = layout.row()
        calc_solar_view_factor = row.operator("thermal.calc_solar_view_factor")
        #calc_solar_view_factor.solar_direction_vector = [0,0,-1]
        #calc_solar_view_factor.ray_cast_displacement = 0.01


