import FreeCAD
from public.utils import iconPath
from constants import CONFIG_GROUP
import ObjectsFem

class CmdCreateFEMMeshRegion:
    def Activated(self):
        """
        Executed when the command is activated
        """
        activeDocument = FreeCAD.activeDocument()
        analysisObject = self.getAnalysisObject(activeDocument)
        meshObject = self.getMeshObject(analysisObject)
        ObjectsFem.makeMeshRegion(activeDocument, meshObject)
        activeDocument.recompute()

    def IsActive(self):
        """
        Function to check if the command is active
        """
        isActiveDocument = bool(FreeCAD.activeDocument())
        configExists = bool(FreeCAD.activeDocument().getObject(CONFIG_GROUP))
        analysisObject = self.getAnalysisObject(FreeCAD.activeDocument())
        femObjectExists = bool(analysisObject) and bool(self.getMeshObject(analysisObject))
        return isActiveDocument and configExists and femObjectExists
        
    def GetResources(self):
        return {
            'MenuText': ("Create FEM Mesh"),
            'ToolTip': ("Create FEM Mesh"),
            'Pixmap': iconPath("FemMesh.svg"),
        }
    
    def getAnalysisObject(self, document):
        """Returns the Analysis object or None if it does not exist"""
        objects = document.Objects
        for object in objects:
            if object.TypeId == "Fem::FemAnalysis":
                return object
        return None
    
    def getMeshObject(self, analysisObject):
        """Returns the mesh object or None if it does not exist"""
        objects = analysisObject.Group
        for object in objects:
            if object.TypeId == "Fem::FemMeshObjectPython":
                return object
        return None
