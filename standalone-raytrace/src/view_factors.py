import numpy as np
import trimesh
from . import utils, visualization

DEBUG_VISUALIZATION_ENABLED = False
RAY_DISPLACEMENT = 1e-4

#prenumbra_fraction is the fraction of the umbra that is considered penumbra
def albedo_edge(ray_sun_dot_product, penumbra_fraction=0):
	min_albedo_dot_product = np.cos((1 - penumbra_fraction)*(np.pi/2))
	albedo_light_indices = ray_sun_dot_product > 0
	albedo_umbra_indices = ray_sun_dot_product < -min_albedo_dot_product
	ray_sun_dot_product[albedo_umbra_indices] = 0
	ray_sun_dot_product[albedo_light_indices] = 1
	ray_sun_dot_product = np.abs(ray_sun_dot_product)
	return ray_sun_dot_product

def element_earth(mesh, earth_direction, sun_direction, penumbra_fraction=0.05, ray_amount=1000):
	"""
	Receives a trimesh mesh object, a vector that represents the direction towards
	the earth and the amount of rays to be casted.
	Finds the view factors of the elements of the mesh with the earth and returns
	a list of the view factors.
	"""
	element_normals = trimesh.triangles.normals(mesh.triangles)[0]
	view_factors = np.zeros(utils.element_amount(mesh.triangles))

	for element_idx in range(utils.element_amount(mesh.triangles)):
		emitting_element = mesh.triangles[element_idx]
		emitting_element_normal = element_normals[element_idx]
	
		#Facing away from earth's plane
		if np.dot(emitting_element_normal, earth_direction) <= 0:
			continue

		ray_origins = utils.generate_random_points_in_element(emitting_element, ray_amount)
		ray_directions = utils.generate_random_unit_vectors(ray_amount)
		utils.orient_vector_towards_normal(ray_directions, earth_direction)

		ray_origins += ray_directions*RAY_DISPLACEMENT

		if(DEBUG_VISUALIZATION_ENABLED):
			visualization.view_raycast(mesh, element_idx, ray_origins, ray_directions)

		hit_element_ids, hit_ray_ids = mesh.ray.intersects_id(ray_origins, ray_directions, return_locations=False, multiple_hits=False)
		
		#View factor (fraction of visible area)
		view_factor = (ray_amount - hit_ray_ids.size)/ray_amount

		mask = np.ones(ray_amount, dtype=bool)
		mask[hit_ray_ids] = 0
		not_hit_ray_directions = ray_directions[mask]

		#Aparent area
		#ray_normal_dot_product = not_hit_ray_directions @ emitting_element_normal[:,np.newaxis].flatten()
		#aparent_area_coefficient = np.sum(ray_normal_dot_product / np.linalg.norm(not_hit_ray_directions, axis=1))/(not_hit_ray_directions.size // 3)

		#Albedo
		ray_sun_dot_product = -not_hit_ray_directions @ sun_direction[:,np.newaxis]
		albedo = np.sum(albedo_edge(ray_sun_dot_product, penumbra_fraction=penumbra_fraction))/(not_hit_ray_directions.size // 3)

		#aparent_area_coefficient * albedo * view_factor
		view_factors[element_idx] = albedo * view_factor

	return view_factors

def element_sun(mesh, sun_direction):
	"""
	Receives a trimesh mesh object and and vector that represents the direction towards the sun.
	Finds the view factors of the elements of the mesh with the sun and returns
	a list of the view factors.
	"""
	element_centers = np.array(list(map(lambda x: (x[0] + x[1] + x[2])/3, mesh.triangles)))
	element_normals = trimesh.triangles.normals(mesh.triangles)[0]
	
	ray_origins =  element_centers + sun_direction*RAY_DISPLACEMENT
	ray_directions = np.broadcast_to(sun_direction, (len(ray_origins), 3))
	element_sun_view_factors = utils.aparent_element_area_multiplier(ray_directions, element_normals)
	intersected = mesh.ray.intersects_any(ray_origins, ray_directions)
	element_sun_view_factors[intersected] = 0

	if(DEBUG_VISUALIZATION_ENABLED):
		invisible_nodes = np.arange(len(element_centers))[intersected]
		visualization.view_invisible_points(mesh, sun_direction, element_centers[invisible_nodes])
	
	return element_sun_view_factors

def _filter_reflected_rays_by_element_absorptance(absorptance, hit_points, hit_ray_ids, hit_element_ids):
	random_values = np.random.rand(len(hit_element_ids))
	reflected_rays = random_values > absorptance[hit_element_ids]
	absorbed_rays = random_values <= absorptance[hit_element_ids]

	_hit_points = hit_points[reflected_rays]
	_hit_ray_ids = hit_ray_ids[reflected_rays]
	_hit_element_ids = hit_element_ids[reflected_rays]

	return _hit_points, _hit_ray_ids, _hit_element_ids, hit_element_ids[absorbed_rays]


def element_element(mesh, props, ray_amount, max_reflections_amount, internal_emission):
	"""
	Receives a trimesh mesh object, a function that returns the material properties of an element,
	the amount of rays to be casted, the maximum amount of reflections and a boolean that
	indicates if the element emits light internally.
	Finds the view factors of the elements of the mesh with the other elements and returns
	a list of the view factors.
	"""
	element_normals = trimesh.triangles.normals(mesh.triangles)[0]
	view_factors = np.zeros((len(mesh.triangles), len(mesh.triangles)))
	absorptance = props.get_absorptance_by_element()
	
	for element_idx in range(len(mesh.triangles)):
		emitting_element = mesh.triangles[element_idx]
		emitting_element_normal = element_normals[element_idx]
		view_factors_row = np.zeros(len(mesh.triangles))

		#Original emission
		ray_origins = utils.generate_random_points_in_element(emitting_element, ray_amount)
		ray_directions = utils.generate_random_unit_vectors(ray_amount)
		if not internal_emission:
			utils.orient_vector_towards_normal(ray_directions, emitting_element_normal)

		ray_origins += ray_directions*RAY_DISPLACEMENT


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
			hit_points += RAY_DISPLACEMENT*element_normals[hit_element_ids]

			for absorbed_element_id in absorbed_element_ids:
				view_factors_row[absorbed_element_id] += 1

		view_factors_row /= ray_amount
		view_factors[element_idx] = (view_factors_row)
	
	return view_factors