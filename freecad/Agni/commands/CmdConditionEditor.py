import FreeCAD
from ui.DialogConditionEditor import DialogConditionEditor
from public.utils import iconPath
from constants import CONFIG_GROUP

class CmdConditionEditor:
    def __init__(self, workbench):
        self.workbench = workbench

    def Activated(self):
        """
        Executed when the command is activated
        """
        form = DialogConditionEditor(self.workbench)
        form.exec_()

    def IsActive(self):
        """
        Function to check if the command is active
        """
        isActiveDocument = bool(FreeCAD.activeDocument())
        configExists = bool(FreeCAD.activeDocument().getObject(CONFIG_GROUP))
        analysisExists = bool(self.getAnalysisObject(FreeCAD.activeDocument()))
        return isActiveDocument and configExists and analysisExists
        
    def GetResources(self):
        return {
            'MenuText': ("Edit Conditions"),
            'ToolTip': ("Edit Conditions"),
            'Pixmap': iconPath("Condition.svg"),
        }
    
    def getAnalysisObject(self, document):
        """Returns the Analysis object or None if it does not exist"""
        objects = document.Objects
        for object in objects:
            if object.TypeId == "Fem::FemAnalysis":
                return object
        return None
