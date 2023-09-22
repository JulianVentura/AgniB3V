import bpy

class ThermalToolSettings(bpy.types.PropertyGroup):
    solar_direction_vector : bpy.props.FloatVectorProperty(name="Solar Direction Vector", default=(0.0,0.0,-1.0))
    ray_cast_displacement : bpy.props.FloatProperty(name="Desplazamiento de Raycast", default=0.01, min=0.001, max=2)
    mesh_file_path : bpy.props.StringProperty(name="", description="Path to Directory", default="", maxlen=2048, subtype='FILE_PATH')