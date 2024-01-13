import timeit
import numpy as np
import trimesh
import open3d as o3d
import sys
import matplotlib.pyplot as plt
import templates

RAY_AMOUNT = 5000
RAY_DISPLACEMENT = 1e-4

def random_points_in_element(element, amount):
    random_weights = np.random.rand(amount, 3)
    random_weights /= np.sum(random_weights, axis=1).reshape(-1, 1)
    return (random_weights[:, np.newaxis] @ element).reshape((amount, 3))

def random_unit_vectors(amount):
    random_vectors = np.random.normal(0, 1, (amount, 3))
    return random_vectors / np.linalg.norm(random_vectors, axis=1)[:, np.newaxis]



def trimesh_benchmark(file_path):
	mesh = None
	with open(file_path) as file_mesh:
		mesh = trimesh.load(file_mesh, "stl")
	element_normals = trimesh.triangles.normals(mesh.triangles)[0]
	element_amount = mesh.triangles.size // 9
	for element_id in range(element_amount):
		emitting_element = mesh.triangles[element_id]
		emitting_element_normal = element_normals[element_id]
		view_factors_row = np.zeros(element_amount)

		ray_origins = random_points_in_element(emitting_element, RAY_AMOUNT)
		ray_directions = random_unit_vectors(RAY_AMOUNT)
		ray_origins += ray_directions * RAY_DISPLACEMENT
		mesh.ray.intersects_id(
		    ray_origins, ray_directions, return_locations=True, multiple_hits=False
		)

def open3d_benchmark(file_path):
	mesh = o3d.io.read_triangle_mesh(file_path)
	elements_amount = len(mesh.triangles)
	mesh.compute_triangle_normals()
	element_normals = np.asarray(mesh.triangle_normals)
	mesh_elements = np.asarray(mesh.triangles)
	vertices = np.asarray(mesh.vertices)
	for element_id in range(elements_amount):
		emitting_element = vertices[mesh_elements[element_id]]      
		emitting_element_normal = element_normals[element_id]

		ray_origins = random_points_in_element(emitting_element, RAY_AMOUNT)
		ray_directions = random_unit_vectors(RAY_AMOUNT)
		ray_origins += ray_directions * RAY_DISPLACEMENT
		rays = o3d.core.Tensor(np.concatenate((ray_origins, ray_directions), axis=1),
		               dtype=o3d.core.Dtype.Float32)
		scene = o3d.t.geometry.RaycastingScene()
		scene.add_triangles(o3d.t.geometry.TriangleMesh.from_legacy(mesh))
		scene.cast_rays(rays)

def main():
	trimesh_time = []
	open3d_time = []
	
	if len(sys.argv) < 3:
		print(f"Use: {sys.argv[0]} <folder> <mesh1> <mesh2> ...")
		print("Meshes must not include .stl extension")

	_, folder, *meshes = sys.argv
	if folder[-1] != "/":
		folder += "/"
	element_amount = list(map(lambda x: int(x), meshes))
	element_amount.sort()
	meshes = list(map(lambda x : folder + str(x) + ".stl", element_amount))

	for mesh in meshes:
		print(mesh)
		trimesh_time.append(timeit.timeit(lambda : trimesh_benchmark(mesh), number=1))
		open3d_time.append(timeit.timeit(lambda : open3d_benchmark(mesh), number=1))

	templates.template_style()
	fig, ax = plt.subplots()
	ax.plot(element_amount, open3d_time, label="Open3d", marker="s")
	ax.plot(element_amount, trimesh_time, label="Trimesh", marker="s")
	templates.template_plot(ax, "Number of Elements", "Execution Time (s)", "Open3d vs Trimesh")
	templates.template_save_multiple_images([fig], "open3d_vs_trimesh", ["open3d_vs_trimesh"])
		
main()
