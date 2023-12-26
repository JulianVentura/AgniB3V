#!<virtualenv_dir>/bin/python

import os
import matplotlib.pyplot as plt
import csv
import numpy as np
import templates

TIMING_FOLDER = "timings"


def _plot_benchmarks(title, element_amount_dict, results_dict):
    templates.template_style()
    fig, ax = plt.subplots()
    for name, results in results_dict.items():
        ax.plot(element_amount_dict[name], results, label=name, marker="s")
    templates.template_plot(
        ax,
        "Number of Elements",
        "Execution Time (s)",
        title,
    )

    return ax, f"timings_{title}"


def _plot_cpu_vs_gpu(
    title, element_amount_dict, elapsed_time_cpu_dict, elapsed_time_gpu_dict
):
    templates.template_style()
    fig, ax = plt.subplots()
    for name, results in elapsed_time_cpu_dict.items():
        ax.plot(element_amount_dict[name], results, label="CPU", marker="s")
        ax.plot(
            element_amount_dict[name],
            elapsed_time_gpu_dict[name],
            label="GPU",
            marker="s",
        )
        break
    templates.template_plot(
        ax,
        "Number of Elements",
        "Execution Time (s)",
        title,
    )

    return ax, "timings_cpu_vs_gpu"


def plot():
    cwd = os.getcwd()
    benchmarks_files = os.listdir(f"{cwd}/sources/{TIMING_FOLDER}")
    element_amounts_dict = {}
    elapsed_time_preprocessor_dict = {}
    elapsed_time_cpu_dict = {}
    elapsed_time_gpu_dict = {}
    elapsed_time_total_dict_gpu = {}
    elapsed_time_total_dict_cpu = {}

    for benchmarks_file in benchmarks_files:
        benchmark_name = benchmarks_file[:-4]
        with open(f"{cwd}/sources/{TIMING_FOLDER}/{benchmarks_file}") as csvfile:
            spamreader = csv.reader(csvfile, delimiter=",", quotechar='"')
            element_amounts = []
            elapsed_time_preprocessor = []
            elapsed_time_implicit = []
            elapsed_time_gpu = []
            for row in spamreader:
                a, p, i, g = row
                element_amounts.append(float(a))
                elapsed_time_preprocessor.append(float(p))
                elapsed_time_implicit.append(float(i))
                elapsed_time_gpu.append(float(g))

            element_amounts_dict[benchmark_name] = element_amounts
            elapsed_time_preprocessor_dict[benchmark_name] = elapsed_time_preprocessor
            elapsed_time_cpu_dict[benchmark_name] = elapsed_time_implicit
            elapsed_time_gpu_dict[benchmark_name] = elapsed_time_gpu
            elapsed_time_total_dict_gpu[benchmark_name] = np.array(
                elapsed_time_preprocessor
            ) + np.array(elapsed_time_gpu)
            elapsed_time_total_dict_cpu[benchmark_name] = np.array(
                elapsed_time_preprocessor
            ) + np.array(elapsed_time_implicit)

    graphs = []
    names = []
    ax, name = _plot_benchmarks(
        "Preprocesador", element_amounts_dict, elapsed_time_preprocessor_dict
    )
    graphs.append(ax)
    names.append(name)
    ax, name = _plot_benchmarks(
        "Solver CPU", element_amounts_dict, elapsed_time_cpu_dict
    )
    graphs.append(ax)
    names.append(name)
    ax, name = _plot_benchmarks(
        "Solver GPU", element_amounts_dict, elapsed_time_gpu_dict
    )
    graphs.append(ax)
    names.append(name)
    ax, name = _plot_benchmarks(
        "Total GPU", element_amounts_dict, elapsed_time_total_dict_gpu
    )
    graphs.append(ax)
    names.append(name)
    ax, name = _plot_benchmarks(
        "Total CPU", element_amounts_dict, elapsed_time_total_dict_cpu
    )
    graphs.append(ax)
    names.append(name)

    ax, name = _plot_cpu_vs_gpu(
        "CPU vs GPU", element_amounts_dict, elapsed_time_cpu_dict, elapsed_time_gpu_dict
    )
    graphs.append(ax)
    names.append(name)

    templates.template_save_multiple_images(graphs, "timings", names)
