import subprocess
import os
import timeit
from datetime import timedelta, datetime
import sys
import math


def decompose_time(total_seconds):
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return hours, minutes, seconds


def run_benchmark(folder):
    preprocessor = ["python3", "../standalone-raytrace/main.py", "process", folder]
    elapsed_time_preprocessor = timeit.timeit(
        lambda: subprocess.run(preprocessor), number=1
    )

    solver_implicit = ["../opencl/target/release/opencl", folder, "Implicit"]
    elapsed_time_implicit = timeit.timeit(
        lambda: subprocess.run(solver_implicit), number=1
    )

    wd = os.getcwd()
    os.chdir("../opencl")

    solver_gpu = ["target/release/opencl", folder, "GPU"]
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


def find_benchmarks(amount=math.inf):
    cwd = os.getcwd()

    folders = [
        cwd + "/" + x for x in sorted(next(os.walk(cwd))[1], key=lambda x: int(x))
    ]
    for folder in folders:
        if amount > 0:
            run_benchmark(folder)
            amount -= 1


def main():
    if len(sys.argv) == 1:
        find_benchmarks()
    else:
        try:
            amount = int(sys.argv[1])
            if amount > 0:
                find_benchmarks(amount)
        except:
            print("Incorrect number of tests to run")


if __name__ == "__main__":
    main()
