import FreeCADGui

from commands.CmdOpenGlobalProperties import CmdOpenGlobalProperties
from commands.CmdExportMesh import CmdExportMesh
from commands.CmdSelectDocument import CmdSelectDocument

def addCommands(workbench):
    """
    Add commands to the workbench
    """
    FreeCADGui.addCommand('THM_Select_Document', CmdSelectDocument(workbench))
    FreeCADGui.addCommand('THM_Global_Properties', CmdOpenGlobalProperties(workbench))
    FreeCADGui.addCommand('THM_Export_Mesh', CmdExportMesh(workbench))
