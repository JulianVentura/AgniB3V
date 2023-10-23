import sys
import json
from src import properties_atlas, vtk_io, view_factors, visualization

def op_process_view_factors(argv):
	if(argv[1] != 'process' or len(argv) != 7):
		return False

	calle_name, op, mesh_file_path, properties_file_path, output_path, sun_direction, internal_emission = sys.argv
	internal_emission = internal_emission == "true"
	mesh = vtk_io.load_vtk(mesh_file_path)

	sun_direction = list(map(float, sun_direction.strip("[]").split(",")))
	props = properties_atlas.PropertiesAtlas(len(mesh.triangles), properties_file_path)

	element_sun_view_factors = view_factors.element_sun(mesh, sun_direction, 0.05),
	element_element_view_factors = view_factors.element_element(mesh, props, 500,3,0.1,internal_emission)
	element_earth_view_factors = view_factors.element_earth(mesh, list(map(lambda x: -x, sun_direction)), 200, 0.05)
	
	props.add_prop("view_factors", {
		"sun": list(element_sun_view_factors),
		"earth": list(element_earth_view_factors),
		"elements": list(map(list, element_element_view_factors))
    })
	props.dump(output_path)

	return True

def op_visualize_view_factors(argv):
	if(argv[1] != 'viewvf' or len(argv) != 5):
		return False
	
	calle_name, op, mesh_file_path, properties_file_path, element_id = sys.argv
	mesh = vtk_io.load_vtk(mesh_file_path)
	element_id = int(element_id)
	material_file = open(properties_file_path)
	material_json = json.load(material_file)

	#visualization.view_other_view_factors(mesh, material_json["view_factors"]["earth"])
	visualization.view_element_view_factors(mesh, element_id, material_json["view_factors"]["elements"][element_id])

	return True

def op_visualize_material(argv):
	if(argv[1] != 'viewm' or len(argv) != 4):
		return False
	calle_name, op, mesh_file_path, properties_file_path = sys.argv
	
	mesh = vtk_io.load_vtk(mesh_file_path)
	props = properties_atlas.PropertiesAtlas(len(mesh.triangles), properties_file_path)
	visualization.view_material(mesh, props)

	return True

def op_default(argv):
	print("Use:")
	print(f"{argv[0]} process mesh_file_path properties_file_path output_path sun_direction")
	print(f"{argv[0]} viewvf mesh_file_path properties_file_path element_id")
	print(f"{argv[0]} viewm mesh_file_path properties_file_path")

	return True

def main():
	ops = [op_process_view_factors, op_visualize_view_factors, op_visualize_material, op_default]
	for op in ops:
		if(op(sys.argv)):
			return

if __name__ == '__main__':
	main()
