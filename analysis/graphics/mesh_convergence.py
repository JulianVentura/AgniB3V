import convergence


def plot():
    files = ["622", "1178", "2841", "5539"]  # Meshes to compare
    points = [
        (158, 244, 417, 608),
        (155, 241, 408, 579),
        (248, 438, 963, 1745),
    ]  # Ids of points to compare for each model
    titles = [
        "Center of Panel",
        "Hidden Pyramid",
        "Interior Face",
    ]  # Titles for each point

    source = "mesh_convergence"

    label_generator = lambda x: f"{x} elements"

    type = "Mesh"

    unit = "elements"

    convergence.plot_convergence(
        source, files, points, titles, label_generator, type, unit
    )
