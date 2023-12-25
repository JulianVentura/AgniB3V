import FreeCAD
from ui.DialogSelectDocument import DialogSelectDocument
from public.utils import iconPath
from constants import CONFIG_GROUP

# TODO: maybe it wont be necessary anymore
class CmdSelectDocument:
    def __init__(self, workbench):
        self.workbench = workbench

    def Activated(self):
        """
        Executed when the command is activated
        """
        form = DialogSelectDocument(self.workbench)
        form.exec_()

    def IsActive(self):
        """
        Function to check if the command is active
        """
        activeDocument = bool(FreeCAD.activeDocument())
        return not activeDocument
        
    def GetResources(self):
        return {
            'MenuText': ("Select Document"),
            'ToolTip': ("Select Document"),
            'Pixmap': iconPath("Save.svg"),
        }
