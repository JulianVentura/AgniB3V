import FreeCADGui

from commands.CmdOpenGlobalProperties import CmdOpenGlobalProperties
from commands.CmdExportMesh import CmdExportMesh
from commands.CmdSelectDocument import CmdSelectDocument
from commands.CmdMaterialEditor import CmdMaterialEditor
from commands.CmdInitializeProperties import CmdInitializeProperties
from commands.CmdCreateAnalysis import CmdCreateAnalysis

def addCommands(workbench):
    """
    Add commands to the workbench
    """
    FreeCADGui.addCommand('THM_Select_Document', CmdSelectDocument(workbench))
    FreeCADGui.addCommand('THM_Global_Properties', CmdOpenGlobalProperties(workbench))
    FreeCADGui.addCommand('THM_Export_Mesh', CmdExportMesh(workbench))
    FreeCADGui.addCommand('THM_Material_Editor', CmdMaterialEditor(workbench))
    FreeCADGui.addCommand('THM_Initialize_Properties', CmdInitializeProperties(workbench))
    FreeCADGui.addCommand('THM_Create_Analysis', CmdCreateAnalysis())
