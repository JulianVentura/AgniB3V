import trimesh
from src import properties_atlas, vtk_io, view_factors, visualization

def main():
	visualization.ENABLED = True

	mesh = vtk_io.load_vtk("./models/cube.vtk")
	point_sun_view_factors = view_factors.point_sun(mesh, [1,0,0], 0.05)
	print("Node-Sun view factors:", point_sun_view_factors)

	props = properties_atlas.PropertiesAtlas(len(mesh.triangles), './models/cube_materials.json')
	print(len(mesh.triangles))
	visualization.view_material(mesh, props)

	mesh = trimesh.load("./models/three_squares.vtk", force='mesh')
	element_element_view_factors = view_factors.element_element(mesh, 100)
	print("Element-Element view factors:\n", element_element_view_factors)
    
	props.add_prop("view_factors", {
		"sun": list(point_sun_view_factors),
		"elements": list(map(list, element_element_view_factors))
    })
	props.dump("output.json")

if __name__ == '__main__':
	main()
