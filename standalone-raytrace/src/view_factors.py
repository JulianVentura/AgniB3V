import numpy as np
import trimesh
from . import utils, visualization

DEBUG_VISUALIZATION_ENABLED = False
RAY_DISPLACEMENT = 1e-4
IR_SCALE_FACTOR = 2.35


def albedo_edge(ray_sun_dot_product, penumbra_fraction=0):
    """
    Sets ray contribution to zero if it comes from umbra.
    prenumbra_fraction is the fraction of the umbra that is considered penumbra
    """
    min_albedo_dot_product = np.cos((1 - penumbra_fraction) * (np.pi / 2))
    albedo_umbra_indices = ray_sun_dot_product < -min_albedo_dot_product
    ray_sun_dot_product[albedo_umbra_indices] = 0
    return np.abs(ray_sun_dot_product)


def element_earth(
    mesh, earth_direction, sun_direction, penumbra_fraction=0, ray_amount=1000
):
    """
    Receives a trimesh mesh object, a vector that represents the direction towards
    the earth and the amount of rays to be casted.
    Finds the view factors of the elements of the mesh with the earth and returns
    a list of the view factors.
    """
    element_normals = trimesh.triangles.normals(mesh.triangles)[0]
    ir_view_factors = np.zeros(utils.element_amount(mesh.triangles))
    albedo_view_factors = np.zeros(utils.element_amount(mesh.triangles))

    for element_idx in range(utils.element_amount(mesh.triangles)):
        emitting_element = mesh.triangles[element_idx]
        emitting_element_normal = element_normals[element_idx]

        ray_origins = utils.generate_random_points_in_element(
            emitting_element, ray_amount
        )
        ray_directions = utils.generate_random_unit_vectors(ray_amount)
        utils.orient_vector_towards_normal(ray_directions, earth_direction)
        ray_origins += ray_directions * RAY_DISPLACEMENT

        if DEBUG_VISUALIZATION_ENABLED:
            visualization.view_raycast(mesh, element_idx, ray_origins, ray_directions)
        hit_element_ids = mesh.ray.intersects_first(ray_origins, ray_directions)
        mask = np.ones(ray_amount, dtype=bool)
        mask[hit_element_ids >= 0] = 0
        not_hit_ray_directions = ray_directions[mask]
        not_hit_ray_directions = utils.flip_vectors_around_axis(
            earth_direction, not_hit_ray_directions
        )

        if not_hit_ray_directions.size == 0:
            ir_view_factors[element_idx] = 0
            albedo_view_factors[element_idx] = 0
            continue

        ray_sat_dot_product = np.abs(
            utils.array_dot(not_hit_ray_directions, emitting_element_normal)
        )

        # IR
        ray_earth_dot_product = utils.array_dot(not_hit_ray_directions, earth_direction)
        ray_earth_dot_product[ray_earth_dot_product < 0] = 0
        ir_view_factor = IR_SCALE_FACTOR * ray_earth_dot_product * ray_sat_dot_product
        ir_view_factors[element_idx] = np.sum(ir_view_factor) / ray_amount
        # Albedo
        ray_sun_dot_product = utils.array_dot(not_hit_ray_directions, -sun_direction)
        albedo_view_factor = (
            ray_earth_dot_product
            * ray_sat_dot_product
            * albedo_edge(ray_sun_dot_product, penumbra_fraction=penumbra_fraction)
        )
        albedo_view_factors[element_idx] = np.sum(albedo_view_factor) / ray_amount

    return ir_view_factors, albedo_view_factors


def element_sun(mesh, sun_direction):
    """
    Receives a trimesh mesh object and and vector that represents the direction towards the sun.
    Finds the view factors of the elements of the mesh with the sun and returns
    a list of the view factors.
    """
    element_centers = np.array(
        list(map(lambda x: (x[0] + x[1] + x[2]) / 3, mesh.triangles))
    )
    element_normals = trimesh.triangles.normals(mesh.triangles)[0]

    ray_origins = element_centers + sun_direction * RAY_DISPLACEMENT
    ray_directions = np.broadcast_to(sun_direction, (len(ray_origins), 3))
    element_sun_view_factors = utils.aparent_element_area_multiplier(
        ray_directions, element_normals
    )
    intersected = mesh.ray.intersects_any(ray_origins, ray_directions)
    element_sun_view_factors[intersected] = 0

    if DEBUG_VISUALIZATION_ENABLED:
        invisible_nodes = np.arange(len(element_centers))[intersected]
        visualization.view_invisible_points(
            mesh, sun_direction, element_centers[invisible_nodes]
        )

    return element_sun_view_factors

def _filter_reflected_rays_by_element_absorptance(
    absorptance, hit_points, hit_ray_ids, hit_element_ids
):
    random_values = np.random.rand(hit_element_ids.size)
    reflected_mask = random_values > absorptance[hit_element_ids]
    absorbed_mask = random_values <= absorptance[hit_element_ids]

    reflected_hit_points = hit_points[reflected_mask]
    reflected_hit_ray_ids = hit_ray_ids[reflected_mask]
    reflected_element_ids = hit_element_ids[reflected_mask]
    absorbed_element_ids = hit_element_ids[absorbed_mask]
    return (
        reflected_hit_points,
        reflected_hit_ray_ids,
        reflected_element_ids,
        absorbed_element_ids,
    )


def element_element(
    mesh, absorptance_by_element, ray_amount, max_reflections_amount, internal_emission
):
    """
    Receives a trimesh mesh object, a function that returns the material properties of an element,
    the amount of rays to be casted, the maximum amount of reflections and a boolean that
    indicates if the element emits light internally.
    Finds the view factors of the elements of the mesh with the other elements and returns
    a list of the view factors.
    """
    element_normals = trimesh.triangles.normals(mesh.triangles)[0]
    view_factors = np.zeros((len(mesh.triangles), len(mesh.triangles)))

    for element_idx in range(len(mesh.triangles)):
        emitting_element = mesh.triangles[element_idx]
        emitting_element_normal = element_normals[element_idx]
        view_factors_row = np.zeros(len(mesh.triangles))

        # Original emission
        ray_origins = utils.generate_random_points_in_element(
            emitting_element, ray_amount
        )
        ray_directions = utils.generate_random_unit_vectors(ray_amount)
        if not internal_emission:
            utils.orient_vector_towards_normal(ray_directions, emitting_element_normal)

        ray_origins += ray_directions * RAY_DISPLACEMENT

        if DEBUG_VISUALIZATION_ENABLED:
            visualization.view_raycast(mesh, element_idx, ray_origins, ray_directions)

        hit_element_ids, hit_ray_ids, hit_points = mesh.ray.intersects_id(
            ray_origins, ray_directions, return_locations=True, multiple_hits=False
        )
        (
            hit_points,
            hit_ray_ids,
            hit_element_ids,
            absorbed_element_ids,
        ) = _filter_reflected_rays_by_element_absorptance(
            absorptance_by_element, hit_points, hit_ray_ids, hit_element_ids
        )

        for absorbed_element_id in absorbed_element_ids:
            view_factors_row[absorbed_element_id] += 1

        # Reflexions
        for _ in range(max_reflections_amount):
            if hit_element_ids.size == 0:
                break

            hit_points += RAY_DISPLACEMENT * element_normals[hit_element_ids]

            ray_directions = utils.reflected_rays(
                ray_directions[hit_ray_ids], element_normals[hit_element_ids]
            )

            if DEBUG_VISUALIZATION_ENABLED:
                visualization.view_raycast(
                    mesh, element_idx, ray_origins, ray_directions
                )

            hit_element_ids, hit_ray_ids, hit_points = mesh.ray.intersects_id(
                hit_points, ray_directions, return_locations=True, multiple_hits=False
            )
            (
                hit_points,
                hit_ray_ids,
                hit_element_ids,
                absorbed_element_ids,
            ) = _filter_reflected_rays_by_element_absorptance(
                absorptance_by_element, hit_points, hit_ray_ids, hit_element_ids
            )

            for absorbed_element_id in absorbed_element_ids:
                view_factors_row[absorbed_element_id] += 1

        view_factors_row /= ray_amount
        view_factors[element_idx] = view_factors_row

    return view_factors


def mesh_look_at(mesh, direction):
    norm, phi, theta = utils.vector_spherical_cordinates(direction)
    rot_matrix = trimesh.transformations.rotation_matrix(theta, [1, 0, 0])
    mesh.apply_transform(rot_matrix)
    rot_matrix = trimesh.transformations.rotation_matrix(phi, [0, 0, 1])
    mesh.apply_transform(rot_matrix)
