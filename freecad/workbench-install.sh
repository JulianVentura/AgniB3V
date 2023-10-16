#!/bin/sh
sudo echo "Installing Thermal Analysis workbench"

echo "Checking FreeCAD installation directory"

freecad_dir1="$HOME/.local/share/FreeCAD"
freecad_dir2="$HOME/.var/app/org.freecadweb.FreeCAD/data/FreeCAD"

if [ -d "$freecad_dir1" ]; then
    freecad_directory="$freecad_dir1"
elif [ -d "$freecad_dir2" ]; then
    freecad_directory="$freecad_dir2"
else
    echo "FreeCAD is not installed in your system"
    exit 1
fi

plugin_name="ThermalB3V"
plugin_dir="${freecad_directory}/Mod/${plugin_name}"


sudo rm -rf "${plugin_dir}"
sudo mkdir -p "${freecad_directory}/Mod"
sudo cp -r "$(pwd)/${plugin_name}" "${plugin_dir}"

echo "Installation directory: ${plugin_dir}"

echo "${plugin_name} plugin installed sucessfully"
