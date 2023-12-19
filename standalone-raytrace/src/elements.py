import numpy as np

def _triangle_area(edge1, edge2):
    return np.linalg.norm(np.cross(edge1, edge2)) / 2


def is_point_in_element(element, point):
    """
    Receives an element and a point in space.
    Returns true if the point is in the element or false otherwise.
    """
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

def random_points_in_element(element, amount):
    """
    Receives an element and an amount.
    Returns an array of size "amount" of points inside the received element. 
    """
    random_weights = np.random.rand(amount, 3)
    random_weights /= np.sum(random_weights, axis=1).reshape(-1, 1)
    return (random_weights[:, np.newaxis] @ element).reshape((amount, 3))
