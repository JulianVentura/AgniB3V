import trimesh
import numpy as np
import seaborn as sb
from . import utils

RESET = "\033[0m"
COLOR_BACKGROUND = [9, 10, 20]


def _get_color_escape(rgb_color):
    r, g, b = list(map(lambda c: int(c * 255), rgb_color))
    return "\033[{};2;{};{};{}m".format(38, r, g, b)


def _color_item_str(rbg_color):
    return _get_color_escape(rbg_color) + "██" + RESET


def view_material(mesh, props):
    print("REFERENCE:")
    palette = sb.color_palette("tab10", len(props.materials))
    for i in range(len(palette)):
        print(_color_item_str(palette[i]), props.materials[i]["name"])

    colors = []
    for element_id in range(utils.element_amount(mesh.triangles)):
        material_id = props.material_by_element[element_id]
        colors.append(palette[material_id])
    colors = np.array(colors)
    colors = np.vstack((colors, colors))
    mesh.faces = np.vstack((mesh.faces, np.fliplr(mesh.faces)))
    mesh.unmerge_vertices()
    mesh.visual.vertex_colors = None
    mesh.visual.face_colors = colors
    scene = trimesh.Scene([mesh])
    scene.show(background=COLOR_BACKGROUND, smooth=True)


def view_normal(mesh):
    print("REFERENCE:")
    palette = np.array([[63, 96, 181], [165, 48, 48]]) / 255
    print(_color_item_str(palette[0]), "+n")
    print(_color_item_str(palette[1]), "-n")

    mesh.faces = np.vstack((mesh.faces, np.fliplr(mesh.faces)))

    side_amount = utils.element_amount(mesh.triangles) // 2
    postiive_side_colors = np.broadcast_to(palette[0], (side_amount, 3))
    negative_side_colors = np.broadcast_to(palette[1], (side_amount, 3))
    side_colors = np.vstack((postiive_side_colors, negative_side_colors))

    mesh.unmerge_vertices()
    mesh.visual.vertex_colors = None
    mesh.visual.face_colors = side_colors
    scene = trimesh.Scene([mesh])
    scene.show(background=COLOR_BACKGROUND, smooth=True)


def view_raycast(mesh, emmiting_element_idx, ray_origins, ray_directions):
    mesh.unmerge_vertices()
    mesh.visual.vertex_colors = None
    mesh.visual.face_colors = [
        [255, 0, 0, 255] if emmiting_element_idx == i else [255, 255, 255, 255]
        for i in range(len(mesh.triangles))
    ]
    rays = trimesh.load_path(
        np.hstack((ray_origins, ray_origins + ray_directions)).reshape(-1, 2, 3)
    )
    scene = trimesh.Scene([mesh, rays])
    scene.show()


def view_element_view_factors(mesh, emmiting_element_idx, element_view_factors):
    mesh.unmerge_vertices()
    mesh.visual.vertex_colors = None
    mesh.visual.face_colors = [
        [int(255 * element_view_factors[i] * 10), 0, 0, 255]
        if emmiting_element_idx != i
        else [0, 255, 0, 255]
        for i in range(len(mesh.triangles))
    ]
    scene = trimesh.Scene([mesh])
    scene.show()


def view_other_view_factors(mesh, element_view_factors):
    mesh.unmerge_vertices()
    mesh.visual.vertex_colors = None
    mesh.visual.face_colors = [
        [int(255 * element_view_factors[i]), 0, 0, 255]
        for i in range(len(mesh.triangles))
    ]
    scene = trimesh.Scene([mesh])
    scene.show()


def view_invisible_points(mesh, sun_direction, invisible_nodes):
    sun_ray = trimesh.load_path(
        [mesh.center_mass, mesh.center_mass - 10 * sun_direction]
    )
    sun_ray.colors = [[255, 233, 92, 255]]
    point_cloud = trimesh.PointCloud(invisible_nodes)
    mesh.unmerge_vertices()
    scene = trimesh.Scene([mesh, point_cloud, sun_ray])
    scene.show()
