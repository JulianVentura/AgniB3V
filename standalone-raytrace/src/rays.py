import numpy as np

#TODO: Extract einsum in array_array_dot
def aparent_element_area_multiplier(ray_directions, element_normals):
    ray_direction_element_normal_dot_product = np.einsum(
        "ij,ij->i", element_normals, ray_directions
    )[:, np.newaxis]
    ray_direction_element_normal_dot_product = np.abs(
        ray_direction_element_normal_dot_product.flatten()
    )
    ray_direction_element_normal_angle = ray_direction_element_normal_dot_product / (
        np.linalg.norm(ray_directions, axis=1) * np.linalg.norm(element_normals, axis=1)
    )
    return ray_direction_element_normal_angle


def reflected_rays(ray_directions, element_normals):
    ray_direction_element_normal_dot_product = np.einsum(
        "ij,ij->i", element_normals, ray_directions
    )[:, np.newaxis]
    return (
        ray_directions - 2 * ray_direction_element_normal_dot_product * element_normals
    )