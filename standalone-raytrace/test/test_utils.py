from .test_config import *
from src import utils
import numpy as np

element0 = np.array([[1, 1, 1], [1, 2, 1], [2, 1, 1]])
element1 = np.array([[1, 2, 1], [2, 1, 1], [2, 2, 1]])
test_element_array = np.array([element0, element1])


def test_normalize():
    test_array = np.array([4, 4, 2])
    normalized_array = utils.normalize(test_array)
    assert np.array_equal(normalized_array, np.array([4 / 6, 4 / 6, 2 / 6]))
    assert np.linalg.norm(normalized_array) == 1


def test_proportionalize():
    test_array = np.array([2, 2, 6])
    proportionalized_array = utils.proportionalize(test_array)
    assert np.array_equal(proportionalized_array, np.array([0.2, 0.2, 0.6]))


def test_elements_amount():
    assert utils.element_amount(test_element_array) == 2


def test_point_in_element_inside():
    assert utils.is_point_in_element(element0, np.array([1.2, 1.2, 1])) == True


def test_point_in_element_edge():
    assert utils.is_point_in_element(element0, np.array([1, 1, 1])) == True


def test_point_in_element_outside():
    assert utils.is_point_in_element(element0, np.array([0, 1, 0])) == False


def test_generate_random_points_in_elements():
    points = utils.generate_random_points_in_element(element0, 10000)
    for point in points:
        assert utils.is_point_in_element(element0, point) == True


def test_generate_random_unit_vectors():
    unit_vectors = utils.generate_random_unit_vectors(10)
    unit_vectors_norm = np.linalg.norm(unit_vectors)
    assert np.all(unit_vectors_norm > 1 - sys.float_info.epsilon * 10)
    assert np.all(unit_vectors_norm < 1 + sys.float_info.epsilon * 10)


def test_reflected_rays_towards_element_normals():
    ray_directions = np.array([[0, 0, -1], [0, 1, -1], [0, 0, -1]])
    element_normals = np.array([[0, 0, 1], [0, 0, 1], [0, 1, 1]])
    reflected_rays = utils.reflected_rays(ray_directions, element_normals)
    expected_reflected_rays = np.array([[0, 0, 1], [0, 1, 1], [0, 2, 1]])
    assert np.array_equal(reflected_rays, expected_reflected_rays)


def test_reflected_rays_against_element_normals():
    ray_directions = np.array([[0, 0, 1], [0, 1, 1], [0, 0, 1]])
    element_normals = np.array([[0, 0, 1], [0, 0, 1], [0, 1, 1]])
    reflected_rays = utils.reflected_rays(ray_directions, element_normals)
    expected_reflected_rays = np.array([[0, 0, -1], [0, 1, -1], [0, -2, -1]])
    assert np.array_equal(reflected_rays, expected_reflected_rays)


def test_aparent_element_area_multiplier():
    ray_directions = np.array([[0, 0, -1], [0, 0, -1], [0, -1, 0], [2, -3, 4]])
    element_normals = np.array([[0, 0, 1], [0, 0, 1], [1, 1, 0], [-6, 8, 5]])
    aparent_area_multipliers = utils.aparent_element_area_multiplier(
        ray_directions, element_normals
    )
    expected_aparent_area_multipliers = [1, 1, np.sin(np.pi / 4), np.sin(0.2657455355)]
    assert np.array_equal(
        np.floor(aparent_area_multipliers), np.floor(expected_aparent_area_multipliers)
    )


def test_orient_vector_towards_normal():
    normal = np.array([1, 1, 0])
    vectors = np.array([[1, 2, 0], [1, 0, 0], [-1, -1, 0], [-1, -2, 0]])
    utils.orient_vector_towards_normal(vectors, normal)
    expected_oriented_vectors = np.array([[1, 2, 0], [1, 0, 0], [1, 1, 0], [1, 2, 0]])
    assert np.array_equal(vectors, expected_oriented_vectors)
