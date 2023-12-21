import numpy as np
from . import vector_math


def aparent_element_area_multiplier(ray_directions, element_normals):
    """
    Receives an array of ray directions and elment normals and for each pair
    (the first element with the first normal, the second element with the secondo normal
    and so on) it computes the proyection of the element area in the ray direction.
    """
    return np.abs(vector_math.array_array_cos(element_normals, ray_directions))


def reflected_rays(ray_directions, element_normals):
    """
    Receives an array of ray directions and elment normals and returns an
    array of the reflected rays according to the element normal with the same
    index.
    """
    ray_direction_element_normal_dot_product = vector_math.array_array_dot(
        element_normals, ray_directions
    )
    return (
        ray_directions
        - 2 * ray_direction_element_normal_dot_product[:, np.newaxis] * element_normals
    )
