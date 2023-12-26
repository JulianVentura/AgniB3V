import matplotlib.pyplot as plt
import os


def template_style():
    plt.style.use("ggplot")


def template_plot(graph, xlabel, ylabel, title):
    graph.set_xlabel(xlabel, fontsize=12)
    graph.set_ylabel(ylabel, fontsize=12)
    graph.set_title(title, fontsize=14)
    graph.grid(
        True, linestyle="--", alpha=0.5
    )  # Adding grid lines with specific style and transparency
    graph.tick_params(axis="x", rotation=45)
    graph.figure.tight_layout()
    graph.legend()


def template_save_image(graph, name):
    graph.figure.savefig(name + ".png", bbox_inches="tight")


def template_save_multiple_images(graphs, directory, names):
    if not os.path.exists("./images/" + directory):
        os.makedirs("./images/" + directory)
    for i in range(len(graphs)):
        template_save_image(graphs[i], "./images/" + directory + "/" + names[i])
