import trimesh

def load_vtk(file_path):
	"""
	Recieves a vtk file path and returns a trimesh object.
	"""	
	with open(file_path) as file_mesh:
		return trimesh.load(file_mesh, "vtk")