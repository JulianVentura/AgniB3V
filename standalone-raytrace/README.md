# Standalone-raytrace

### Installation

Install python 3.10.12 and run the following command.

```sh
pip install -r requirements.txt
```

### Execution

Processing of view factors:

```sh
main process mesh_file_path properties_file_path output_path sun_direction
```

Viewing mesh assigned materials:

```sh
main viewm mesh_file_path properties_file_path
```

Requires a color property per material on properties_file_path.

Viewing "view factors" corresponding to element_id:

```sh
main viewvf mesh_file_path properties_file_path element_id
```

### Tests

Install pytest:

```sh
pip install pytest
```

And run the following command:

```sh
pytest
```
