import numpy as np
import trimesh
from collections import Counter
from src import vtk_io, view_factors, visualization

def main():
	visualization.ENABLED = True

	mesh = vtk_io.load_vtk("./models/cube.vtk")
	node_sun_view_factors = view_factors.node_sun(mesh, [1,0,0], 0.05)
	print("Node-Sun view factors:", node_sun_view_factors)

	mesh = trimesh.load("./models/three_squares.glb", force='mesh') 
	surface_surface_view_factors = view_factors.surface_surface(mesh, 100)
	print("Surface-Surface view factors:\n", surface_surface_view_factors)

if __name__ == '__main__':
	main()
