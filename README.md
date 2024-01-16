

<p align="center">
    <img src="./user-gui/public/icons/agni.png" width=256>
</p>
<p align="center">
    <font color="#9A0C0C" size=5><i>Parallelized Satellite Thermal Analysis System</i></font>
</p>
 

**This is the code repository of AGNI B3V. For install instructions, user/technical manuals and benchmarks  visit the website: https://agnib3v.github.io/**



## Introduction

Agni B3V is an all encompassing solution for modeling, simulating and interpreting thermal phenomena affecting satellites in circular orbits and sun pointing aptitudes. It currently includes tools capable of:

* Building satellite structure meshes through primitives union or individual node placement and connection.
* Automatically remeshing models to improve FEM results.
* Assigning different materials and conditions to separate parts of the model.
* Configuring desired orbit and constants such as earth ir emission, albedo and sun intensity.
* Estimating view factors and energy exchange between elements and between elements and other celestial bodies.
* Simulating second by second temperature modification in an specified interval of time and orbit.
* Postprocessing results and extracting relevant data and graphs.



## Authors

This system was developed in the context of the professional task for "Universidad de Buenos Aires" by:

Barreneche Franco  (fbarreneche@fi.uba.ar)

Belinche Gianluca (gbelinche@fi.uba.ar) 

Botta Guido (gbotta@fi.uba.ar)

Ventura Julian (jventura@fi.uba.ar)



## Building from source

A convenient installer is provided in the [user manual](https://agnib3v.github.io/user_manual/installation/installation.html).

Alternatively, each tool install and basic usage is described in its respective folders README.

It is possible to install all required python modules from the root folder:

```bash
pip install -r requirements.txt
```

To be able to access all functions from the user GUI, install third party software as described in the following section.



## Installing third party software

All commands must be run from the root folder.



### FreeCAD  + Agni Workbench

#### Install FreeCAD

```bash
curl -L -o FreeCAD 'https://github.com/FreeCAD/FreeCAD/releases/download/0.21.1/FreeCAD_0.21.1-Linux-x86_64.AppImage'
chmod +x FreeCAD
mkdir _FreeCAD
mv FreeCAD ./_FreeCAD
mv _FreeCAD FreeCAD
```

#### Install Gmsh

```bash
curl -L -o gmsh.tgz "https://gmsh.info/bin/Linux/gmsh-4.12.0-Linux64.tgz"
tar -xf gmsh.tgz
sudo mv -f gmsh-4.12.0-Linux64/bin/gmsh /usr/bin 
rm -rf gmsh-4.12.0-Linux64
rm -rf gmsh.tgz
```



#### Install Agni Workbench

Install for the current user:

```bash
export FREECAD_DIRECTORY="~/.local/share/FreeCAD"
mkdir -p "${FREECAD_DIRECTORY}/Mod"
cp -r "freecad/Agni" "${FREECAD_DIRECTORY}/Mod/Agni"
```

Install to run with sudo privileges:

```bash
export FREECAD_DIRECTORY="/root/.local/share/FreeCAD"
sudo mkdir -p "${FREECAD_DIRECTORY}/Mod"
sudo cp -r "freecad/Agni" "${FREECAD_DIRECTORY}/Mod/Agni"
```



### GMAT

```bash
curl -L -o gmat.tar.gz "https://sourceforge.net/projects/gmat/files/GMAT/GMAT-R2022a/gmat-ubuntu-x64-R2022a.tar.gz/download"
tar -xf gmat.tar.gz
rm -rf gmat.tar.gz
```



### Paraview

```bash
curl -L -o paraview.tar.gz "https://www.paraview.org/paraview-downloads/download.php?submit=Download&version=v5.12&type=binary&os=Linux&downloadFile=ParaView-5.12.0-RC1-MPI-Linux-Python3.10-x86_64.tar.gz"
tar -xf paraview.tar.gz
mv ParaView*x86_64 ParaView
rm -rf paraview.tar.gz
```
