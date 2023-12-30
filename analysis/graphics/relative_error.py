import matplotlib.pyplot as plt


def plot_relative_error(datax, datay, labels):
    transposed_data = list(map(list, zip(*datay)))
    fig, ax = plt.subplots()
    relative_errors = []
    for data in transposed_data:
        relative_error = []
        last_data = data[-1]
        for i in range(len(data) - 1):
            relative_error.append((data[i] - last_data) / last_data)
        relative_errors.append(relative_error)

    transposed_error = list(map(list, zip(*relative_errors)))
    for error in transposed_error:
        ax.plot(datax, error, label=labels.pop(0))
    return ax
