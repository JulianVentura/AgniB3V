import FreeCAD, FreeCADGui

class ThermalWorkbench(FreeCADGui.Workbench):

    MenuText = "Thermal B3V"
    ToolTip = "A description of my workbench" # TODO: change description
    Icon = "./public/icons/ThermalWorkbench.svg" # TODO: change icon

    def Initialize(self):
        """This function is executed when the workbench is first activated.
        It is executed once in a FreeCAD session followed by the Activated function.
        """
        import commands.Commander as Commander

        # Attributes
        self.betaAngle = 30.0
        self.orbitHeight = 300.0

        # List of tools in the workbench toolbar
        self.appendToolbar("Thermal", ["Global_Properties"])

        Commander.addCommands(self)

    def Activated(self):
        """This function is executed whenever the workbench is activated"""
        return

    def Deactivated(self):
        """This function is executed whenever the workbench is deactivated"""
        return

    def ContextMenu(self, recipient):
        """This function is executed whenever the user right-clicks on screen"""
        # "recipient" will be either "view" or "tree"
        self.appendContextMenu("My commands", self.list) # add commands to the context menu

    def GetClassName(self): 
        # This function is mandatory if this is a full Python workbench
        # This is not a template, the returned string should be exactly "Gui::PythonWorkbench"
        return "Gui::PythonWorkbench"
    
    def getBetaAngle(self):
        return self.betaAngle
    
    def setBetaAngle(self, betaAngle):
        self.betaAngle = betaAngle

    def getOrbitHeight(self):
        return self.orbitHeight
    
    def setOrbitHeight(self, orbitHeight):
        self.orbitHeight = orbitHeight

FreeCAD.Gui.addWorkbench(ThermalWorkbench())