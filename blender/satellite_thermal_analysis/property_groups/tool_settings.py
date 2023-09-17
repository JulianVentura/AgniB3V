import bpy

class ThermalToolSettings(bpy.types.PropertyGroup):
    solar_direction_vector : bpy.props.FloatVectorProperty()
    ray_cast_displacement : bpy.props.FloatProperty()