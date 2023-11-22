import FreeCAD
import FreeCADGui
from public.utils import iconPath
from constants import CONFIG_GROUP
import ObjectsFem
from femmesh.gmshtools import GmshTools

class CmdCreateFEMMesh:
    def Activated(self):
        """
        Executed when the command is activated
        """
        activeDocument = FreeCAD.activeDocument()
        analysisObject = self.getAnalysisObject(activeDocument)
        partSelected = self.getPartSelected()

        femMeshObj = ObjectsFem.makeMeshGmsh(activeDocument, partSelected.Name + "_Mesh")
        femMeshObj.Part = FreeCAD.ActiveDocument.getObject(partSelected.Name)
        femMeshObj.ElementDimension = "2D"
        femMeshObj.ElementOrder = "1st"

        gmshMesh = GmshTools(femMeshObj)
        error = gmshMesh.create_mesh()
        if error:
            FreeCAD.Console.PrintError("Error: " + error + "\n")
            return

        analysisObject.addObject(femMeshObj)
        activeDocument.recompute()

    def IsActive(self):
        """
        Function to check if the command is active
        """
        isActiveDocument = bool(FreeCAD.activeDocument())
        configExists = bool(FreeCAD.activeDocument().getObject(CONFIG_GROUP))
        analysisExists = bool(self.getAnalysisObject(FreeCAD.activeDocument()))
        partIsSelected = bool(self.getPartSelected())
        return isActiveDocument and configExists and analysisExists and partIsSelected
        
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
    
    def getPartSelected(self):
        """
        Returns the selected Part object or None if there is no selection or the
        selected object is not a Part.
        """
        selection = FreeCADGui.Selection.getSelection()
        if len(selection) == 1 and selection[0].isDerivedFrom("Part::Feature"):
            return selection[0]
        else:
            return None
