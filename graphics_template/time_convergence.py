import convergence


def plot():
    files = ["100", "10", "1"]  # Times to compare
    points = [
        (417, 417, 417),
        (408, 408, 408),
        (963, 963, 963),
    ]  # Ids of points to compare for each model
    titles = [
        "Center of Panel",
        "Hidden Pyramid",
        "Interior Face",
    ]  # Titles for each point

    source = "time_convergence"

    label_generator = lambda x: f"{x} s"

    type = "Time"

    unit = "s"
    convergence.plot_convergence(
        source, files, points, titles, label_generator, type, unit
    )
