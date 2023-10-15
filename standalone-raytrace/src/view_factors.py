import numpy as np
import trimesh
from . import utils, visualization

DEBUG_VISUALIZATION_ENABLED = False

def point_sun(mesh, sun_direction, displacement=0.05):
	sun_direction = np.array(sun_direction)
	ray_origins = mesh.vertices - sun_direction*displacement
	ray_directions = np.broadcast_to(-sun_direction, (len(ray_origins), 3))
	intersected = mesh.ray.intersects_any(ray_origins, ray_directions)
	
	if(DEBUG_VISUALIZATION_ENABLED):
		invisible_nodes = np.arange(len(mesh.vertices))[intersected]
		visualization.view_invisible_points(mesh, sun_direction, mesh.vertices[invisible_nodes])
	
	return [1 if x else 0 for x in intersected]

def element_earth(mesh, earth_direction, ray_amount, displacement=0.05):
	earth_direction = np.array(earth_direction)
	center = np.array([0.5,0.5,0.5])
	element_normals = trimesh.triangles.normals(mesh.triangles)[0]
	view_factors = np.zeros(len(mesh.triangles))

	for element_idx in range(len(mesh.triangles)):
		element_normal = element_normals[element_idx]

		triangle = mesh.triangles[element_idx]
		ray_origins = np.zeros((ray_amount, 3))
		ray_directions = np.zeros((ray_amount, 3))

		random_verts = np.random.rand(2*ray_amount,3)

		#Original emission
		for i in range(ray_amount):
			weights = utils.proportionalize(random_verts[2*i])
			ray_origins[i] = weights[0]*triangle[0] + weights[1]*triangle[1] + weights[2]*triangle[2] + displacement*element_normal

			# Flip random rays that have a direction contrary to Earth's direction
			random_direction = utils.normalize(random_verts[2*i + 1] - center)
			oriented_towards_normal = np.dot(random_direction, -earth_direction) >= 0
			ray_directions[i] = random_direction if oriented_towards_normal else -random_direction

		if(DEBUG_VISUALIZATION_ENABLED):
			visualization.view_raycast(mesh, element_idx, ray_origins, ray_directions)

		locations, index_ray, index_tri = mesh.ray.intersects_location(ray_origins, ray_directions)
		view_factors[element_idx] = 1 if (len(index_tri) < ray_amount) else 0
	
	return view_factors

def element_sun(mesh, sun_direction, displacement=0.05):
	sun_direction = np.array(sun_direction)
	element_centers = np.array(list(map(lambda x: (x[0] + x[1] + x[2])/3, mesh.triangles)))
	ray_origins =  element_centers - sun_direction*displacement
	ray_directions = np.broadcast_to(-sun_direction, (len(ray_origins), 3))
	intersected = mesh.ray.intersects_any(ray_origins, ray_directions)
	
	if(DEBUG_VISUALIZATION_ENABLED):
		invisible_nodes = np.arange(len(element_centers))[intersected]
		visualization.view_invisible_points(mesh, sun_direction, element_centers[invisible_nodes])
	
	return [1 if x else 0 for x in intersected]

def element_element(mesh, ray_amount=1000, max_reflections_amount=3, displacement=0.1):
	center = np.array([0.5,0.5,0.5])
	element_normals = trimesh.triangles.normals(mesh.triangles)[0]
	view_factors = np.zeros((len(mesh.triangles), len(mesh.triangles)))

	for element_idx in range(len(mesh.triangles)):
		triangle = mesh.triangles[element_idx]
		element_normal = element_normals[element_idx]
		ray_origins = np.zeros((ray_amount, 3))
		ray_directions = np.zeros((ray_amount, 3))

		random_verts = np.random.rand(2*ray_amount,3)

		#Original emission
		for i in range(ray_amount):
			weights = utils.proportionalize(random_verts[2*i])
			ray_origins[i] = weights[0]*triangle[0] + weights[1]*triangle[1] + weights[2]*triangle[2] + displacement*element_normal

			# Flip random rays that have a direction contrary to the element normal
			random_direction = utils.normalize(random_verts[2*i + 1] - center)
			oriented_towards_normal = np.dot(random_direction, element_normals[element_idx]) >= 0
			ray_directions[i] = random_direction if oriented_towards_normal else -random_direction

		if(DEBUG_VISUALIZATION_ENABLED):
			visualization.view_raycast(mesh, element_idx, ray_origins, ray_directions)

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
				normal_dir_dot[i] = np.dot(element_normals[index_tri[i]], ray_directions[index_ray[i]])
			ray_directions = last_ray_directions[index_ray] - 2*normal_dir_dot*element_normals[index_tri]

			if(DEBUG_VISUALIZATION_ENABLED):
				visualization.view_raycast(mesh, element_idx, ray_origins, ray_directions)

			#TODO: ¿Increment ray_amount? ¿What if a reflected ray hits the original element or another element two times? 
			locations, index_ray, index_tri = mesh.ray.intersects_location(ray_origins, ray_directions)
			for index in index_tri:
				view_factors_row[index] += 1

		view_factors_row /= ray_amount
		view_factors[element_idx] = (view_factors_row)
	return view_factors