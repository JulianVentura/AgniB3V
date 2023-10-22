from .test_config import *
from src import vtk_io

def test_vtk_geometry_loading():
    mesh = vtk_io.load_vtk(ICOSPHERE_GEOMETRY_PATH)
    assert len(mesh.triangles) == 20
