# Blender Thermal Analysis Plugin

### Installation

If you are on a unix machine, run the `install.sh` script which will copy the _satellite_thermal_analysis_ plugin to the Blender's folder located under /usr

You can execute the script under the current folder like so:

```sh
./install.sh
```

If you want to manually install the plugin, then you will have to copy the folder _satellite_thermal_analysis_ under the _/usr/blender/{BLENDER_VERSION}/scripts/startup_ folder, given your Blender version.

### Development

There is a shorcut if you are going to modify the satellite plugin.
You can execute the `devel.sh` script which will create a symlink of the satellite plugin from the current folder to the Blender's folder located under _/usr_

You can execute the script under the current folder like so:

```sh
./devel.sh
```

If you don't want to create a symlink, then you can install the plugin on every modification you make.
