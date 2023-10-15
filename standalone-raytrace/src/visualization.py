import trimesh
import numpy as np

def view_material(mesh, materials):
    colors = []
    mesh.unmerge_vertices()
    for triangle_index in range(len(mesh.triangles)):
        material = materials.get_material_props(triangle_index)
        colors.append(material["color"])

    mesh.visual.vertex_colors = None
    mesh.visual.face_colors = colors
    scene = trimesh.Scene([mesh])
    scene.show()

def view_raycast(mesh, emmiting_element_idx, ray_origins, ray_directions):
    mesh.unmerge_vertices()
    mesh.visual.vertex_colors = None
    mesh.visual.face_colors = [[255,0,0,255] if emmiting_element_idx == i else [255,255,255,255] for i in range(len(mesh.triangles))]
    rays = trimesh.load_path(np.hstack((ray_origins,ray_origins + ray_directions)).reshape(-1, 2, 3))
    scene = trimesh.Scene([mesh, rays])
    scene.show()

def view_element_view_factors(mesh, emmiting_element_idx, element_view_factors):
    mesh.unmerge_vertices()
    mesh.visual.vertex_colors = None
    mesh.visual.face_colors = [[int(255*element_view_factors[i]*10),0,0,255] if emmiting_element_idx != i else [0,255,0,255] for i in range(len(mesh.triangles))]
    scene = trimesh.Scene([mesh])
    scene.show()

def view_other_view_factors(mesh, element_view_factors):
    mesh.unmerge_vertices()
    mesh.visual.vertex_colors = None
    mesh.visual.face_colors = [[int(255*element_view_factors[i]),0,0,255] for i in range(len(mesh.triangles))]
    scene = trimesh.Scene([mesh])
    scene.show()

def view_invisible_points(mesh, sun_direction, invisible_nodes):
    sun_ray = trimesh.load_path([mesh.center_mass, mesh.center_mass -10*sun_direction])
    sun_ray.colors = [[255,233,92,255]]
    point_cloud = trimesh.PointCloud(invisible_nodes)
    mesh.unmerge_vertices()
    scene = trimesh.Scene([mesh, point_cloud, sun_ray])
    scene.show()