from test_config import *
from src import rays
import numpy as np


def test_aparent_element_area_multiplier():
    ray_directions = np.array([[0, 0, -1], [0, 0, -1], [0, -1, 0], [2, -3, 4]])
    element_normals = np.array([[0, 0, 1], [0, 0, 1], [1, 1, 0], [-6, 8, 5]])
    aparent_area_multipliers = rays.aparent_element_area_multiplier(
        ray_directions, element_normals
    )
    expected_aparent_area_multipliers = [1, 1, np.cos(np.pi / 4), np.cos(1.301819131)]
    assert np.allclose(aparent_area_multipliers, expected_aparent_area_multipliers)

def test_reflected_rays_towards_element_normals():
    ray_directions = np.array([[0, 0, -1], [0, 1, -1], [0, 0, -1]])
    element_normals = np.array([[0, 0, 1], [0, 0, 1], [0, 1/np.sqrt(2), 1/np.sqrt(2)]])
    reflected_rays = rays.reflected_rays(ray_directions, element_normals)
    expected_reflected_rays = np.array([[0, 0, 1], [0, 1, 1], [0, 1, 0]])
    assert np.allclose(reflected_rays, expected_reflected_rays)


def test_reflected_rays_against_element_normals():
    ray_directions = np.array([[0, 0, 1], [0, 1, 1], [0, 0, 1]])
    element_normals = np.array([[0, 0, 1], [0, 0, 1], [0, 1/np.sqrt(2), 1/np.sqrt(2)]])
    reflected_rays = rays.reflected_rays(ray_directions, element_normals)
    expected_reflected_rays = np.array([[0, 0, -1], [0, 1, -1], [0, -1, -0]])
    assert np.allclose(reflected_rays, expected_reflected_rays)
