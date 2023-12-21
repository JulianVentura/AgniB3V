from test_config import *
from src import mesh_ops, vtk_io
import numpy as np


def test_element_amount():
    mesh = vtk_io.load_vtk(ICOSPHERE_GEOMETRY_PATH)
    assert mesh_ops.element_amount(mesh) == 20


def test_mesh_look_at():
    directions = np.array(
        [[1, 0, 0], [0, 1, 0], [0, 0, 1], [0, 0, -1], [1, 1, 1], [2, 3, 4]]
    )
    expected_vertices = [
        [
            [1.0, 1.0, 1.0],
            [1.0, -1.0, -1.0],
            [1.0, 1.0, -1.0],
            [-1.0, 1.0, -1.0],
        ],
        [
            [-1.0, 1.0, 1.0],
            [1.0, 1.0, -1.0],
            [-1.0, 1.0, -1.0],
            [-1.0, -1.0, -1.0],
        ],
        [
            [1.0, 1.0, 1.0],
            [-1.0, -1.0, 1.0],
            [1.0, -1.0, 1.0],
            [1.0, -1.0, -1.0],
        ],
        [
            [1.0, -1.0, -1.0],
            [-1.0, 1.0, -1.0],
            [1.0, 1.0, -1.0],
            [1.0, 1.0, 1.0],
        ],
        [
            [-0.53800478, 0.87620878, 1.3938468],
            [1.69270532, 0.27849175, -0.23914626],
            [0.27849182, 1.6927053, -0.23914631],
            [-0.87620872, 0.53800476, -1.39384685],
        ],
        [
            [-0.87268056, 0.4937548, 1.41231538],
            [1.61546191, 0.62041722, 0.07324733],
            [-0.04863861, 1.72981762, 0.07324729],
            [-0.79141996, 0.61564559, -1.41231542],
        ],
    ]

    for i, direction in enumerate(directions):
        mesh = vtk_io.load_vtk(ARROWS_GEOMETRY_PATH)
        mesh_ops.look_at(mesh, direction)
        assert np.allclose(mesh.vertices, np.array(expected_vertices[i]).reshape(4, 3))
