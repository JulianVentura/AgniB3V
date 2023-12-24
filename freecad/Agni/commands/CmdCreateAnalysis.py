import FreeCAD
from public.utils import iconPath
from constants import CONFIG_GROUP, MATERIALS_GROUP, CONDITIONS_GROUP
import ObjectsFem
import FemGui

class CmdCreateAnalysis:
    def Activated(self):
        """
        Executed when the command is activated
        """
        ObjectsFem.makeAnalysis(FreeCAD.ActiveDocument, "Analysis")
        FemGui.setActiveAnalysis(FreeCAD.ActiveDocument.Analysis)

        # Create materials and conditions groups
        materialsGroup = FreeCAD.ActiveDocument.addObject("App::DocumentObjectGroupPython", MATERIALS_GROUP)
        conditionsGroup = FreeCAD.ActiveDocument.addObject("App::DocumentObjectGroupPython", CONDITIONS_GROUP)
        FreeCAD.ActiveDocument.Analysis.addObject(materialsGroup)
        FreeCAD.ActiveDocument.Analysis.addObject(conditionsGroup)

        FreeCAD.ActiveDocument.recompute()

    def IsActive(self):
        """
        Function to check if the command is active
        """
        isActiveDocument = bool(FreeCAD.activeDocument())
        configExists = bool(FreeCAD.activeDocument().getObject(CONFIG_GROUP))
        analysisExists = bool(self.getAnalysisObject(FreeCAD.activeDocument()))
        return isActiveDocument and configExists and not analysisExists
        
    def GetResources(self):
        return {
            'MenuText': ("Create Analysis"),
            'ToolTip': ("Create Analysis"),
            'Pixmap': iconPath("Analysis.svg"),
        }
    
    def getAnalysisObject(self, document):
        """Returns the Analysis object or None if it does not exist"""
        objects = document.Objects
        for object in objects:
            if object.TypeId == "Fem::FemAnalysis":
                return object
        return None
