import bpy
from .ui import panels, custom_materials
from .operators import export_thermal_mesh, calc_solar_view_factor, load_temperature_values, paint_temperature_values
from .property_groups import tool_settings

bl_info = {
    "name": "Satellite Thermal Analysis",
    "blender": (3, 6, 2),
    "category": "Object",
}

def register():
    bpy.utils.register_class(tool_settings.ThermalToolSettings)
    bpy.types.Scene.thermal_tool_settings = bpy.props.PointerProperty(type=tool_settings.ThermalToolSettings)
    bpy.utils.register_class(calc_solar_view_factor.CalcSolarViewFactor)
    bpy.utils.register_class(load_temperature_values.LoadTemperatureValues)
    bpy.utils.register_class(paint_temperature_values.PaintTemperatureValues)
    bpy.utils.register_class(export_thermal_mesh.ExportThermalMesh)
    bpy.utils.register_class(panels.ThermalAnalysisPanel)
    custom_materials.custom_materials_register()

def unregister():
    bpy.utils.unregister_class(panels.ThermalAnalysisPanel)
    bpy.utils.unregister_class(export_thermal_mesh.ExportThermalMesh)
    bpy.utils.unregister_class(paint_temperature_values.PaintTemperatureValues)
    bpy.utils.unregister_class(load_temperature_values.LoadTemperatureValues)
    bpy.utils.unregister_class(calc_solar_view_factor.CalcSolarViewFactor)
    del bpy.types.Scene.thermal_tool_settings
    bpy.utils.unregister_class(tool_settings.ThermalToolSettings)
    custom_materials.custom_materials_unregister()
