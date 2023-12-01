from .globalConfiguration import GlobalConfiguration

class AppStateMeta(type):
    _instance = None

    def __call__(cls, *args, **kwargs):
        if not cls._instance:
            instance = super().__call__(*args, **kwargs)
            cls._instance = instance
        return cls._instance

class AppState(metaclass=AppStateMeta):
    def __init__(self):
        self.globalConfiguration = GlobalConfiguration()
        self.projectDirectory = None
        self.routes = []

    def openProject(self, directory):
        self.projectDirectory = directory

    def addRoute(self, route):
        self.routes.append(route)

    def resetRoutes(self):
        self.routes = []
    
    def popLastRoute(self) -> int:
        print(self.routes)
        if len(self.routes) == 0:
            return 0
        return self.routes.pop()

    def getGlobalConfiguration(self) -> dict:
        return self.globalConfiguration.config
    
    def setGlobalConfiguration(self, config):
        self.globalConfiguration.updateConfig(config)