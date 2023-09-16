import bpy
from .ui import panels
from .operators import export_thermal_mesh, calc_solar_view_factor

bl_info = {
    "name": "Satellite Thermal Analysis",
    "blender": (3, 6, 2),
    "category": "Object",
}

def register():
    bpy.utils.register_class(export_thermal_mesh.ExportThermalMesh)
    bpy.utils.register_class(calc_solar_view_factor.CalcSolarViewFactor)
    bpy.utils.register_class(panels.ThermalAnalysisPanel)

def unregister():
    bpy.utils.unregister_class(panels.ThermalAnalysisPanel)