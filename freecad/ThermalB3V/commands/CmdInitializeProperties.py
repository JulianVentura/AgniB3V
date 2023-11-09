import FreeCAD
from ui.DialogGlobalProperties import DialogGlobalProperties
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
        Show command as active if there is an active document
        but config does not exists
        """
        return bool(FreeCAD.activeDocument()) and not bool(FreeCAD.activeDocument().getObject(CONFIG_GROUP))
        
    def GetResources(self):
        return {
            'MenuText': ("Initialize properties"),
            'ToolTip': ("Initialize properties"),
            'Pixmap': iconPath("DbInit.svg"),
        }
