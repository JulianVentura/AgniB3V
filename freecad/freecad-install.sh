#!/bin/sh


executable_name="FreeCAD"

sudo echo "Installing FreeCAD v21.1 from repository"
curl -LJo ${executable_name} https://github.com/FreeCAD/FreeCAD-Bundle/releases/download/0.21.1/FreeCAD_0.21.1-2023-08-31-conda-Linux-x86_64-py310.AppImage
sudo mv ./${executable_name} /bin
echo "FreeCAD v21.1 installed sucessfully"
