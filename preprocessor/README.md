# Preprocessor



## Installation

Install Python 3.10.  The recommended way is  [Pyenv](https://github.com/pyenv/pyenv)

```bash
pyenv install 3.10 -s
pyenv local 3.10
```
Install requirements:

```bash
pip install -r requirements.txt
```



## Usage



**View factor processing**

```bash
python main.py process <directory-path>
```

Required files: mesh.vtk, properties.json, ReportFile.txt, EclipseLocator.txt.



**Mesh normals direction display**

```bash
python main.py viewn <directory-path>
```

Required files: mesh.vtk



**Assigned materials display**

```bash
python main.py viewm <directory-path>
```

Required files: mesh.vtk, properties.json



### Test

Install pytest:

```bash
pip install pytest
```

Execute tests:

```bash
pytest
```
