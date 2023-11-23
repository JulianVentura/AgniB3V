import json
import meshio
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import Slider
import sys
import pandas as pd

# We have to install pip and then meshio for it to work


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


def parse_results_xls(directory, xls_path, progress):
    results_temperatures = {}
    results_positions = {}
    df = pd.read_excel(directory + "/" + xls_path)
    times = df["Time, s"]
    columns = []
    for col in df.columns:
        if "MAIN.T" in col:
            columns.append(col)
    for i, time in enumerate(times):
        progress((i / len(times)) * 100)
        temperatures = {}
        for col in columns:
            id = int(col.split(".")[1][1:])
            temperatures[id] = df[col][i]
        results_temperatures[time] = temperatures
    return results_temperatures, results_positions


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


plt.style.use("ggplot")


def plot_temperature_by_id(id, results):
    times = []
    temperatures = []
    for time, result in results.items():
        temperatures.append(result[id])
        times.append(time)

    plt.xlabel("Time", fontsize=12)
    plt.ylabel("Temperature", fontsize=12)
    plt.title(f"Temperatures of Node {id} Over Time", fontsize=14)
    plt.grid(
        True, linestyle="--", alpha=0.5
    )  # Adding grid lines with specific style and transparency
    plt.xticks(rotation=45)  # Rotating x-axis labels for better visibility
    plt.tight_layout()  # Adjusting layout for better spacing
    plt.plot(times, temperatures, label=f"ID {id}")
    plt.show()


def plot_all_temperatures(results):
    times = []
    id_temperatures = {}

    for time, result in results.items():
        times.append(time)
        for id, temp in result.items():
            if id in id_temperatures:
                id_temperatures[id].append(temp)
            else:
                id_temperatures[id] = [temp]

    for id, temps in id_temperatures.items():
        plt.plot(times, temps, linestyle="-", linewidth=2)

    plt.xlabel("Time", fontsize=12)
    plt.ylabel("Temperature", fontsize=12)
    plt.title("All Temperatures Over Time", fontsize=14)
    plt.grid(
        True, linestyle="--", alpha=0.5
    )  # Adding grid lines with specific style and transparency
    plt.xticks(rotation=45)  # Rotating x-axis labels for better visibility
    plt.tight_layout()  # Adjusting layout for better spacing
    plt.show()


def plot_average_temperature(results):
    times = []
    average_temperatures = []

    for time, result in results.items():
        times.append(time)
        average_temperatures.append(sum(result.values()) / len(result.values()))

    plt.plot(times, average_temperatures, linestyle="-", linewidth=2)
    plt.xlabel("Time", fontsize=12)
    plt.ylabel("Temperature", fontsize=12)
    plt.title("Average Temperatures Over Time", fontsize=14)
    plt.grid(
        True, linestyle="--", alpha=0.5
    )  # Adding grid lines with specific style and transparency
    plt.xticks(rotation=45)  # Rotating x-axis labels for better visibility
    plt.tight_layout()  # Adjusting layout for better spacing
    plt.show()


def plot_std_temperature(results):
    times = []
    std_temperatures = []

    for time, result in results.items():
        times.append(time)
        std_temperatures.append(np.std(list(result.values())))

    plt.plot(times, std_temperatures, linestyle="-", linewidth=2)
    plt.xlabel("Time", fontsize=12)
    plt.ylabel("Temperature", fontsize=12)
    plt.title("Standard Deviation Temperatures Over Time", fontsize=14)
    plt.grid(
        True, linestyle="--", alpha=0.5
    )  # Adding grid lines with specific style and transparency
    plt.xticks(rotation=45)  # Rotating x-axis labels for better visibility
    plt.tight_layout()  # Adjusting layout for better spacing
    plt.show()


def plot_3d_scatter(results_temperatures, results_positions):
    nodes = list(results_positions.keys())
    current_time = list(results_temperatures.keys())[0]

    # Create initial plot
    fig = plt.figure()
    ax = fig.add_subplot(111, projection="3d")
    scatter = ax.scatter(
        [results_positions[node][0] for node in nodes],
        [results_positions[node][1] for node in nodes],
        [results_positions[node][2] for node in nodes],
        c=[results_temperatures[current_time][node] for node in nodes],
        cmap="viridis",
        s=100,
    )

    # Add a color bar which maps values to colors
    plt.grid(False)
    cbar = plt.colorbar(scatter)
    cbar.set_label("Temperature")

    # Set labels and title
    ax.set_xlabel("X Label")
    ax.set_ylabel("Y Label")
    ax.set_zlabel("Z Label")
    ax.set_title("3D Scatter Plot with Temperature")

    # Slider
    ax_time = plt.axes([0.15, 0.02, 0.65, 0.03], facecolor="lightgoldenrodyellow")
    slider_time = Slider(
        ax_time,
        "Time",
        1,
        len(list(results_temperatures.keys())) - 1,
        valinit=1,
        valstep=1,
    )

    def update(val):
        global current_time, scatter
        current_time = list(results_temperatures.keys())[(int(slider_time.val))]
        ax.clear()
        scatter = ax.scatter(
            [results_positions[node][0] for node in nodes],
            [results_positions[node][1] for node in nodes],
            [results_positions[node][2] for node in nodes],
            c=[results_temperatures[current_time][node] for node in nodes],
            cmap="viridis",
            s=100,
        )
        ax.set_xlabel("X Label")
        ax.set_ylabel("Y Label")
        ax.set_zlabel("Z Label")
        ax.set_title("3D Scatter Plot with Temperature")
        fig.canvas.draw_idle()

    slider_time.on_changed(update)
    plt.show()


def plot_all(results_temperatures):
    plot_all_temperatures(results_temperatures)
    plot_temperature_by_id(0, results_temperatures)
    plot_average_temperature(results_temperatures)
    plot_std_temperature(results_temperatures)


def __main__():
    if len(sys.argv) < 3:
        print("Usage: python script.py [directory] [file_name.vtk.series] ...")
        sys.exit(1)

    directory = sys.argv[1]
    vtk_series_path = sys.argv[2]

    results_temperatures, results_positions = parse_results_vtk_series(
        directory, vtk_series_path
    )
    plot_all(results_temperatures)
    # plot_3d_scatter(results_temperatures, results_positions)


if __name__ == "__main__":
    __main__()
