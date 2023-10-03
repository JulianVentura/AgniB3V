import FreeCADGui

from commands.CmdOpenGlobalProperties import CmdOpenGlobalProperties

def addCommands(workbench):
    FreeCADGui.addCommand('Global_Properties', CmdOpenGlobalProperties(workbench))
