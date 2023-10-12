import numpy as np

def normalize(v):
	norm = np.sqrt(v.dot(v))
	return v/norm

def proportionalize(v):
	p = sum(v)
	return v/p
