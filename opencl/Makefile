vtk_path ?= models/mesh.vtk
json_path ?= models/mesh_res.json
results_name ?= mesh_vtk
results_path ?= models

build:
	cargo build --release
	./target/release/opencl $(vtk_path) $(json_path) $(results_path) $(results_name)
