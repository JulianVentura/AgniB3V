import energy
import mesh_convergence


def generate_images():
    energy.plot()
    mesh_convergence.plot()


if __name__ == "__main__":
    generate_images()
