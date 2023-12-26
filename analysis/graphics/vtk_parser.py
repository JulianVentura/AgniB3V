import json
import meshio


def parse_vtk(vtk_path):
    # print("Parsing ", vtk_path)
    temperatures = {}
    try:
        meshio_mesh = meshio.read(vtk_path, file_format="vtk")
    except:
        raise Exception("Invalid vtk file")
    for i, temp in enumerate(meshio_mesh.point_data["Temperature"]):
        temperatures[i] = temp[0]
    return temperatures


def get_positions(vtk_path):
    print("Getting positions")
    positions = {}
    meshio_mesh = meshio.read(vtk_path, file_format="vtk")
    for i, position in enumerate(meshio_mesh.points):
        positions[i] = position
    return positions


def parse_results_vtk_series(directory, vtk_series_path, progress):
    results_temperatures = {}
    results_positions = {}
    with open(directory + "/" + vtk_series_path) as file:
        try:
            vtk_series = json.load(file)
        except:
            raise Exception("Invalid vtk.series file")
    print("Loaded VTK Series")

    files_length = len(vtk_series["files"])
    for i, vtk in enumerate(vtk_series["files"]):
        progress((i / files_length) * 100)

        time = vtk["time"]
        name = vtk["name"]
        temperatures = parse_vtk(directory + "/" + name)
        results_temperatures[time] = temperatures
    if len(vtk_series["files"]) > 0:
        results_positions = get_positions(
            directory + "/" + vtk_series["files"][0]["name"]
        )
    return results_temperatures, results_positions
