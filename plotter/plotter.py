import json
import meshio
import matplotlib.pyplot as plt
import numpy as np

# We have to install pip and then meshio for it to work


def parse_vtk(vtk_path):
    temperatures = {}
    meshio_mesh = meshio.read(vtk_path, file_format="vtk")
    for i, temp in enumerate(meshio_mesh.point_data["Temperatura"]):
        temperatures[i] = temp[0]
    return temperatures


def parse_results_vtk_series(directory, vtk_series_path):
    results = {}
    with open(directory + "/" + vtk_series_path) as file:
        vtk_series = json.load(file)
    for vtk in vtk_series["files"]:
        time = vtk["time"]
        name = vtk["name"]
        temperatures = parse_vtk(directory + "/" + name)
        results[time] = temperatures
    return results


plt.style.use("ggplot")


def plot_temperature_by_id(id, results):
    times = []
    temperatures = []
    for time, result in results.items():
        temperatures.append(result[id])
        times.append(time)

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
    plt.title("Temperatures of IDs Over Time", fontsize=14)
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


results = parse_results_vtk_series("results", "cilindro_mesh_prepo_results.vtk.series")
plot_all_temperatures(results)
plot_temperature_by_id(0, results)
plot_average_temperature(results)
plot_std_temperature(results)
