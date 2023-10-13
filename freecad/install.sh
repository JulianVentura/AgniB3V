#!/bin/sh
echo "Installing Thermal Analysis workbench..."
sudo rm -rf "$HOME/.local/share/FreeCAD/Mod/ThermalB3V"
sudo mkdir -p "$HOME/.local/share/FreeCAD/Mod"
sudo cp -r "$(pwd)/ThermalB3V" "$HOME/.local/share/FreeCAD/Mod/ThermalB3V"
echo "Workbench installed"

