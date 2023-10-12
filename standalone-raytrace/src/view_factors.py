import numpy as np
import trimesh
from . import utils, visualization

def node_sun(mesh, sun_direction, displacement=0.05, visualize=False):
	sun_direction = np.array(sun_direction)
	ray_origins = mesh.vertices - sun_direction*displacement
	ray_directions = np.broadcast_to(-sun_direction, (len(ray_origins), 3))
	intersected = mesh.ray.intersects_any(ray_origins, ray_directions)
	
	visualization.view_invisible_nodes(mesh, sun_direction, intersected)
	
	return [1 if x else 0 for x in intersected]

def surface_surface(mesh, ray_amount=1000, max_reflections_amount=3, displacement=0.1):
	center = np.array([0.5,0.5,0.5])
	surface_normals = trimesh.triangles.normals(mesh.triangles)[0]
	view_factors = np.zeros((len(mesh.triangles), len(mesh.triangles)))

	for surface_idx in range(len(mesh.triangles)):
		triangle = mesh.triangles[surface_idx]
		surface_normal = surface_normals[surface_idx]
		ray_origins = np.zeros((ray_amount, 3))
		ray_directions = np.zeros((ray_amount, 3))

		random_verts = np.random.rand(2*ray_amount,3)

		#Original emission
		for i in range(ray_amount):
			weights = utils.proportionalize(random_verts[2*i])
			ray_origins[i] = weights[0]*triangle[0] + weights[1]*triangle[1] + weights[2]*triangle[2] + displacement*surface_normal

			# Flip random rays that have a direction contrary to the surface normal
			random_direction = utils.normalize(random_verts[2*i + 1] - center)
			oriented_towards_normal = np.dot(random_direction, surface_normals[surface_idx]) >= 0
			ray_directions[i] = random_direction if oriented_towards_normal else -random_direction

		visualization.view_raycast(mesh, surface_idx, ray_origins, ray_directions)

		locations, index_ray, index_tri = mesh.ray.intersects_location(ray_origins, ray_directions)
		view_factors_row = np.zeros(len(mesh.triangles))
		for index in index_tri:
			view_factors_row[index] += 1

		#Reflexions
		for j in range(max_reflections_amount):
			if len(locations) == 0:
				break
			ray_origins = locations
			last_ray_directions = ray_directions
			
			#reflected_ray_direction = ray_direction - 2*(ray_direction*normal)*normal
			normal_dir_dot = np.zeros((len(locations),3))
			for i in range(len(locations)):
				normal_dir_dot[i] = np.dot(surface_normals[index_tri[i]], ray_directions[index_ray[i]])
			ray_directions = last_ray_directions[index_ray] - 2*normal_dir_dot*surface_normals[index_tri]

			visualization.view_raycast(mesh, surface_idx, ray_origins, ray_directions)

			#TODO: ¿Increment ray_amount? ¿What if a reflected ray hits the original surface or another surface two times? 
			locations, index_ray, index_tri = mesh.ray.intersects_location(ray_origins, ray_directions)
			for index in index_tri:
				view_factors_row[index] += 1

		view_factors_row /= ray_amount
		view_factors[surface_idx] = (view_factors_row)
	return view_factors