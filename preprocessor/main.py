import os
import sys
from src import commands

def _get_file_with_name(directory, filename):
    """
    Given a filename and a directory, it looks for a file that matches the name 
    in the given directory and returns its path.
    """
    files = [f for f in os.listdir(directory)]
    for file in files:
        if filename in file:
            return f"{directory}/{file}"
    raise FileNotFoundError(filename)

def main():
    """
    Reads from the argv and expect a command as the first argument.

    The commands are:
        process: given the mesh, properties, gmat report and eclipse report files
        it calculates the view factors.
        viewm: given the mesh and properties files it displays the materials of the mesh.
        viewn: given the mesh file it displays the normal orientation of each mesh element.
    """
    if len(sys.argv) < 3:
        commands.show_help(sys.argv)
        return

    [_, opcode, files_directory_path] = sys.argv

    if files_directory_path[-1] != "/":
        files_directory_path += "/"

    try:
        mesh_file_path = _get_file_with_name(files_directory_path, "mesh.vtk")
        properties_file_path = _get_file_with_name(files_directory_path, "properties.json")
        view_factors_file_path = f"{files_directory_path}/view_factors.vf"
    except FileNotFoundError as e:
        print("Error: File not found", e)
        return -1

    try:
        match opcode:
            case "process":
                try:
                    gmat_report_file_path = _get_file_with_name(files_directory_path, "ReportFile")
                    gmat_eclipse_file_path = _get_file_with_name(files_directory_path, "EclipseLocator")
                except FileNotFoundError as e:
                    print("Error: File not found", e)
                    return -1
                commands.process_view_factors(
                    mesh_file_path,
                    properties_file_path,
                    gmat_report_file_path,
                    gmat_eclipse_file_path,
                    view_factors_file_path,
                )

            case "viewm":
                commands.visualize_material(mesh_file_path, properties_file_path)
            
            case "viewn":
                commands.visualize_normal(mesh_file_path)
            
            case _:
                commands.show_help(sys.argv)
    except Exception as  e:
        print("Error:" , e)

if __name__ == "__main__":
    main()
