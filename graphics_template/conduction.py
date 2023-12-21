import vtk_parser
import matplotlib.pyplot as plt
import templates
import numpy as np
import std_deviation
import cuadratic_error


def plot():
    templates.template_style()

    files = ["Prueba1", "Prueba2", "Prueba3", "Prueba4", "Prueba5"]
    graphs = []
    names = []
    for file in files:
        temperatures = vtk_parser.parse_results_vtk_series(
            f"./sources/conduction/{file}/results",
            "result.vtk.series",
            lambda x: print(f"{x:.2f}"),
        )[0]

        fig, ax = plt.subplots()
        times = []

        id_temperatures = {}
        for time, result in temperatures.items():
            times.append(time)
            for id, temp in result.items():
                if id in id_temperatures:
                    id_temperatures[id].append(temp)
                else:
                    id_temperatures[id] = [temp]

        for id, temps in id_temperatures.items():
            ax.plot(times, temps)

        templates.template_plot(
            ax,
            "Time (s)",
            "Temperature (K)",
            f"Temperature vs Time of {file}",
        )
        graphs.append(ax)
        names.append(f"conduction_{file}")

    templates.template_save_multiple_images(graphs, "conduction", names)
