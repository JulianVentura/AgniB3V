import json
from .constants import CONFIG_FILE_PATH

class GlobalConfiguration():
    def __init__(self):
        with open(CONFIG_FILE_PATH) as json_file:
            self.config = json.load(json_file)

    def getExecutable(self, executableName: str) -> str:
        """
        Receives an executable name and returns the path to the executable.
        """
        return self.config["executables"][executableName]

    def getSolverConfiguration(self, config: str) -> str:
        """
        Receives a solver config name and returns the solver configuration.
        """
        return self.config["solver"][config]
    
    def updateConfig(self, config: dict):
        """
        Receives a config and updates the global configuration file.
        """
        self.config = config
        with open(CONFIG_FILE_PATH, "w") as json_file:
            json.dump(self.config, json_file, indent=4)