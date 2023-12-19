from test_config import *
from src import vector_math
import numpy as np
import scipy as sp


def test_normalize():
    test_array = np.array([4, 4, 2])
    normalized_array = vector_math.normalize(test_array)
    assert np.array_equal(normalized_array, np.array([4 / 6, 4 / 6, 2 / 6]))
    assert np.linalg.norm(normalized_array) == 1


def test_proportionalize():
    test_array = np.array([2, 2, 6])
    proportionalized_array = vector_math.proportionalize(test_array)
    assert np.array_equal(proportionalized_array, np.array([0.2, 0.2, 0.6]))


def test_random_unit_vectors_norm():
    unit_vectors = vector_math.random_unit_vectors(10)
    unit_vectors_norm = np.linalg.norm(unit_vectors, axis=1)
    assert np.all(unit_vectors_norm > 1 - sys.float_info.epsilon * 10)
    assert np.all(unit_vectors_norm < 1 + sys.float_info.epsilon * 10)


# Based on:
# Distributions of Angles in Random Packing on Spheres
# By Tony Cai, Jianqing Fan, and Tiefeng Jiang
# Angles between vectors of n dimensions uniformly
# distributed in a unit sphere are distributed according to:
# f(x) = 1/sqrt(pi)*gamma(n/2)/gamma((n-1)/2)*(sin(x))^(n-2)
# Where n is the dimension of the space. For n = 3:
# f(x) = 1/2*sin(x)
# Using the inverse transform method samples from this
# distribution are computed and compared with the observed
# ones using Kolmogorov-Smirnov test, with null hipotesis:
# H0 : "Angles between vectors follow f(x) distribution"
def test_random_unit_vectors_distribution():
    sample_size = 10000
    bins = 100
    alpha = 0.05

    # Oberserved samples
    unit_vectors = vector_math.random_unit_vectors(sample_size)
    observed_thetas = unit_vectors @ unit_vectors.T
    observed_thetas = observed_thetas[np.triu_indices_from(observed_thetas, 1)]
    observed_thetas = np.array(observed_thetas)
    observed_thetas = np.arccos(observed_thetas)

    # Expected samples
    expected_thetas = np.random.rand(observed_thetas.size)
    expected_thetas = np.arccos(1 - 2 * expected_thetas)

    # Frequencies
    observed_frec, _ = np.histogram(observed_thetas, bins=bins)
    expected_frec, _ = np.histogram(expected_thetas, bins=bins)

    # Kolmogorov-Smirnov Test
    _, p_value = sp.stats.kstest(rvs=observed_frec, cdf=expected_frec)
    assert p_value > alpha


def test_orient_towards_direction():
    normal = np.array([1, 1, 0])
    vectors = np.array([[1, 2, 0], [1, 0, 0], [-1, -1, 0], [-1, -2, 0]])
    vector_math.orient_towards_direction(vectors, normal)
    expected_oriented_vectors = np.array([[1, 2, 0], [1, 0, 0], [1, 1, 0], [1, 2, 0]])
    assert np.array_equal(vectors, expected_oriented_vectors)


def test_spherical_coordinates():
    cartesian_coords_vectors = np.array(
        [[1, 1, 0], [3, 3, 0], [-1, 1, 0], [1, 0, 1], [2.5, 2.5, 3.5355339]]
    )
    expected_spherical_coords_vectors = [
        [3 * np.pi / 4, np.pi / 2],
        [3 * np.pi / 4, np.pi / 2],
        [5 * np.pi / 4, np.pi / 2],
        [np.pi / 2, np.pi / 4],
        [3 * np.pi / 4, np.pi / 4],
    ]
    for i in range(len(cartesian_coords_vectors)):
        spherical_coords_vectors = vector_math.spherical_cordinates(
            cartesian_coords_vectors[i]
        )
        assert np.array_equal(
            np.round(expected_spherical_coords_vectors[i], 5),
            np.round(spherical_coords_vectors[1:], 5),
        )


def test_flip_around_axis():
    vectors = [
        np.array([[0, 1, 0], [0, 0, 1]]),
        np.array([[1, 0, 0], [0, 0, 1]]),
        np.array([[1, 0, 0], [0, 1, 0]]),
        np.array([[1, 0, 0], [0, 0, 1]]),
        np.array([[2, 3, 4], [5, 3, 4]]),
    ]
    axis = [
        np.array([1, 0, 0]),
        np.array([0, 1, 0]),
        np.array([0, 0, 1]),
        np.array([1, 1, 0]),
        np.array([2, 3, 4]),
    ]

    expected_vectors = [
        np.array([[0, -1, 0], [0, 0, -1]]),
        np.array([[-1, 0, 0], [0, 0, -1]]),
        np.array([[-1, 0, 0], [0, -1, 0]]),
        np.array([[0, 1, 0], [0, 0, -1]]),
        np.array([[2, 3, 4], [-0.17241379, 4.24137931, 5.65517241]]),
    ]
    for i in range(len(vectors)):
        flipped_vectors = vector_math.flip_around_axis(vectors[i], axis[i])
        assert np.allclose(flipped_vectors, expected_vectors[i])
