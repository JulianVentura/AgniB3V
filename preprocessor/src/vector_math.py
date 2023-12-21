import numpy as np


def normalize(vector):
    """
    Receives a vector and returns another vector with the same
    direction and lenght one.
    """
    norm = np.sqrt(vector.dot(vector))
    return vector / norm


def proportionalize(vector):
    """
    Receives a vector and returns another vector where each
    component is proportional to the original vector one
    and the sum of all components is one.
    """
    p = sum(vector)
    return vector / p


def spherical_cordinates(vector):
    """
    Returns vector spherical coordinates according to the
    following convention:
         z
         |.
         |  θ : theta e [0, 2*PI]
         |_ _._ y
        /  .
       /. φ : phi e [0, PI)
      x
    """
    norm = np.linalg.norm(vector)
    theta = np.arccos(vector[2] / norm)
    phi = 0
    if vector[0] != 0 or vector[1] != 0:
        phi = (
            np.sign(vector[1])
            * np.arccos(vector[0] / np.sqrt(vector[0] ** 2 + vector[1] ** 2))
            + np.pi / 2
        )
    return norm, phi, theta


def random_unit_vectors(amount):
    """
    Generates an array of unit vectors with pseudorandom directions.
    """
    random_vectors = np.random.normal(0, 1, (amount, 3))
    return random_vectors / np.linalg.norm(random_vectors, axis=1)[:, np.newaxis]


def array_dot(vectors, other_vector):
    """
    Receives an array of vectors and returns an array of inner product
    between them and other vector.
    """
    return vectors @ (other_vector)[:, np.newaxis]


def array_array_dot(vectors, other_vectors):
    """
    Receives two array of vectors and returns an array of the inner products
    between each pair of elements.
    """
    return np.einsum("...j,...j", vectors, other_vectors)


def array_array_cos(vectors, other_vectors):
    """
    Receives two array of vectors and returns an array of the cosine
    of the angle between each pair of elements.
    """
    dot_products = array_array_dot(vectors, other_vectors)
    norm_products = np.linalg.norm(vectors, axis=1) * np.linalg.norm(
        other_vectors, axis=1
    )
    return dot_products / norm_products


# TODO: If vector is ortogonal to direction it will be multiplied by zero
def orient_towards_direction(vectors, direction):
    """
    Receives a vector and flips it inplace if the inner product with
    the direction is negative.
    """
    vectors *= np.sign(vectors @ direction[:, np.newaxis])


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
    return np.array(
        [
            [aa + bb - cc - dd, 2 * (bc + ad), 2 * (bd - ac)],
            [2 * (bc - ad), aa + cc - bb - dd, 2 * (cd + ab)],
            [2 * (bd + ac), 2 * (cd - ab), aa + dd - bb - cc],
        ]
    )


def flip_around_axis(vectors, axis):
    """
    Returns vectors rotated by pi radians around the given axis.
    """
    rot_matrix = _rotation_matrix(axis, np.pi)
    return np.dot(rot_matrix, vectors.T).T
