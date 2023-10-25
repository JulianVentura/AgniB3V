# List of inputs
# Format is:
# attribute_name, label, unit, initial_value
# Attributes must be defined in the workbench
GLOBAL_PROPERTIES_INPUTS = [
    ("betaAngle", "Beta angle", "deg", 30.0),
    ("orbitHeight", "Orbit height", "km", 300.0),
    ("orbitalPeriod", "Orbital period", "s", 6000.0),
    ("albedo", "Albedo factor", "", 0.2),
    ("earthIR", "Earth IR", "W/m2", 225.0),
    ("solarConstant", "Solar constant", "W/m2", 1361.0),
    ("spaceTemperature", "Space temperature", "K", 4.0),
    ("initialTemperature", "Initial temperature", "K", 200.0),
    ("sunDirection", "Sun direction", "", "0,0,1"),
    ("earthDirection", "Earth direction", "", "0,0,-1"),
    ("internalEmission", "Internal emission", "W/m2", 0.0),
    ("timeStep", "Time step", "s", 60.0),
    ("snapTime", "Snap time", "s", 3600.0),
]
