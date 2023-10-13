import FreeCADGui

from commands.CmdOpenGlobalProperties import CmdOpenGlobalProperties
from commands.CmdExportMesh import CmdExportMesh

def addCommands(workbench):
    FreeCADGui.addCommand('THM_Global_Properties', CmdOpenGlobalProperties(workbench))
    FreeCADGui.addCommand('THM_Export_Mesh', CmdExportMesh())
