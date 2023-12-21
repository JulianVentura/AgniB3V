from test_config import *
from src import vtk_io
import numpy as np


def test_vtk_geometry_loading():
    mesh = vtk_io.load_vtk(BACKWARDS_PYRAMID_GEOMETRY_PATH)
    assert len(mesh.vertices) == 4
    assert len(mesh.triangles) == 4
