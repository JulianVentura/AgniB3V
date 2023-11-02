import FreeCAD
from ui.DialogSelectDocument import DialogSelectDocument
from public.utils import iconPath
from constants import CONFIG_GROUP

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
        Active only when no document is active and config exists
        """
        return not (bool(FreeCAD.activeDocument()) and bool(FreeCAD.activeDocument().getObject(CONFIG_GROUP)))
        
    def GetResources(self):
        return {
            'MenuText': ("Select Document"),
            'ToolTip': ("Select Document"),
            'Pixmap': iconPath("Save.svg"),
        }
