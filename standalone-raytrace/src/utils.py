import numpy as np
import sys

RAND_VECTOR_CENTER = np.array([0.5,0.5,0.5])

def normalize(v):
	norm = np.sqrt(v.dot(v))
	return v/norm

def proportionalize(v):
	p = sum(v)
	return v/p

def element_amount(elements):
	return elements.size // 9

def _triangle_area(edge1, edge2):
	return np.linalg.norm(np.cross(edge1, edge2))/2
	
def is_point_in_element(element, point):
	element_area = _triangle_area(element[2] - element[0], element[1] - element[0])
	sub_area1 = _triangle_area(point - element[1], point - element[0])
	sub_area2 = _triangle_area(point - element[2], point - element[0])
	alpha = sub_area1/element_area
	beta = sub_area2/element_area
	gamma = 1 - alpha - beta
	return alpha >= 0 and alpha <= 1 and beta >= 0 and beta <= 1 and gamma >= 0 and gamma <= 1

def generate_random_points_in_element(element, amount):
	random_weights = np.random.rand(amount,3)
	random_weights /=np.sum(random_weights, axis=1).reshape(-1,1)
	return random_weights @ element

def generate_random_unit_vectors(amount):
	random_vectors = np.random.rand(amount,3) - RAND_VECTOR_CENTER
	return random_vectors / np.linalg.norm(random_vectors)

#TODO: If vector equals normal it will be multiplied by zero
def orient_vector_towards_normal(vectors, normal):
	vectors *= (np.sign(vectors @ normal[:,np.newaxis]))

def reflected_rays(ray_directions, element_normals):
	ray_direction_element_normal_dot_product = np.einsum('ij,ij->i',element_normals, ray_directions)[:,np.newaxis]
	return ray_directions - 2*ray_direction_element_normal_dot_product*element_normals
