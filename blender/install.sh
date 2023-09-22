#!/bin/sh
echo "Installing thermal plugin to Blender user folder..."

blender_version=$(ls /usr/share/blender/ | grep -E '^[0-9]+\.[0-9]+')

if [ -n "$blender_version" ]; then
    sudo rm -rf "/usr/share/blender/$blender_version/scripts/startup/satellite_thermal_analysis"
    sudo cp -r "$(pwd)/satellite_thermal_analysis" "/usr/share/blender/$blender_version/scripts/startup"
    echo "Plugin installed for Blender $blender_version"
else
    echo "Blender is not installed in the expected directory."
fi

