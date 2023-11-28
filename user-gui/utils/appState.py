class AppStateMeta(type):
    _instance = None

    def __call__(cls, *args, **kwargs):
        if not cls._instance:
            instance = super().__call__(*args, **kwargs)
            cls._instance = instance
        return cls._instance

class AppState(metaclass=AppStateMeta):
    def __init__(self):
        self.projectDirectory = None

    def openProject(self, directory):
        self.projectDirectory = directory
