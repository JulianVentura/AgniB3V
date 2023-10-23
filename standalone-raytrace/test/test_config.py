import sys
import os

ICOSPHERE_GEOMETRY_PATH = "./test/models/icosphere.vtk"
ICOSPHERE_PROPERTIES_PATH = "./test/models/icosphere.json"
ICOSPHERE_OUTPUT_PROPERTIES_PATH = "./test/icosphere_output.json"
ICOSPHERE_EXPECTED_OUTPUT_PROPERTIES_PATH = "./test/models/expected_icosphere_output.json"

BACKWARDS_PYRAMID_GEOMETRY_PATH = "./test/models/backwards_pyramid.vtk"
BACKWARDS_PYRAMID_PROPERTIES_PATH_NO_REFLECTIONS = "./test/models/backwards_pyramid_no_reflections.json"
BACKWARDS_PYRAMID_PROPERTIES_PATH_HALF_REFLECTIONS = "./test/models/backwards_pyramid_half_reflections.json"
BACKWARDS_PYRAMID_PROPERTIES_PATH_HALF_REFLECTIONS_HALF_ABSORTANCE = "./test/models/backwards_pyramid_half_reflection_half_absortance.json"
BACKWARDS_PYRAMID_PROPERTIES_PATH_FULL_REFLECTIONS = "./test/models/backwards_pyramid_full_reflections.json"

sys.path.append(os.path.dirname(os.path.abspath(__file__)))