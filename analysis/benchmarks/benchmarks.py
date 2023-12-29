import subprocess
import os
import timeit
from datetime import timedelta, datetime
import sys
import math
import matplotlib.pyplot as plt
import csv
import numpy as np

TIMING_FOLDER = "timings"
CURRENT_USER = os.environ["USER"]
TIMING_FILE_PATH = f"{TIMING_FOLDER}/{CURRENT_USER}.csv"
PREPROCESSOR_PATH = "../../preprocessor"
SOLVER_PATH="../../solver"

def decompose_time(total_seconds):
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return hours, minutes, seconds


def run_benchmark(folder):
    benchmark_elments_amount = folder.split("/")[-1]
    print(f"RUNNING {benchmark_elments_amount} ELEMENTS BENCHMARK ")
    print("PREPROCESSOR")
    preprocessor = ["python3", f"{PREPROCESSOR_PATH}/main.py", "process", folder]
    elapsed_time_preprocessor = timeit.timeit(
        lambda: subprocess.run(preprocessor), number=1
    )
    print("SOLVER CPU")
    solver_implicit = [f"{SOLVER_PATH}/target/release/solver", folder, "Implicit"]
    elapsed_time_implicit = timeit.timeit(
        lambda: subprocess.run(solver_implicit), number=1
    )

    print("SOLVER GPU")
    wd = os.getcwd()
    os.chdir(SOLVER_PATH)
    solver_gpu = [f"./target/release/solver", folder, "GPU"]
    elapsed_time_gpu = timeit.timeit(lambda: subprocess.run(solver_gpu), number=1)
    os.chdir(wd)

    preprocessor_time_decomposed = decompose_time(elapsed_time_preprocessor)
    implicit_time_decomposed = decompose_time(elapsed_time_implicit)
    gpu_time_decomposed = decompose_time(elapsed_time_gpu)

    preprocessor_str = f"{int(preprocessor_time_decomposed[0])} hs, {int(preprocessor_time_decomposed[1])} m, {preprocessor_time_decomposed[2]:.2f} s"
    implicit_str = f"{int(implicit_time_decomposed[0])} hs, {int(implicit_time_decomposed[1])} m, {implicit_time_decomposed[2]:.2f} s"
    gpu_str = f"{int(gpu_time_decomposed[0])} hs, {int(gpu_time_decomposed[1])} m, {gpu_time_decomposed[2]:.2f} s"
    now = datetime.now()
    timings = f"Date: {now} \nPreprocessor \n{preprocessor_str} \n\nImplicit \n{implicit_str} \n\nGPU \n{gpu_str}"
    with open(folder + "/timings.txt", "w") as file:
        file.write(timings)

    with open(TIMING_FILE_PATH, "a+") as file:
        file.write(
            f"{benchmark_elments_amount},{elapsed_time_preprocessor},{elapsed_time_implicit},{elapsed_time_gpu}\n"
        )


def find_benchmarks(specific_benchmark=None):
    cwd = os.getcwd()
    folders = [specific_benchmark]
    if not specific_benchmark:
        filtered_folders = [x[1] for x in os.walk(cwd)][0]
        filtered_folders.remove(TIMING_FOLDER)
        folders = [
            cwd + "/" + x for x in sorted(filtered_folders, key=lambda x: int(x))
        ]

    for folder in folders:
        run_benchmark(folder)


def _plot_benchmarks(title, element_amount_dict, results_dict):
    plt.title(title)
    plt.xlabel("Number of Elements", fontsize=12)
    plt.ylabel("Execution Time", fontsize=12)
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.style.use("ggplot")
    for name, results in results_dict.items():
        plt.plot(element_amount_dict[name], results, label=name, marker="s")
    plt.legend()
    plt.show()


def plot_benchmarks():
    print("PLOTTING BENCHMARKS")
    cwd = os.getcwd()
    benchmarks_files = os.listdir(f"{cwd}/{TIMING_FOLDER}")
    element_amounts_dict = {}
    elapsed_time_preprocessor_dict = {}
    elapsed_time_cpu_dict = {}
    elapsed_time_gpu_dict = {}
    elapsed_time_total_dict = {}

    for benchmarks_file in benchmarks_files:
        benchmark_name = benchmarks_file[:-4]
        with open(f"{cwd}/{TIMING_FOLDER}/{benchmarks_file}") as csvfile:
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
            elapsed_time_total_dict[benchmark_name] = np.array(
                elapsed_time_preprocessor
            ) + np.array(elapsed_time_gpu)

    _plot_benchmarks(
        "Preprocesador", element_amounts_dict, elapsed_time_preprocessor_dict
    )
    _plot_benchmarks("Solver CPU", element_amounts_dict, elapsed_time_cpu_dict)
    _plot_benchmarks("Solver GPU", element_amounts_dict, elapsed_time_gpu_dict)
    _plot_benchmarks("Total", element_amounts_dict, elapsed_time_total_dict)


def main():
    if not os.path.isdir(TIMING_FOLDER):
        os.mkdir(TIMING_FOLDER)

    if not os.path.exists(TIMING_FILE_PATH):
        if len(sys.argv) == 1:
            find_benchmarks()
        else:
            specific_benchmark = sys.argv[1]
            find_benchmarks(specific_benchmark)
    else:
        print("TIMINGS FILE FOUND - SKIPPING COMPUTATION")

    plot_benchmarks()


if __name__ == "__main__":
    main()
