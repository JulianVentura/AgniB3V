from os import path
import subprocess
import FreeCAD
from public.utils import iconPath
from constants import CONFIG_GROUP

class CmdExecutePlotter:
    def Activated(self):
        """
        Executed when the command is activated
        """
        # TODO: implementar getPlotterPath y ver si usamos UI.py o el sh (o si hacemos un main.py)
        # plotterPath = self.workbench.getPlotterPath()
        plotterPath = "/home/guidobotta/dev/tpp/TrabajoProfesional/plotter/plotter.sh"

        if not path.isfile(plotterPath):
            FreeCAD.Console.PrintError(f"Plotter file {plotterPath} not found\n")
            return
        
        FreeCAD.Console.PrintMessage(f"Executing Plotter from {plotterPath}\n")

        # python3 UI.py
        subprocess.run([plotterPath])

    def IsActive(self):
        """
        Function to check if the command is active
        """
        # TODO: ver si se podemos verificar que se haya ejecutado el solver
        isActiveDocument = bool(FreeCAD.activeDocument())
        configExists = bool(FreeCAD.activeDocument().getObject(CONFIG_GROUP))
        analysisExists = bool(self.getAnalysisObject(FreeCAD.activeDocument()))
        return isActiveDocument and configExists and analysisExists
        
    def GetResources(self):
        return {
            'MenuText': ("Execute plotter"),
            'ToolTip': ("Execute plotter"),
            'Pixmap': iconPath("FemMesh.svg"),
        }
    
    def getAnalysisObject(self, document):
        """Returns the Analysis object or None if it does not exist"""
        objects = document.Objects
        for object in objects:
            if object.TypeId == "Fem::FemAnalysis":
                return object
        return None
