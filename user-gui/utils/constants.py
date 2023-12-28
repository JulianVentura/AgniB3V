ROUTES = {
    "landing": 0,
    "newProject": 1,
    "project": 2,
    "configuration": 3,
    "globalProperties": 4,
}

CONFIG_FILE_PATH = "./files/globalConfiguration.json"

RESULTS_SERIES="results/results.vtk.series"

DOCUMENTATION_URL="https://agnib3v.github.io/"

# Dict of global properties inputs
GLOBAL_PROPERTIES_INPUTS = {
    "albedo": {
        "label": "Albedo factor",
        "unit": "",
    },
    "earth_ir": {
        "label": "Earth IR",
        "unit": "W/m2",
    },
    "solar_constant": {
        "label": "Solar constant",
        "unit": "W/m2",
    },
    "initial_temperature": {
        "label": "Default initial temperature",
        "unit": "K",
    },
    "simulation_time": {
        "label": "Simulation time",
        "unit": "s",
    },
    "time_step": {
        "label": "Time step",
        "unit": "s",
    },
    "snap_period": {
        "label": "Snap period",
        "unit": "s",
    },
    "element_ray_amount": {
        "label": "Element ray amount",
        "unit": "",
    },
    "element_max_reflections_amount": {
        "label": "Element max reflections amount",
        "unit": "",
    },
    "earth_ray_amount": {
        "label": "Earth ray amount",
        "unit": "",
    },
    "orbit_divisions": {
        "label": "Orbit divisions",
        "unit": "",
    },
}
