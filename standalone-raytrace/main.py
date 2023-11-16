import sys
import json
from src import utils, properties_atlas, vtk_io, view_factors, visualization, serializer
import numpy as np


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


def op_process_view_factors(
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
        len(mesh.triangles),
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
    sun_direction = utils.normalize(properties.orbit_properties.sun_position)

    if orbit_divisions > len(elapsed_secs):
        print(
            f"Error: Orbit divisions ({orbit_divisions}) is greater than GMAT data rows ({len(elapsed_secs)})"
        )
        sys.exit(1)

    print("Setting up bodies")
    view_factors.mesh_look_at(mesh, sun_direction)

    print("Calculating sun view factors")
    element_sun_view_factors = [
        (
            view_factors.element_sun(mesh, sun_direction),
            properties.orbit_properties.elapsed_secs[0],
        )
    ]

    print("Calculating element-element view factors")
    element_element_view_factors = view_factors.element_element(
        mesh,
        properties.absortance_by_element,
        element_ray_amount,
        element_max_reflections_amount,
        internal_emission,
    )

    print("Calculating earth view factors")
    element_earth_ir_view_factors = []
    element_earth_albedo_view_factors = []
    division_number = 0
    for step in range(len(elapsed_secs)):
        if not _is_closest_orbit_point(
            step, elapsed_secs, division_time * division_number
        ):
            continue

        earth_direction = utils.normalize(
            -properties.orbit_properties.sat_position[step]
        )
        earth_view_factors, earth_albedo_coefficients = view_factors.element_earth(
            mesh, earth_direction, sun_direction, ray_amount=earth_ray_amount
        )
        element_earth_ir_view_factors.append((earth_view_factors, elapsed_secs[step]))
        element_earth_albedo_view_factors.append(
            (earth_view_factors * earth_albedo_coefficients, elapsed_secs[step])
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
        element_element_view_factors,
    )
    print("Done")


def op_visualize_view_factors(mesh_file_path, properties_file_path, element_id):
    """
    Receives the mesh file path (vtk), the properties file path (json) and the element id
    and creates a visualization of the view factors of the element.
    """
    print("Starting visualization of view factors")
    mesh = vtk_io.load_vtk(mesh_file_path)
    element_id = int(element_id)
    material_file = open(properties_file_path)
    material_json = json.load(material_file)

    # visualization.view_other_view_factors(mesh, material_json["view_factors"]["earth"])
    visualization.view_element_view_factors(
        mesh, element_id, material_json["view_factors"]["elements"][element_id]
    )


def op_visualize_material(mesh_file_path, properties_file_path):
    """
    Receives the mesh file path (vtk) and the properties file path (json) and creates
    a visualization of the material.
    """
    print("Starting visualization of material")
    mesh = vtk_io.load_vtk(mesh_file_path)
    props = properties_atlas.PropertiesAtlas(len(mesh.triangles), properties_file_path)
    visualization.view_material(mesh, props)


def op_show_help(argv):
    """
    Receives the argv list and prints a help message.
    """
    print("Use:")
    print(
        f"  python3 {argv[0]} process <mesh_file_path> <properties_file_path> <gmat_report_file_path> <gmat_eclipse_file_path> <view_factors_file_path>"
    )
    print(
        f"  python3 {argv[0]} viewvf <mesh_file_path> <properties_file_path> <element_id>"
    )
    print(f"  python3 {argv[0]} viewm <mesh_file_path> <properties_file_path>")


def main():
    """
    Reads from the argv and expect a command as a first argument.

    The commands are:
        process: given a mesh file, a properties file and gmat report and eclipse files
        it calculates the view factors.
        viewvf: creates visualization for the view factors of an element.
        viewm: creates visualization for the material of the mesh.

    For each command expect the following arguments:
        process: mesh_file_path, properties_file_path, gmat_report_file_path, gmat_eclipse_file_path, view_factors_file_path
        viewvf: mesh_file_path, properties_file_path, element_id
        viewm: mesh_file_path, properties_file_path
    """
    if len(sys.argv) < 2:
        op_show_help(sys.argv)
        return

    match sys.argv:
        case [
            _,
            "process",
            mesh_file_path,
            properties_file_path,
            gmat_report_file_path,
            gmat_eclipse_file_path,
            view_factors_file_path,
        ]:
            op_process_view_factors(
                mesh_file_path,
                properties_file_path,
                gmat_report_file_path,
                gmat_eclipse_file_path,
                view_factors_file_path,
            )
        case [_, "viewvf", mesh_file_path, properties_file_path, element_id]:
            op_visualize_view_factors(mesh_file_path, properties_file_path, element_id)
        case [_, "viewm", mesh_file_path, properties_file_path]:
            op_visualize_material(mesh_file_path, properties_file_path)
        case _:
            op_show_help(sys.argv)


if __name__ == "__main__":
    main()
