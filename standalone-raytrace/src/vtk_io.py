import meshio
import trimesh

def load_vtk(file_path):
	meshio_mesh = meshio.read(file_path, file_format="vtk")
	dict_mesh = {'vertices': meshio_mesh.points, 'faces': meshio_mesh.get_cells_type("triangle")}
	return trimesh.load_mesh(dict_mesh)