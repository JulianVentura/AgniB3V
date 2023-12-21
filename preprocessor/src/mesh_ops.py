import trimesh
from . import vector_math

def look_at(mesh, direction):
    """
    Receives a mesh and a direction in space and rotates the mesh
    so that mesh local z+ matches direction.
    """
    _, phi, theta = vector_math.spherical_cordinates(direction)
    rot_matrix = trimesh.transformations.rotation_matrix(theta, [1, 0, 0])
    mesh.apply_transform(rot_matrix)
    rot_matrix = trimesh.transformations.rotation_matrix(phi, [0, 0, 1])
    mesh.apply_transform(rot_matrix)

def element_amount(mesh):
    """
    Given a mesh, returns its elements amount.
    """
    return mesh.triangles.size // 9