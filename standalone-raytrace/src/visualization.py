import trimesh
import numpy as np

ENABLED = True

def view_raycast(mesh, emmiting_surface_idx, ray_origins, ray_directions):
    if not ENABLED:
        return
    mesh.unmerge_vertices()
    rays = trimesh.load_path(np.hstack((ray_origins,ray_origins + ray_directions)).reshape(-1, 2, 3))
    scene = trimesh.Scene([mesh, rays])
    scene.show()
	
def view_invisible_nodes(mesh, sun_direction, node_invisibility):
    if not ENABLED:
        return
    invisible_nodes = np.arange(len(mesh.vertices))[node_invisibility]
    sun_ray = trimesh.load_path([mesh.center_mass, mesh.center_mass -10*sun_direction])
    sun_ray.colors = [[255,233,92,255]]
    point_cloud = trimesh.PointCloud(mesh.vertices[invisible_nodes])
    mesh.unmerge_vertices()
    scene = trimesh.Scene([mesh, point_cloud, sun_ray])
    scene.show()