import trimesh
from src import properties_atlas, vtk_io, view_factors, visualization

def main():
	visualization.ENABLED = True

	mesh = vtk_io.load_vtk("./models/cube.vtk")
	node_sun_view_factors = view_factors.node_sun(mesh, [1,0,0], 0.05)
	print("Node-Sun view factors:", node_sun_view_factors)

	props = properties_atlas.PropertiesAtlas(len(mesh.triangles), './models/cube_materials.json')
	print(len(mesh.triangles))
	visualization.view_material(mesh, props)

	mesh = trimesh.load("./models/three_squares.vtk", force='mesh')
	surface_surface_view_factors = view_factors.surface_surface(mesh, 100)
	print("Surface-Surface view factors:\n", surface_surface_view_factors)
    
	props.add_prop("view_factors", {
		"node_sun": list(node_sun_view_factors),
		"surface_surface": list(map(list, surface_surface_view_factors))
    })
	props.dump("output.json")

if __name__ == '__main__':
	main()
