import FreeCAD
from ui.DialogGlobalProperties import DialogGlobalProperties
from public.utils import iconPath
from constants import CONFIG_GROUP

class CmdOpenGlobalProperties:
    def __init__(self, workbench):
        self.workbench = workbench

    def Activated(self):
        """
        Executed when the command is activated
        """
        form = DialogGlobalProperties(self.workbench)
        form.exec_()

    def IsActive(self):
        """
        Function to check if the command is active
        """
        isActiveDocument = bool(FreeCAD.activeDocument())
        configExists = bool(FreeCAD.activeDocument().getObject(CONFIG_GROUP))
        return isActiveDocument and configExists
        
    def GetResources(self):
        return {
            'MenuText': ("Set Global Properties"),
            'ToolTip': ("Set Global Properties"),
            'Pixmap': iconPath("Settings.svg"),
        }
