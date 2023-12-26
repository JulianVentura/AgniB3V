import matplotlib.pyplot as plt
import os
import csv
import templates
import vtk_parser


def plot():
    file_name = "./sources/energy/results/result.vtk.series"

    temperatures = vtk_parser.parse_results_vtk_series(
        os.path.dirname(file_name),
        os.path.basename(file_name),
        lambda x: print(f"{x:.2f}"),
    )[0]

    fluxes = []
    with open("./sources/energy/output.csv", newline="") as output:
        reader = csv.reader(output, delimiter=",")
        for row in reader:
            fluxes.append([float(r) for r in row])

    with open("./sources/energy/areas.csv", newline="") as csvfile:
        reader = csv.reader(csvfile, delimiter=",")
        for row in reader:
            areas = row

    areas = [float(area) for area in areas]

    fluxes_times_area = []

    for flux in fluxes:
        sum = 0
        for i in range(len(flux)):
            sum += flux[i] * 100
        fluxes_times_area.append(sum)

    energies = []
    for time, nodes_temperatures in temperatures.items():
        energy = 0
        for i, t in nodes_temperatures.items():
            energy += t * 900 * 2700 * 0.05 * areas[i]
        energies.append(energy)

    energy_diff = []
    for i in range(1, len(energies)):
        e1 = energies[i - 1]
        e2 = energies[i]
        e = e2 - e1
        energy_diff.append(e)

    templates.template_style()
    fig, ax = plt.subplots()
    ax.plot([e - f for e, f in zip(energy_diff, fluxes_times_area[1:])])
    templates.template_plot(
        ax, "Time (s)", "Energy difference (J)", "Energy difference over time"
    )
    templates.template_save_multiple_images([fig], "energy", ["energy_diff"])
