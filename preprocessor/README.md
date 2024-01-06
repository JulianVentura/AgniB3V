# Preprocessor



## Installation

Install python 3.10.12 and run the following command:

```sh
pip install -r requirements.txt
```



## Usage



**View factor processing**

```sh
python main.py process /files/directory
```

Required files: mesh.vtk, properties.json, ReportFile.txt, EclipseLocator.txt.



**Mesh normals direction display**

```
python main.py viewn /files/directory
```

Required files: mesh.vtk



**Assigned materials display**

```sh
python main.py viewm /files/directory
```

Required files: mesh.vtk, properties.json



### Test

Install pytest:

```sh
pip install pytest
```

Execute tests:

```sh
pytest
```
