import FreeCAD
from public.utils import iconPath
from constants import CONFIG_GROUP

class CmdInitializeProperties:
    def __init__(self, workbench):
        self.workbench = workbench

    def Activated(self):
        """
        Executed when the command is activated
        """
        self.workbench.saveWorkbenchSettings()

    def IsActive(self):
        """
        Function to check if the command is active
        """
        isActiveDocument = bool(FreeCAD.activeDocument())
        configExists = bool(FreeCAD.activeDocument().getObject(CONFIG_GROUP))
        return isActiveDocument and not configExists
        
    def GetResources(self):
        return {
            'MenuText': ("Initialize Properties"),
            'ToolTip': ("Initialize Properties"),
            'Pixmap': iconPath("DbInit.svg"),
        }
