import numpy as np
from . import vector_math, mesh_ops, properties_atlas, vtk_io, view_factors, visualization, serializer

def _is_closest_orbit_point(step, elapsed_secs, target_time):
    if step == len(elapsed_secs) - 1:
        return True
    curr_elapsed_seconds = elapsed_secs[step]
    next_elapsed_seconds = elapsed_secs[step + 1]

    if next_elapsed_seconds > target_time and np.abs(
        target_time - curr_elapsed_seconds
    ) < np.abs(target_time - next_elapsed_seconds):
        return True
    return False


def process_view_factors(
    mesh_file_path,
    properties_file_path,
    orbit_report_file_path,
    orbit_eclipse_file_path,
    view_factors_file_path,
):
    """
    Receives the mesh file path (vtk), the properties file path (json) and GMAT
    report and eclipse locator files (txt)
    It calculates the view factors for each step and saves them into the
    output_path file.
    """
    print("Starting process of view factors")

    print(f"Loading mesh")
    mesh = vtk_io.load_vtk(mesh_file_path)

    print(f"Loading properties")
    properties = properties_atlas.PropertiesAtlas(
        mesh_ops.element_amount(mesh),
        properties_file_path,
        orbit_report_file_path,
        orbit_eclipse_file_path,
    )
    earth_ray_amount = properties.global_properties["earth_ray_amount"]
    element_ray_amount = properties.global_properties["element_ray_amount"]
    element_max_reflections_amount = properties.global_properties[
        "element_max_reflections_amount"
    ]
    internal_emission = properties.global_properties["internal_emission"]
    orbit_divisions = properties.global_properties["orbit_divisions"]
    division_time = properties.orbit_properties.period / orbit_divisions
    elapsed_secs = properties.orbit_properties.elapsed_secs
    sun_direction = vector_math.normalize(properties.orbit_properties.sun_position)

    if orbit_divisions > len(elapsed_secs):
        raise Exception(
            "Orbit divisions ({orbit_divisions}) is greater than GMAT data rows ({len(elapsed_secs)})"
        )

    print("Setting up celestial bodies")
    mesh_ops.look_at(mesh, sun_direction)

    print("Calculating element-element ir view factors")
    element_element_ir_view_factors = view_factors.element_element(
        mesh,
        properties.absortance_ir_by_element,
        element_ray_amount,
        element_max_reflections_amount,
        internal_emission,
    )

    print("Calculating sun view factors")
    element_sun_view_factors = [
        (
            view_factors.element_sun(mesh, sun_direction),
            properties.orbit_properties.elapsed_secs[0],
        )
    ]

    print("Calculating earth view factors")
    element_earth_ir_view_factors = []
    element_earth_albedo_view_factors = []
    division_number = 0

    for step in range(len(elapsed_secs)):
        if not _is_closest_orbit_point(
            step, elapsed_secs, division_time * division_number
        ):
            continue

        earth_direction = vector_math.normalize(
            -properties.orbit_properties.sat_position[step]
        )

        ir_view_factors, albedo_view_factors = view_factors.element_earth(
            mesh,
            earth_direction,
            sun_direction,
            penumbra_fraction=0.0,
            ray_amount=earth_ray_amount,
        )
        element_earth_ir_view_factors.append((ir_view_factors, elapsed_secs[step]))
        element_earth_albedo_view_factors.append(
            (albedo_view_factors, elapsed_secs[step])
        )
        division_number += 1
        if division_number == orbit_divisions:
            break
        print(f"{(division_number*100)/orbit_divisions:>5.1f}%")
    print(f"{100:>5.1f}%")
    print(f"Orbit was divided into {division_number} points")
    print("Writing output files")

    properties.dump(properties_file_path)
    serializer.serialize_view_factors(
        view_factors_file_path,
        element_earth_ir_view_factors,
        element_earth_albedo_view_factors,
        element_sun_view_factors,
        element_element_ir_view_factors,
    )


def visualize_material(mesh_file_path, properties_file_path):
    """
    Receives the mesh file path (vtk) and the properties file path (json) and creates
    a visualization of the material.
    """
    print("Starting visualization of material")
    mesh = vtk_io.load_vtk(mesh_file_path)
    props = properties_atlas.PropertiesAtlas(mesh_ops.element_amount(mesh), properties_file_path)
    visualization.view_material(mesh, props)


def visualize_normal(mesh_file_path):
    """
    Receives the mesh file path (vtk) and creates a visualization of normals direction.
    """
    print("Starting visualization of normals")
    mesh = vtk_io.load_vtk(mesh_file_path)
    visualization.view_normal(mesh)


def show_help(argv):
    """
    Receives the argv list and prints a help message.
    """
    print("Use:")
    print(f"  python3 {argv[0]} process <files_directory_path>")
    print(f"  Requires: mesh, properties, ReportFile and EclipseLocator files")
    print(f"  python3 {argv[0]} viewm <files_directory_path>")
    print(f"  Requires: mesh and properties files")
    print(f"  python3 {argv[0]} viewn <files_directory_path>")
    print(f"  Requires: mesh file")
