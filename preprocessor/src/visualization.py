import trimesh
import numpy as np
import seaborn as sb
from . import mesh_ops

RESET = "\033[0m"
BACKGROUND_COLOR = np.array([9, 10, 20]) / 255


def _get_color_escape(rgb_color):
    r, g, b = list(map(lambda c: int(c * 255), rgb_color))
    return "\033[{};2;{};{};{}m".format(38, r, g, b)


def _color_item_str(rbg_color):
    return _get_color_escape(rbg_color) + "██" + RESET


def view_material(mesh, props):
    """
    Receives a mesh, adds opposite side faces inplace and colors them
    according to the element material. Pallete is generated automatically.
    """
    print("REFERENCE:")
    palette = sb.color_palette("tab10", len(props.materials))
    for i in range(len(palette)):
        print(_color_item_str(palette[i]), props.materials[i]["name"])

    colors = []
    for element_id in range(mesh_ops.element_amount(mesh)):
        material_id = props.material_by_element[element_id]
        colors.append(palette[material_id])
    colors = np.array(colors)
    colors = np.vstack((colors, colors))

    mesh.faces = np.vstack((mesh.faces, np.fliplr(mesh.faces)))
    mesh.unmerge_vertices()
    mesh.visual.vertex_colors = None
    mesh.visual.face_colors = colors
    scene = trimesh.Scene([mesh])
    scene.show(background=BACKGROUND_COLOR, smooth=True)


def view_normal(mesh):
    """
    Receives a mesh, adds opposite side faces inplace and colors them
    according to the element normals orientation.
    """
    print("REFERENCE:")
    POSITIVE_COLOR = np.array([63, 96, 181]) / 255
    NEGATIVE_COLOR = np.array([165, 48, 48]) / 255
    print(_color_item_str(POSITIVE_COLOR), "+n")
    print(_color_item_str(NEGATIVE_COLOR), "-n")

    mesh.faces = np.vstack((mesh.faces, np.fliplr(mesh.faces)))

    side_amount = mesh_ops.element_amount(mesh) // 2
    postiive_side_colors = np.broadcast_to(POSITIVE_COLOR, (side_amount, 3))
    negative_side_colors = np.broadcast_to(NEGATIVE_COLOR, (side_amount, 3))
    side_colors = np.vstack((postiive_side_colors, negative_side_colors))

    mesh.unmerge_vertices()
    mesh.visual.vertex_colors = None
    mesh.visual.face_colors = side_colors
    scene = trimesh.Scene([mesh])
    scene.show(background=BACKGROUND_COLOR, smooth=True)


def view_raycast(ray_origins, ray_directions, mesh=None, emmiting_element_id=-1):
    """
    Receives ray origins and directions and displays them in 3D space.
    Optionally it can show the mesh and color the element from which rays
    are being cast.
    """
    RAY_COLOR = np.array([232, 193, 112])
    OTHER_ELEMENTS_COLOR = np.array([235, 237, 233])
    EMMITING_ELEMENT_COLOR = np.array([70, 130, 50])

    rays = trimesh.load_path(
        np.hstack((ray_origins, ray_origins + ray_directions)).reshape(-1, 2, 3)
    )
    rays.colors = np.broadcast_to(RAY_COLOR, (ray_origins.size // 3, 3))
    if mesh:
        mesh.unmerge_vertices()
        mesh.visual.vertex_colors = None
        mesh.visual.face_colors = [
            EMMITING_ELEMENT_COLOR
            if element_id == emmiting_element_id
            else OTHER_ELEMENTS_COLOR
            for element_id in range(mesh_ops.element_amount(mesh))
        ]
        scene = trimesh.Scene([mesh, rays])
    else:
        scene = trimesh.Scene([rays])

    scene.show(background=BACKGROUND_COLOR, smooth=True)
