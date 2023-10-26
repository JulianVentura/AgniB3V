from .test_config import *
from src import vtk_io, utils, properties_atlas, view_factors
import numpy as np

def test_element_earth():
    earth_direction = np.array([1,0,0])
    mesh = vtk_io.load_vtk(ICOSPHERE_GEOMETRY_PATH)
    earth_view_factors = view_factors.element_earth(mesh, earth_direction ,10000)
    #TODO: Fix 11,13,18,16 are almost ortogonal
    expected_visible_elements = np.array([0,1,4,5,6,9,10,14,15,19,11,13,18,16])
    expected_view_factors = np.zeros(20)
    expected_view_factors[expected_visible_elements] = 1
    assert np.array_equal(earth_view_factors, expected_view_factors)

def test_element_sun():
    mesh = vtk_io.load_vtk(ICOSPHERE_GEOMETRY_PATH)
    sun_direction = np.array([1,0,0])
    sun_view_factors = view_factors.element_sun(mesh, sun_direction)
    expected_visible_elements = np.array([0,1,4,5,6,9,10,14,15,19])
    expected_view_factors = np.zeros(20)
    expected_view_factors[expected_visible_elements] = 1
    assert np.array_equal(sun_view_factors, expected_view_factors)

def _element_element_backwards_pyramid(properties_path, ray_amount):
    mesh = vtk_io.load_vtk(BACKWARDS_PYRAMID_GEOMETRY_PATH)
    properties = properties_atlas.PropertiesAtlas(utils.element_amount(mesh.triangles), properties_path)
    return view_factors.element_element(mesh, properties, ray_amount, 50, 0.01, False)

def test_element_element_backwards_pyramid_view_factors_rows_sum_one():
    element_element_view_factors = _element_element_backwards_pyramid(BACKWARDS_PYRAMID_PROPERTIES_PATH_NO_REFLECTIONS, 10000)
    print(element_element_view_factors)
    for element_id in range(len(element_element_view_factors)):
        row = np.delete(element_element_view_factors[element_id], element_id)
        row_sum = np.sum(row)
        assert row_sum < 1.01 and row_sum > 0.98

def test_element_element_backwards_pyramid_view_factors_rows_are_similar():
    element_element_view_factors_epsilon = 0.02
    element_element_view_factors = _element_element_backwards_pyramid(BACKWARDS_PYRAMID_PROPERTIES_PATH_NO_REFLECTIONS, 10000)
    for element_id in range(len(element_element_view_factors)):
        row = np.delete(element_element_view_factors[element_id], element_id)
        assert np.all(row < 1/3 + element_element_view_factors_epsilon)
        assert np.all(row > 1/3 - element_element_view_factors_epsilon)

def test_view_factors_full_reflections():
    element_element_view_factors = _element_element_backwards_pyramid(BACKWARDS_PYRAMID_PROPERTIES_PATH_FULL_REFLECTIONS, 10000)
    view_factors_sum = np.sum(element_element_view_factors)
    assert view_factors_sum > 0 - sys.float_info.epsilon*10 and view_factors_sum < 0 + sys.float_info.epsilon*10 

def test_element_element_backwards_pyramid_view_factors_half_reflections_sum_one():
    element_element_view_factors = _element_element_backwards_pyramid(BACKWARDS_PYRAMID_PROPERTIES_PATH_HALF_REFLECTIONS, 10000)
    for row in element_element_view_factors:
        row_sum = np.sum(row)
        assert row_sum < 1.01 and row_sum > 0.98

def test_element_element_backwards_pyramid_view_factors_half_reflections_are_correct():
    element_element_view_factors = _element_element_backwards_pyramid(BACKWARDS_PYRAMID_PROPERTIES_PATH_HALF_REFLECTIONS, 10000)
    expected_element_element_view_factors = np.array([[1/3,2/3,0,0],[2/3,1/3,0,0],[0.5,0.5,0,0],[0.5,0.5,0,0]]),
    view_factors_errors = element_element_view_factors - expected_element_element_view_factors
    print(element_element_view_factors)
    assert np.sum(view_factors_errors * view_factors_errors) < 0.02*16

def test_element_element_backwards_pyramid_view_factors_half_reflections_half_absortance_sum_one():
    element_element_view_factors = _element_element_backwards_pyramid(BACKWARDS_PYRAMID_PROPERTIES_PATH_HALF_REFLECTIONS_HALF_ABSORTANCE, 10000)
    print(element_element_view_factors)
    for row in element_element_view_factors:
        row_sum = np.sum(row)
        assert row_sum < 1.01 and row_sum > 0.98

def test_element_element_backwards_pyramid_view_factors_half_reflections_half_absortance_are_correct():
    element_element_view_factors = _element_element_backwards_pyramid(BACKWARDS_PYRAMID_PROPERTIES_PATH_HALF_REFLECTIONS_HALF_ABSORTANCE, 10000)
    expected_element_element_view_factors = np.array([[1/3,2/3,0,0],[2/3,1/3,0,0],[0.5,0.5,0,0],[0.5,0.5,0,0]]),
    view_factors_errors = element_element_view_factors - expected_element_element_view_factors
    assert np.sum(view_factors_errors * view_factors_errors) < 0.02*16