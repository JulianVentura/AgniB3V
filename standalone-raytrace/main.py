import sys
import json
from src import properties_atlas, vtk_io, view_factors, visualization
import numpy as np


def op_process_view_factors(
    mesh_file_path,
    properties_file_path,
    output_path,
    sun_direction,
    internal_emission,
):
    """
    Recieves the mesh file path (vtk), the properties file path (json), the output path (json),
    the sun direction (vector) and a boolean indicating if the internal emission is enabled.
    It calculates the view factors and saves them into the output_path file.
    """
    internal_emission = internal_emission == "true"
    mesh = vtk_io.load_vtk(mesh_file_path)

    sun_direction = np.array(list(map(float, sun_direction.strip("[]").split(","))))
    props = properties_atlas.PropertiesAtlas(len(mesh.triangles), properties_file_path)

    element_sun_view_factors = view_factors.element_sun(mesh, sun_direction)
    element_element_view_factors = view_factors.element_element(
        mesh, props, 500, 3, internal_emission
    )
    element_earth_view_factors = view_factors.element_earth(
        mesh, list(map(lambda x: -x, sun_direction)), 200
    )

    props.add_prop(
        "view_factors",
        {
            "sun": list(element_sun_view_factors),
            "earth": list(element_earth_view_factors),
            "elements": list(map(list, element_element_view_factors)),
        },
    )
    props.dump(output_path)


def op_process_view_factors_config(config_file_path):
    """
    Recieves the config file path (json) and calculates the view factors and
    saves them into the defined output file.
    """
    config_file = open(config_file_path)
    config_json = json.load(config_file)
    op_process_view_factors(
        config_json["mesh_file_path"],
        config_json["properties_file_path"],
        config_json["output_path"],
        config_json["sun_direction"],
        config_json["internal_emission"],
    )


def op_visualize_view_factors(mesh_file_path, properties_file_path, element_id):
    """
    Recieves the mesh file path (vtk), the properties file path (json) and the element id
    and creates a visualization of the view factors of the element.
    """
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
    Recieves the mesh file path (vtk) and the properties file path (json) and creates
    a visualization of the material.
    """
    mesh = vtk_io.load_vtk(mesh_file_path)
    props = properties_atlas.PropertiesAtlas(len(mesh.triangles), properties_file_path)
    visualization.view_material(mesh, props)


def op_show_help(argv):
    """
    Recieves the argv list and prints a help message.
    """
    print("Use:")
    print(f"  python3 {argv[0]} process <config_file_path>")
    print(
        f"  python3 {argv[0]} processcli <mesh_file_path> <properties_file_path> <output_path> <sun_direction> <internal_emission>"
    )
    print(f"  python3 {argv[0]} viewvf <mesh_file_path> <properties_file_path> <element_id>")
    print(f"  python3 {argv[0]} viewm <mesh_file_path> <properties_file_path>")


def main():
    """
    Reads from the argv and expect a command as a first argument.
    
    The commands are:
        process: given a config file, it calculates the view factors.
        processcli: given the expected arguments, it calculates the view factors.
        viewvf: creates visualization for the view factors of an element.
        viewm: creates visualization for the material of the mesh.

    For each command expect the following arguments:
        process: config_file_path
        processcli: mesh_file_path, properties_file_path, output_path, sun_direction, internal_emission
        viewvf: mesh_file_path, properties_file_path, element_id
        viewm: mesh_file_path, properties_file_path
    """
    if len(sys.argv) < 2:
        op_show_help(sys.argv)
        return

    match sys.argv:
        case [_, "process", config_file_path]:
            op_process_view_factors_config(config_file_path)
        case [_, "processcli", mesh_file_path, properties_file_path, output_path, sun_direction, internal_emission]:
            op_process_view_factors(mesh_file_path, properties_file_path, output_path, sun_direction, internal_emission)
        case [_, "viewvf", mesh_file_path, properties_file_path, element_id]:
            op_visualize_view_factors(mesh_file_path, properties_file_path, element_id)
        case [_, "viewm", mesh_file_path, properties_file_path]:
            op_visualize_material(mesh_file_path, properties_file_path)
        case _:
            op_show_help(sys.argv)


if __name__ == "__main__":
    main()
