import sys
import os

ICOSPHERE_GEOMETRY_PATH = "./test/models/icosphere.vtk"
ICOSPHERE_PROPERTIES_PATH = "./test/models/icosphere.json"
ICOSPHERE_OUTPUT_PROPERTIES_PATH = "./test/icosphere_output.json"
ICOSPHERE_EXPECTED_OUTPUT_PROPERTIES_PATH = (
    "./test/models/expected_icosphere_output.json"
)

BACKWARDS_PYRAMID_GEOMETRY_PATH = "./test/models/backwards_pyramid.vtk"
BACKWARDS_PYRAMID_PROPERTIES_PATH_NO_REFLECTIONS = (
    "./test/models/backwards_pyramid_no_reflections.json"
)
BACKWARDS_PYRAMID_PROPERTIES_PATH_HALF_REFLECTIONS = (
    "./test/models/backwards_pyramid_half_reflections.json"
)
BACKWARDS_PYRAMID_PROPERTIES_PATH_HALF_REFLECTIONS_HALF_ABSORTANCE = (
    "./test/models/backwards_pyramid_half_reflection_half_absortance.json"
)
BACKWARDS_PYRAMID_PROPERTIES_PATH_FULL_REFLECTIONS = (
    "./test/models/backwards_pyramid_full_reflections.json"
)
BACKWARDS_PYRAMID_PROPERTIES_PATH_MIXED_EMISSION = (
    "./test/models/backwards_pyramid_mixed_emission.json"
)

BACKWARDS_DIAMOND_GEOMETRY_PATH = "./test/models/backwards_diamond.vtk"
BACKWARDS_DIAMOND_PROPERTIES_PATH = "./test/models/backwards_diamond.json"
BACKWARDS_DIAMOND_INTERNAL_ELEMENT_ID = 1

RING_GEOMETRY_PATH = "./test/models/ring.vtk"

ARROWS_GEOMETRY_PATH = "./test/models/arrows.vtk"

GMAT_REPORT_FILE_PATH = "./test/models/gmat_report.txt"
GMAT_ECLIPSE_LOCATOR_FILE_PATH = "./test/models/gmat_eclipse_locator.txt"
GMAT_ECLIPSE_LOCATOR_FILE_PATH_NO_ECLIPSE = (
    "./test/models/gmat_eclipse_locator_no_eclipse.txt"
)

sys.path.append("..")
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
