import vtk_parser
import matplotlib.pyplot as plt
import templates
import numpy as np
import std_deviation
import cuadratic_error


def plot():
    templates.template_style()
    files = ["622", "1178", "2841", "5539"]  # Meshes to compare
    points = [
        (158, 244, 417, 608),
        (155, 241, 408, 579),
        (248, 438, 963, 1745),
    ]  # Ids of points to compare for each model
    titles = [
        "Center of Panel",
        "Hidden Pyramid",
        "Interior Face",
    ]  # Titles for each point

    temperatures = []
    for file in files:
        temperatures.append(
            vtk_parser.parse_results_vtk_series(
                f"./sources/mesh_convergence/{file}/results",
                "result.vtk.series",
                lambda x: print(f"{x:.2f}"),
            )[0]
        )

    graphs = []
    names = []
    for i in range(len(points)):
        point = points[i]
        fig, ax = plt.subplots()
        temperatures_by_id = []
        for j in range(len(files)):
            times = []
            temperatures_id = []
            for time, result in temperatures[j].items():
                temperatures_id.append(result[point[j]])
                times.append(time)
            ax.plot(times, temperatures_id, label=f"Mesh {files[j]} elements")
            temperatures_by_id.append(temperatures_id)
        templates.template_plot(
            ax,
            "Time (s)",
            "Temperature (K)",
            f"Mesh Convergence at {titles[i]}",
        )
        graphs.append(ax)
        names.append(f"mesh_convergence_{titles[i]}")

        ax = std_deviation.plot_std_deviation(times, temperatures_by_id)
        templates.template_plot(
            ax,
            "Time (s)",
            "Standard Deviation of Temperature (K)",
            f"Standard Deviation over Mesh Convergence at {titles[i]}",
        )
        graphs.append(ax)
        names.append(f"mesh_convergence_std_deviation_{titles[i]}")

        ax = cuadratic_error.plot_cuadratic_error(
            times, temperatures_by_id, labels=[f + " elements" for f in files]
        )
        templates.template_plot(
            ax,
            "Time (s)",
            "Cuadratic Error of Temperature",
            f"Cuadratic Error over Mesh Convergence at {titles[i]} vs {files[-1]} elements",
        )
        graphs.append(ax)
        names.append(f"mesh_convergence_cuadratic_error_{titles[i]}")

    templates.template_save_multiple_images(graphs, "mesh_convergence", names)
