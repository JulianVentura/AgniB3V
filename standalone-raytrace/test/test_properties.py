from .test_config import *
from src import vtk_io, utils, properties_atlas
import json

test_property = {"a": 0, "b": [1,2,3]}

def test_properties_loading():
    mesh = vtk_io.load_vtk(ICOSPHERE_GEOMETRY_PATH)
    properties = properties_atlas.PropertiesAtlas(len(mesh.triangles), ICOSPHERE_PROPERTIES_PATH)
    
    for element_id in range(utils.element_amount(mesh.triangles)):
        material = properties.get_material_props(element_id)
        if element_id <= 9:
            assert material["test_id"] == 0
            assert material["absorptance"] == 0.75
            assert material["color"] == [255,0,0,255]
        else:
            assert material["test_id"] == 1
            assert material["absorptance"] == 0.25
            assert material["color"] == [0,255,0,255]

def test_property_add():
    mesh = vtk_io.load_vtk(ICOSPHERE_GEOMETRY_PATH)
    properties = properties_atlas.PropertiesAtlas(len(mesh.triangles), ICOSPHERE_PROPERTIES_PATH)
    properties.add_prop("test", test_property)
    assert properties.material_json["test"] == test_property

def test_property_dump():
    mesh = vtk_io.load_vtk(ICOSPHERE_GEOMETRY_PATH)
    properties = properties_atlas.PropertiesAtlas(len(mesh.triangles), ICOSPHERE_PROPERTIES_PATH)
    properties.add_prop("test", test_property)
    properties.dump(ICOSPHERE_OUTPUT_PROPERTIES_PATH)
    
    output_properties_file = open(ICOSPHERE_OUTPUT_PROPERTIES_PATH)
    expected_output_properties_file = open(ICOSPHERE_EXPECTED_OUTPUT_PROPERTIES_PATH)
    output_properties = json.load(output_properties_file)
    expected_output_properties = json.load(expected_output_properties_file)
    assert json.dumps(output_properties, sort_keys=True) == json.dumps(expected_output_properties, sort_keys=True)