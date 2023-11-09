import sys
import json
from src import properties_atlas, vtk_io, view_factors, visualization, serializer, gmat_parser
import numpy as np

def op_process_view_factors(mesh_file_path, properties_file_path, gmat_report_file_path, gmat_eclipse_file_path, view_factors_file_path):
    """
    Receives the mesh file path (vtk), the properties file path (json) and GMAT
    report and eclipse locator files (txt)
    It calculates the view factors for each step and saves them into the
    output_path file.
    """
    print("Starting process of view factors")
    mesh = vtk_io.load_vtk(mesh_file_path)
    properties = properties_atlas.PropertiesAtlas(len(mesh.triangles), properties_file_path)
    earth_ray_amount = properties.get_global_prop("earth_ray_amount")
    element_ray_amount = properties.get_global_prop("element_ray_amount")
    element_max_reflections_amount = properties.get_global_prop("element_max_reflections_amount")
    internal_emission = properties.get_global_prop("internal_emission")

    gmat_params = gmat_parser.parse_gmat(gmat_report_file_path, gmat_eclipse_file_path)
    sun_direction = np.array([
        gmat_params.sun_position.x,
        gmat_params.sun_position.y,
        gmat_params.sun_position.z
    ])
    element_sun_view_factors = [view_factors.element_sun(mesh, sun_direction)]

    element_element_view_factors = [view_factors.element_element(
            mesh,
            properties,
            element_ray_amount,
            element_max_reflections_amount,
            internal_emission,
     )]
    
    element_earth_view_factors = []
    for step in range(len(gmat_params.elapsed_secs)):
        earth_direction = -np.array([
            gmat_params.sat_position[step].x,
            gmat_params.sat_position[step].y,
            gmat_params.sat_position[step].z,
        ])
        element_earth_view_factors.append(
        view_factors.element_earth(
            mesh,
            earth_direction,
            sun_direction,
            ray_amount=earth_ray_amount
        ))

    serializer.serialize_view_factors(
        view_factors_file_path,
        element_earth_view_factors,
        element_sun_view_factors,
        element_element_view_factors
    )

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
    print(f"  python3 {argv[0]} process <mesh_file_path> <properties_file_path> <gmat_report_file_path> <gmat_eclipse_file_path>")
    print(f"  python3 {argv[0]} viewvf <mesh_file_path> <properties_file_path> <element_id>")
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
        process: mesh_file_path, properties_file_path
        viewvf: mesh_file_path, properties_file_path, element_id
        viewm: mesh_file_path, properties_file_path
    """
    if len(sys.argv) < 2:
        op_show_help(sys.argv)
        return

    match sys.argv:
        case [_, "process", mesh_file_path, properties_file_path, gmat_report_file_path, gmat_eclipse_file_path, view_factors_file_path]:
            op_process_view_factors(mesh_file_path, properties_file_path, gmat_report_file_path, gmat_eclipse_file_path, view_factors_file_path)
        case [_, "viewvf", mesh_file_path, properties_file_path, element_id]:
            op_visualize_view_factors(mesh_file_path, properties_file_path, element_id)
        case [_, "viewm", mesh_file_path, properties_file_path]:
            op_visualize_material(mesh_file_path, properties_file_path)
        case _:
            op_show_help(sys.argv)


if __name__ == "__main__":
    main()
