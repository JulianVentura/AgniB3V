#!/bin/sh
echo "Installing Thermal Analysis workbench development version..."
sudo rm -rf "$HOME/.local/share/FreeCAD/Mod/ThermalB3V"
sudo mkdir -p "$HOME/.local/share/FreeCAD/Mod"
sudo ln -sf "$(pwd)/ThermalB3V" "$HOME/.local/share/FreeCAD/Mod/ThermalB3V"
echo "Workbench installed"

