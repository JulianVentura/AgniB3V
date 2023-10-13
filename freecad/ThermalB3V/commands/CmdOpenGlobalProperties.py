import FreeCAD
from ui.DialogGlobalProperties import DialogGlobalProperties

class CmdOpenGlobalProperties:
    def __init__(self, workbench):
        self.workbench = workbench

    def Activated(self):
        form = DialogGlobalProperties(self.workbench)
        form.exec_()

    def IsActive(self):
        # Always available, even without active document
        return True
        
    def GetResources(self):
        return {
            'MenuText': ("Set Global Properties"),
            'ToolTip': ("Set Global Properties"),
            'Pixmap': "./public/icons/Settings.svg",
        }
