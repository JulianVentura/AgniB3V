import sys
import json
from src import properties_atlas, vtk_io, view_factors, visualization
import numpy as np


def op_process_view_factors(mesh_file_path, properties_file_path):
    """
    Receives the mesh file path (vtk) and the properties file path (json).
    It calculates the view factors and saves them into the output_path file.
    """
    print("Starting process of view factors")
    mesh = vtk_io.load_vtk(mesh_file_path)
    props = properties_atlas.PropertiesAtlas(len(mesh.triangles), properties_file_path)

    SUN_DISPLACEMENT = 0.05
    ELEMENT_DISPLACEMENT = 0.1
    EARTH_DISPLACEMENT = 0.05
    
    sun_direction = np.array(list(map(float, props.get_global_prop("sun_direction").strip("[]").split(","))))

    element_sun_view_factors = view_factors.element_sun(mesh, sun_direction, SUN_DISPLACEMENT)
    element_element_view_factors = view_factors.element_element(mesh, props, ELEMENT_DISPLACEMENT)
    element_earth_view_factors = view_factors.element_earth(
        mesh, list(map(lambda x: -x, sun_direction)), EARTH_DISPLACEMENT
    )

    props.add_prop(
        "view_factors",
        {
            "sun": list(element_sun_view_factors),
            "earth": list(element_earth_view_factors),
            "elements": list(map(list, element_element_view_factors)),
        },
    )
    props.dump(properties_file_path)

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
    print(f"  python3 {argv[0]} process <mesh_file_path> <properties_file_path>")
    print(f"  python3 {argv[0]} viewvf <mesh_file_path> <properties_file_path> <element_id>")
    print(f"  python3 {argv[0]} viewm <mesh_file_path> <properties_file_path>")


def main():
    """
    Reads from the argv and expect a command as a first argument.
    
    The commands are:
        process: given a mesh file and a properties file, it calculates the view factors.
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
        case [_, "process", mesh_file_path, properties_file_path]:
            op_process_view_factors(mesh_file_path, properties_file_path)
        case [_, "viewvf", mesh_file_path, properties_file_path, element_id]:
            op_visualize_view_factors(mesh_file_path, properties_file_path, element_id)
        case [_, "viewm", mesh_file_path, properties_file_path]:
            op_visualize_material(mesh_file_path, properties_file_path)
        case _:
            op_show_help(sys.argv)


if __name__ == "__main__":
    main()
