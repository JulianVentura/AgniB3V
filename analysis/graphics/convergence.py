import vtk_parser
import matplotlib.pyplot as plt
import templates
import numpy as np
import std_deviation
import relative_error


def plot_convergence(source, files, points, titles, label_generator, type, unit):
    templates.template_style()

    temperatures = []
    for file in files:
        temperatures.append(
            vtk_parser.parse_results_vtk_series(
                f"./sources/{source}/{file}/results",
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
            ax.plot(times, temperatures_id, label=label_generator(files[j]))
            temperatures_by_id.append(temperatures_id)
        templates.template_plot(
            ax,
            "Time (s)",
            "Temperature (K)",
            f"{type} Convergence at {titles[i]}",
        )
        graphs.append(ax)
        names.append(f"{source}_{titles[i]}")

        ax = std_deviation.plot_std_deviation(times, temperatures_by_id)
        templates.template_plot(
            ax,
            "Time (s)",
            "Standard Deviation of Temperature (K)",
            f"Standard Deviation over {type} Convergence at {titles[i]}",
        )
        graphs.append(ax)
        names.append(f"{source}_std_deviation_{titles[i]}")

        ax = relative_error.plot_relative_error(
            times, temperatures_by_id, labels=[f + " " + unit for f in files]
        )
        templates.template_plot(
            ax,
            "Time (s)",
            "Relative Error of Temperature",
            f"Relative Error over {type} Convergence at {titles[i]} vs {files[-1]} {unit}",
        )
        graphs.append(ax)
        names.append(f"{source}_relative_error_{titles[i]}")

    templates.template_save_multiple_images(graphs, source, names)
