import FreeCAD
from public.utils import iconPath
from constants import CONFIG_GROUP
import ObjectsFem
import FemGui

class CmdCreateAnalysis:
    def Activated(self):
        """
        Executed when the command is activated
        """
        # TODO: here on function IsActive, check if analysis exists
        ObjectsFem.makeAnalysis(FreeCAD.ActiveDocument, "Analysis")
        FemGui.setActiveAnalysis(FreeCAD.ActiveDocument.Analysis)

    def IsActive(self):
        """
        Show command as active if there is an active document
        but config does not exists
        """
        return bool(FreeCAD.activeDocument()) and bool(FreeCAD.activeDocument().getObject(CONFIG_GROUP))
        
    def GetResources(self):
        return {
            'MenuText': ("Create Analysis"),
            'ToolTip': ("Create Analysis"),
            'Pixmap': iconPath("Analysis.svg"),
        }
