import FreeCAD
from ui.DialogSelectDocument import DialogSelectDocument
from public.utils import iconPath

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
        Active only when no document is active and saved (i.e. has FileName)
        """
        return not (bool(FreeCAD.activeDocument()) and bool(FreeCAD.activeDocument().FileName))
        
    def GetResources(self):
        return {
            'MenuText': ("Select Document"),
            'ToolTip': ("Select Document"),
            'Pixmap': iconPath("Save.svg"),
        }
