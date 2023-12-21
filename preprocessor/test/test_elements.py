from test_config import *
from src import elements
import numpy as np

element0 = np.array([[1, 1, 1], [1, 2, 1], [2, 1, 1]])
element1 = np.array([[1, 2, 1], [2, 1, 1], [2, 2, 1]])
test_element_array = np.array([element0, element1])


def test_point_in_element_inside():
    assert elements.is_point_in_element(element0, np.array([1.2, 1.2, 1])) == True


def test_point_in_element_edge():
    assert elements.is_point_in_element(element0, np.array([1, 1, 1])) == True


def test_point_in_element_outside():
    assert elements.is_point_in_element(element0, np.array([0, 1, 0])) == False


def test_generate_random_points_in_elements():
    points = elements.random_points_in_element(element0, 10000)
    for point in points:
        assert elements.is_point_in_element(element0, point) == True
