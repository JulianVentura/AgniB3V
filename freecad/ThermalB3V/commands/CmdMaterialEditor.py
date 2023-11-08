import FreeCAD
from ui.DialogMaterialEditor import DialogMaterialEditor
from public.utils import iconPath
from constants import CONFIG_GROUP

class CmdMaterialEditor:
    def __init__(self, workbench):
        self.workbench = workbench

    def Activated(self):
        """
        Executed when the command is activated
        """
        form = DialogMaterialEditor(self.workbench)
        form.exec_()

    def IsActive(self):
        """
        Show command as active if there is an active document
        and config exists
        """
        return bool(FreeCAD.activeDocument()) and bool(FreeCAD.activeDocument().getObject(CONFIG_GROUP))
        
    def GetResources(self):
        return {
            'MenuText': ("Edit Materials"),
            'ToolTip': ("Edit Materials"),
            'Pixmap': iconPath("Material.svg"),
        }
