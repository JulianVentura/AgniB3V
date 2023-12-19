import numpy as np
import matplotlib.pyplot as plt


def plot_std_deviation(datax, datay):
    transposed_data = list(map(list, zip(*datay)))
    std_deviation = [np.std(temp) for temp in transposed_data]
    fig, ax = plt.subplots()
    ax.plot(datax, std_deviation)
    return ax
