import numpy as np
import trimesh
from collections import Counter
from src import vtk_io

def solar_view_factor(mesh):
	solar_direction = np.array([0, 1, 1])
	ray_origins = mesh.vertices - solar_direction*0.05
	ray_directions = np.broadcast_to(-solar_direction, (len(ray_origins), 3))

	# raycast
	intersected = mesh.ray.intersects_any(ray_origins, ray_directions)
	not_visible_vertices = np.arange(len(mesh.vertices))[intersected]

	# visualization
	sun_ray = trimesh.load_path([[0,0,0], -10*solar_direction])
	sun_ray.colors = [[255,233,92,255]]
	point_cloud = trimesh.PointCloud(mesh.vertices[not_visible_vertices])
	mesh.unmerge_vertices()
	scene = trimesh.Scene([mesh, point_cloud, sun_ray]) #ray_visualize])
	scene.show()

def normalize(v):
	norm = np.sqrt(v.dot(v))
	return v/norm

def proportionalize(v):
	p = sum(v)
	return v/p

def surface_view_factor(mesh):
	num_rays = 100
	num_reflections = 1

	center = np.array([0.5,0.5,0.5])
	surface_normals = trimesh.triangles.normals(mesh.triangles)[0]
	view_factors = np.zeros((len(mesh.triangles), len(mesh.triangles)))

	for surface_idx in range(len(mesh.triangles)):
		triangle = mesh.triangles[surface_idx]
		surface_normal = surface_normals[surface_idx]

		random_verts = np.random.rand(2*num_rays,3)
		ray_origins = np.zeros((num_rays, 3))
		ray_directions = np.zeros((num_rays, 3))

		for i in range(num_rays):
			weights = proportionalize(random_verts[2*i])
			ray_origins[i] = weights[0]*triangle[0] + weights[1]*triangle[1] + weights[2]*triangle[2] + 0.1*surface_normal

			direction = normalize(random_verts[2*i + 1] - center)
			oriented_towards_normal = np.dot(direction, surface_normals[surface_idx]) >= 0
			ray_directions[i] = direction if oriented_towards_normal else -direction

		# Visualization
		# mesh.visual.face_colors = [255,255,255,255]
		# mesh.visual.face_colors[surface_idx] = [255, 0, 0, 255]
		# ray_visualize = trimesh.load_path(np.hstack((ray_origins,ray_origins + ray_directions)).reshape(-1, 2, 3))
		# mesh.unmerge_vertices()
		# scene = trimesh.Scene([mesh, ray_visualize])
		# scene.show()

		locations, index_ray, index_tri = mesh.ray.intersects_location(ray_origins, ray_directions)
		

		view_factors_row = np.zeros(len(mesh.triangles))
		for index in index_tri:
			view_factors_row[index] += 1

		for j in range(num_reflections):
			if len(locations) == 0:
				break
			ray_origins = locations
			last_ray_directions = ray_directions
			
			#reflected_direction = direction - 2*(direction*normal)*normal
			normal_dir_dot = np.zeros((len(locations),3))
			for i in range(len(locations)):
				normal_dir_dot[i] = np.dot(surface_normals[index_tri[i]], ray_directions[index_ray[i]])
			ray_directions = last_ray_directions[index_ray] - 2*normal_dir_dot*surface_normals[index_tri]

			locations, index_ray, index_tri = mesh.ray.intersects_location(ray_origins, ray_directions)
			for index in index_tri:
				view_factors_row[index] += 1
			
			#Warning ¿What if a reflected ray hits the original surface or another surface two times? 
			#num_rays += len(locations)

			#ray_visualize = trimesh.load_path(np.hstack((ray_origins,ray_origins + ray_directions)).reshape(-1, 2, 3))


		# mesh.unmerge_vertices()
		# scene = trimesh.Scene([mesh, ray_visualize])
		# scene.show()
		view_factors_row /= num_rays
		view_factors[surface_idx] = (view_factors_row)
	return view_factors;

def trimesh_main():
	
	# test on a sphere primitive
	mesh = vtk_io.load_vtk("./models/cube.vtk")
	#mesh = trimesh.load_mesh("./models/cube.vtk", force='mesh')
	mesh.visual.face_colors = [255,255,255,255]
	mesh.visual.face_colors[0] = [255, 0, 0, 255]
	mesh.unmerge_vertices()
	scene = trimesh.Scene([mesh])
	scene.show()
	#solar_view_factor(mesh)
	#print(surface_view_factor(mesh))



if __name__ == '__main__':
	trimesh_main()
