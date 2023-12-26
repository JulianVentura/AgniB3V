import matplotlib.pyplot as plt


def plot_cuadratic_error(datax, datay, labels):
    transposed_data = list(map(list, zip(*datay)))
    fig, ax = plt.subplots()
    cuadratic_errors = []
    for data in transposed_data:
        cuadratic_error = []
        last_data = data[-1]
        for i in range(len(data) - 1):
            cuadratic_error.append((data[i] - last_data) ** 2)
        cuadratic_errors.append(cuadratic_error)

    transposed_error = list(map(list, zip(*cuadratic_errors)))
    for error in transposed_error:
        ax.plot(datax, error, label=labels.pop(0))
    return ax
