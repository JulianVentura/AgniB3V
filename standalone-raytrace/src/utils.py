import numpy as np
import os




def normalize(v):
    norm = np.sqrt(v.dot(v))
    return v / norm


def proportionalize(v):
    p = sum(v)
    return v / p
    
def element_amount(elements):
    return elements.size // 9


def _triangle_area(edge1, edge2):
    return np.linalg.norm(np.cross(edge1, edge2)) / 2


def is_point_in_element(element, point):
    element_area = _triangle_area(element[2] - element[0], element[1] - element[0])
    sub_area1 = _triangle_area(point - element[1], point - element[0])
    sub_area2 = _triangle_area(point - element[2], point - element[0])
    alpha = sub_area1 / element_area
    beta = sub_area2 / element_area
    gamma = 1 - alpha - beta
    return (
        alpha >= 0
        and alpha <= 1
        and beta >= 0
        and beta <= 1
        and gamma >= 0
        and gamma <= 1
    )


def array_dot(vector_array, vector):
    return vector_array @ (vector)[:,np.newaxis]

def generate_random_points_in_element(element, amount):
    random_weights = np.random.rand(amount, 3)
    random_weights /= np.sum(random_weights, axis=1).reshape(-1, 1)
    return (random_weights[:, np.newaxis] @ element).reshape((amount, 3))


def generate_random_unit_vectors(amount):
    random_vectors = np.random.normal(0, 1, (amount, 3))
    return random_vectors / np.linalg.norm(random_vectors, axis=1)[:, np.newaxis]


# TODO: If vector is ortogonal to normal it will be multiplied by zero
def orient_vector_towards_normal(vectors, normal):
    vectors *= np.sign(vectors @ normal[:, np.newaxis])


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


# 	 z
#    |.
#    |  θ : theta e [0, 2*PI]
# 	 |_ _._ y
# 	/  .
#  /. φ : phi e [0, PI)
# x
def vector_spherical_cordinates(vector):
    norm = np.linalg.norm(vector)
    theta = np.arccos(vector[2] / norm)
    phi = 0
    if(vector[0] != 0 or vector[1] != 0):
        phi = np.sign(vector[1]) * np.arccos(
            vector[0] / np.sqrt(vector[0] ** 2 + vector[1] ** 2)
        ) + np.pi/2
    return norm, phi, theta

def _rotation_matrix(axis, theta):
    """
    Return the rotation matrix associated with counterclockwise rotation about
    the given axis by theta radians using euler-rodriguez formula.
    """
    axis = np.asarray(axis)
    axis = axis / np.sqrt(np.dot(axis, axis))
    a = np.cos(theta / 2.0)
    b, c, d = -axis * np.sin(theta / 2.0)
    aa, bb, cc, dd = a * a, b * b, c * c, d * d
    bc, ad, ac, ab, bd, cd = b * c, a * d, a * c, a * b, b * d, c * d
    return np.array([[aa + bb - cc - dd, 2 * (bc + ad), 2 * (bd - ac)],
                     [2 * (bc - ad), aa + cc - bb - dd, 2 * (cd + ab)],
                     [2 * (bd + ac), 2 * (cd - ab), aa + dd - bb - cc]])

def flip_vectors_around_axis(axis, vectors):
	"""
    Returns vectors rotated by pi radians around the given axis. 
    """
	rot_matrix = _rotation_matrix(axis, np.pi)
	return np.dot(rot_matrix, vectors.T).T

def get_file_with_name(filename: str, directory: str) -> str or None:
    """
    Given a filename and a directory, it looks for a file that matches the name 
    in the given directory and returns its path.
    """
    files = [f for f in os.listdir(directory)]
    for file in files:
        if filename in file:
            return file
    return None
