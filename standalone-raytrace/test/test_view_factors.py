from .test_config import *
from src import vtk_io, utils, properties_atlas, view_factors
import numpy as np


def _is_in_interval(value, center, epsilon):
    return value <= center + epsilon and value >= center - epsilon


#   /_15_|_19_\    .       /15 \             ___/_\___
#  | \10/ \14/ |     .    /   10\            \ /   \ /
#  |6_\/_5_\/_9|     .   |      5|  <-----   /_\___/_\
#   \0 \ 1 / 4/    .      \    0/               \ /
def test_element_sun_visible_faces():
    sun_direction = np.array([1, 0, 0])
    mesh = vtk_io.load_vtk(ICOSPHERE_GEOMETRY_PATH)
    earth_view_factors = view_factors.element_sun(mesh, sun_direction)
    earth_view_factors = np.ceil(earth_view_factors)
    expected_visible_elements = np.array([0, 1, 4, 5, 6, 9, 10, 14, 15, 19])
    expected_view_factors = np.zeros(20)
    expected_view_factors[expected_visible_elements] = 1
    assert np.array_equal(earth_view_factors, expected_view_factors)


def test_element_sun_view_factors_are_as_expected():
    mesh = vtk_io.load_vtk(ICOSPHERE_GEOMETRY_PATH)
    sun_direction = np.array([1, 0, 0])
    sun_view_factors = view_factors.element_sun(mesh, sun_direction)
    expected_view_factors = np.zeros(20)
    expected_view_factors[0] = 0.2
    expected_view_factors[1] = 0.6
    expected_view_factors[4] = expected_view_factors[0]
    expected_view_factors[5] = 1.0
    expected_view_factors[6] = 0.3
    expected_view_factors[9] = expected_view_factors[6]
    expected_view_factors[10] = 0.8
    expected_view_factors[14] = expected_view_factors[10]
    expected_view_factors[15] = 0.5
    expected_view_factors[19] = expected_view_factors[15]

    for i in range(20):
        assert _is_in_interval(sun_view_factors[i], expected_view_factors[i], 0.02)


def test_element_earth_visible_faces():
    earth_direction = np.array([1, 0, 0])
    sun_direction = np.array([1, 0, 0])
    mesh = vtk_io.load_vtk(ICOSPHERE_GEOMETRY_PATH)
    earth_view_factors, earth_albedo_coefficients = view_factors.element_earth(
        mesh, earth_direction, sun_direction, 0.05, 10000
    )
    earth_view_factors = np.ceil(earth_view_factors)
    expected_visible_elements = np.array([0, 1, 4, 5, 6, 9, 10, 14, 15, 19])
    expected_view_factors = np.zeros(20)
    expected_view_factors[expected_visible_elements] = 1
    assert np.array_equal(earth_view_factors, expected_view_factors)


def _test_element_earth_view_factors_are_as_expected(penumbra_fraction):
    earth_direction = np.array([1, 0, 0])
    sun_direction = np.array([-1, 0, 0])
    mesh = vtk_io.load_vtk(ICOSPHERE_GEOMETRY_PATH)
    earth_view_factors, earth_albedo_coefficients = view_factors.element_earth(
        mesh, earth_direction, sun_direction, penumbra_fraction, 10000
    )
    expected_view_factors = np.zeros(20)
    expected_view_factors[0] = 0.6
    expected_view_factors[1] = 0.7
    expected_view_factors[4] = expected_view_factors[0]
    expected_view_factors[5] = 1.0
    expected_view_factors[6] = 0.6
    expected_view_factors[9] = expected_view_factors[6]
    expected_view_factors[10] = 0.85
    expected_view_factors[14] = expected_view_factors[10]
    expected_view_factors[15] = 0.65
    expected_view_factors[19] = expected_view_factors[15]

    for i in range(20):
        assert _is_in_interval(
            earth_albedo_coefficients[i], expected_view_factors[i], 0.06
        )


def test_element_earth_view_factors_are_as_expected_without_penumbra():
    _test_element_earth_view_factors_are_as_expected(0)


def test_element_earth_view_factors_are_as_expected_with_penumbra():
    _test_element_earth_view_factors_are_as_expected(0.5)


def _test_penumbra(expected_lit_fractions, penumbra_fraction):
    SUBDIVISIONS = 16
    SUN_VECTOR = np.array([12, 0, 0])
    mesh = vtk_io.load_vtk(RING_GEOMETRY_PATH)
    for i in range(SUBDIVISIONS - 1):
        angle = (i / SUBDIVISIONS) * 2 * np.pi
        earth_vector = np.array([np.cos(angle), np.sin(angle), 0])
        earth_view_factors, earth_albedo_coefficients = view_factors.element_earth(
            mesh,
            -earth_vector,
            SUN_VECTOR,
            penumbra_fraction=penumbra_fraction,
            ray_amount=1000,
        )
        lit_fraction = (
            np.sum(earth_albedo_coefficients > 0.1) / earth_albedo_coefficients.size
        )
        assert _is_in_interval(lit_fraction, expected_lit_fractions[i], 0.06)


def test_penumbra_full_umbra():
    expected_lit_fractions = [
        0.5,
        0.5,
        0.5,
        0.4,
        0.4,
        0.3,
        0.2,
        0.0,
        0.0,
        0.0,
        0.2,
        0.3,
        0.3,
        0.4,
        0.5,
    ]
    _test_penumbra(expected_lit_fractions, 0)


def test_penumbra_half_umbra():
    expected_lit_fractions = [
        0.5,
        0.5,
        0.5,
        0.5,
        0.5,
        0.4,
        0.3,
        0.3,
        0.0,
        0.3,
        0.3,
        0.4,
        0.4,
        0.5,
        0.5,
    ]
    _test_penumbra(expected_lit_fractions, 0.5)


def test_penumbra_full_umbra():
    expected_lit_fractions = [
        0.5,
        0.5,
        0.5,
        0.5,
        0.5,
        0.5,
        0.5,
        0.5,
        0.5,
        0.5,
        0.5,
        0.5,
        0.5,
        0.5,
        0.5,
    ]
    _test_penumbra(expected_lit_fractions, 1.0)


def _element_element_backwards_pyramid(properties_path, ray_amount):
    mesh = vtk_io.load_vtk(BACKWARDS_PYRAMID_GEOMETRY_PATH)
    properties = properties_atlas.PropertiesAtlas(
        utils.element_amount(mesh.triangles), properties_path
    )
    return view_factors.element_element(
        mesh, properties.absortance_by_element, ray_amount, 50, False
    )


def test_element_element_backwards_pyramid_view_factors_rows_sum_one():
    element_element_view_factors = _element_element_backwards_pyramid(
        BACKWARDS_PYRAMID_PROPERTIES_PATH_NO_REFLECTIONS, 10000
    )
    for element_id in range(len(element_element_view_factors)):
        row = np.delete(element_element_view_factors[element_id], element_id)
        row_sum = np.sum(row)
        assert _is_in_interval(row_sum, 1, 0.2)


def test_element_element_backwards_pyramid_view_factors_rows_are_similar():
    element_element_view_factors_epsilon = 0.03
    element_element_view_factors = _element_element_backwards_pyramid(
        BACKWARDS_PYRAMID_PROPERTIES_PATH_NO_REFLECTIONS, 10000
    )
    for element_id in range(len(element_element_view_factors)):
        row = np.delete(element_element_view_factors[element_id], element_id)
        assert np.all(row < 1 / 3 + element_element_view_factors_epsilon)
        assert np.all(row > 1 / 3 - element_element_view_factors_epsilon)


def test_view_factors_full_reflections():
    element_element_view_factors = _element_element_backwards_pyramid(
        BACKWARDS_PYRAMID_PROPERTIES_PATH_FULL_REFLECTIONS, 10000
    )
    view_factors_sum = np.sum(element_element_view_factors)
    assert _is_in_interval(view_factors_sum, 0, sys.float_info.epsilon * 10)


def test_element_element_backwards_pyramid_view_factors_half_reflections_sum_one():
    element_element_view_factors = _element_element_backwards_pyramid(
        BACKWARDS_PYRAMID_PROPERTIES_PATH_HALF_REFLECTIONS, 10000
    )
    for row in element_element_view_factors:
        row_sum = np.sum(row)
        assert _is_in_interval(row_sum, 1, 0.2)


def test_element_element_backwards_pyramid_view_factors_half_reflections_are_correct():
    element_element_view_factors = _element_element_backwards_pyramid(
        BACKWARDS_PYRAMID_PROPERTIES_PATH_HALF_REFLECTIONS, 10000
    )
    expected_element_element_view_factors = (
        np.array(
            [
                [1 / 3, 2 / 3, 0, 0],
                [2 / 3, 1 / 3, 0, 0],
                [0.5, 0.5, 0, 0],
                [0.5, 0.5, 0, 0],
            ]
        ),
    )
    view_factors_errors = (
        element_element_view_factors - expected_element_element_view_factors
    )
    assert np.sum(view_factors_errors * view_factors_errors) < 0.02 * 16


def test_element_element_backwards_pyramid_view_factors_half_reflections_half_absortance_sum_one():
    element_element_view_factors = _element_element_backwards_pyramid(
        BACKWARDS_PYRAMID_PROPERTIES_PATH_HALF_REFLECTIONS_HALF_ABSORTANCE, 10000
    )
    for row in element_element_view_factors:
        row_sum = np.sum(row)
        assert _is_in_interval(row_sum, 1, 0.2)


def test_element_element_backwards_pyramid_view_factors_half_reflections_half_absortance_are_correct():
    element_element_view_factors = _element_element_backwards_pyramid(
        BACKWARDS_PYRAMID_PROPERTIES_PATH_HALF_REFLECTIONS_HALF_ABSORTANCE, 10000
    )
    expected_element_element_view_factors = (
        np.array(
            [
                [1 / 3, 2 / 3, 0, 0],
                [2 / 3, 1 / 3, 0, 0],
                [0.5, 0.5, 0, 0],
                [0.5, 0.5, 0, 0],
            ]
        ),
    )
    view_factors_errors = (
        element_element_view_factors - expected_element_element_view_factors
    )
    assert np.sum(view_factors_errors * view_factors_errors) < 0.02 * 16


def _element_element_backwards_diamond(properties_path, ray_amount):
    mesh = vtk_io.load_vtk(BACKWARDS_DIAMOND_GEOMETRY_PATH)
    properties = properties_atlas.PropertiesAtlas(
        utils.element_amount(mesh.triangles), properties_path
    )
    return view_factors.element_element(
        mesh, properties.absortance_by_element, ray_amount, 50, True
    )


def test_element_element_backwards_diamond_view_factors_sum_one_half():
    element_element_view_factors = _element_element_backwards_diamond(
        BACKWARDS_DIAMOND_PROPERTIES_PATH, 10000
    )
    for element_id, row in enumerate(element_element_view_factors):
        row_sum = np.sum(row)
        if element_id == BACKWARDS_DIAMOND_INTERNAL_ELEMENT_ID:
            assert _is_in_interval(row_sum, 1, 0.03)
        else:
            assert _is_in_interval(row_sum, 0.5, 0.03)


def test_element_element_backwards_diamond_view_factors_are_correct():
    element_element_view_factors = _element_element_backwards_diamond(
        BACKWARDS_DIAMOND_PROPERTIES_PATH, 10000
    )
    expected_element_element_view_factors = (
        np.array(
            [
                [0, 1 / 6, 1 / 6, 1 / 6, 0, 0, 0],
                [1 / 6, 0, 1 / 6, 1 / 6, 1 / 6, 1 / 6, 1 / 6],
                [1 / 6, 1 / 6, 0, 1 / 6, 0, 0, 0],
                [1 / 6, 1 / 6, 1 / 6, 0, 0, 0, 0],
                [0, 1 / 6, 0, 0, 0, 1 / 6, 1 / 6],
                [0, 1 / 6, 0, 0, 1 / 6, 0, 1 / 6],
                [0, 1 / 6, 0, 0, 1 / 6, 1 / 6, 0],
            ]
        ),
    )
    view_factors_errors = (
        element_element_view_factors - expected_element_element_view_factors
    )
    assert np.sum(view_factors_errors * view_factors_errors) < 0.02 * 16


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
        view_factors.mesh_look_at(mesh, direction)
        assert np.allclose(mesh.vertices, np.array(expected_vertices[i]).reshape(4, 3))
