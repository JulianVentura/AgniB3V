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
			oriented_towards_normal = np.dot(random_direction, earth_direction) >= 0
			ray_directions[i] = random_direction if oriented_towards_normal else -random_direction

		if(DEBUG_VISUALIZATION_ENABLED):
			visualization.view_raycast(mesh, element_idx, ray_origins, ray_directions)

		locations, index_ray, index_tri = mesh.ray.intersects_location(ray_origins, ray_directions)
		view_factors[element_idx] = 1 if (len(index_tri) < ray_amount) else 0
	
	return view_factors

def element_sun(mesh, sun_direction, displacement=0.01):
	element_centers = np.array(list(map(lambda x: (x[0] + x[1] + x[2])/3, mesh.triangles)))
	ray_origins =  element_centers + sun_direction*displacement
	ray_directions = np.broadcast_to(sun_direction, (len(ray_origins), 3))
	intersected = mesh.ray.intersects_any(ray_origins, ray_directions)
	
	if(DEBUG_VISUALIZATION_ENABLED):
		invisible_nodes = np.arange(len(element_centers))[intersected]
		visualization.view_invisible_points(mesh, -sun_direction, element_centers[invisible_nodes])
	
	return [0 if x else 1 for x in intersected]

def _filter_reflected_rays_by_element_absorptance(absorptance, hit_points, hit_ray_ids, hit_element_ids):
	random_values = np.random.rand(len(hit_element_ids))
	reflected_rays = random_values > absorptance[hit_element_ids]
	absorbed_rays = random_values <= absorptance[hit_element_ids]

	_hit_points = hit_points[reflected_rays]
	_hit_ray_ids = hit_ray_ids[reflected_rays]
	_hit_element_ids = hit_element_ids[reflected_rays]

	return _hit_points, _hit_ray_ids, _hit_element_ids, hit_element_ids[absorbed_rays]


def element_element(mesh, properties, ray_amount=1000, max_reflections_amount=3, displacement=0.1, internal_emission=True):
	element_normals = trimesh.triangles.normals(mesh.triangles)[0]
	view_factors = np.zeros((len(mesh.triangles), len(mesh.triangles)))
	
	absorptance = np.zeros(len(mesh.triangles))
	for element_idx in range(len(mesh.triangles)):
		element_material = properties.get_material_props(element_idx)
		absorptance[element_idx] = element_material['absorptance']

	for element_idx in range(len(mesh.triangles)):
		emitting_element = mesh.triangles[element_idx]
		emitting_element_normal = element_normals[element_idx]
		view_factors_row = np.zeros(len(mesh.triangles))

		#Original emission
		ray_origins = utils.generate_random_points_in_element(emitting_element, ray_amount)
		ray_origins += displacement*emitting_element_normal
		ray_directions = utils.generate_random_unit_vectors(ray_amount)

		if not internal_emission:
			utils.orient_vector_towards_normal(ray_directions, emitting_element_normal)

		if(DEBUG_VISUALIZATION_ENABLED):
			visualization.view_raycast(mesh, element_idx, ray_origins, ray_directions)

		hit_element_ids, hit_ray_ids, hit_points = mesh.ray.intersects_id(ray_origins, ray_directions, return_locations=True, multiple_hits=False)
		hit_points, hit_ray_ids, hit_element_ids, absorbed_element_ids =_filter_reflected_rays_by_element_absorptance(absorptance, hit_points, hit_ray_ids, hit_element_ids)
		for absorbed_ray_id in absorbed_element_ids:
			view_factors_row[absorbed_ray_id] += 1
		
		#Reflexions
		for j in range(max_reflections_amount):
			if len(ray_origins) == 0:
				break
			
			ray_directions = utils.reflected_rays(ray_directions[hit_ray_ids], element_normals[hit_element_ids])

			if(DEBUG_VISUALIZATION_ENABLED):
				visualization.view_raycast(mesh, element_idx, ray_origins, ray_directions)

			hit_element_ids, hit_ray_ids, hit_points = mesh.ray.intersects_id(hit_points, ray_directions, return_locations=True, multiple_hits=False)
			hit_points, hit_ray_ids, hit_element_ids, absorbed_element_ids =_filter_reflected_rays_by_element_absorptance(absorptance, hit_points, hit_ray_ids, hit_element_ids)
			hit_points += displacement*element_normals[hit_element_ids]

			for absorbed_element_id in absorbed_element_ids:
				view_factors_row[absorbed_element_id] += 1

		print(view_factors_row)
		view_factors_row /= ray_amount
		view_factors[element_idx] = (view_factors_row)
	
	return view_factors