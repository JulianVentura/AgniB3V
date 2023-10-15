# Standalone-raytrace

### Installation

Install python and run the following commands.

```sh
pip install meshio
pip install numpy
pip install trimesh[easy]
```

### Execution

Processing of view factors:
```sh
main process mesh_file_path properties_file_path output_path sun_direction
``

Viewing mesh assigned materials:
```sh
main viewm mesh_file_path properties_file_path
``
Requires a color property per material on properties_file_path.

Viewing "view factors" corresponding to element_id:
```sh
main viewvf mesh_file_path properties_file_path element_id
``
