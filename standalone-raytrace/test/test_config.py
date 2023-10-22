import sys
import os

ICOSPHERE_GEOMETRY_PATH = "./test/models/icosphere.vtk"
ICOSPHERE_PROPERTIES_PATH = "./test/models/icosphere.json"
OUTPUT_PROPERTIES_PATH = "./test/icosphere_output.json"
EXPECTED_OUTPUT_PROPERTIES_PATH = "./test/models/expected_icosphere_output.json"
sys.path.append(os.path.dirname(os.path.abspath(__file__)))