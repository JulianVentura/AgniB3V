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
        import femcommands.commands
        from constants.global_properties import GLOBAL_PROPERTIES_INPUTS

        # Attributes
        for property in GLOBAL_PROPERTIES_INPUTS:
            print(property)
            self.createAttributes(property)

        # List of tools in the workbench toolbar
        thermalList = [
            "THM_Global_Properties",
        ]
        femList = [
            "FEM_Analysis",
            "FEM_MaterialSolid",
            "FEM_MaterialEditor",
            "FEM_MeshGmshFromShape"
        ]
        self.appendToolbar("Thermal", thermalList)
        self.appendToolbar("FEM", femList)

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
    
    def createAttributes(self, property):
        """
        This functions creates the attributes of the workbench
        It creates the setters and getters for each attribute
        """
        # Create attribute for property[0]
        setattr(self, property[0], property[3])
        # Create getter with capitalized first letter
        setattr(self, f"get{property[0][:1].upper() + property[0][1:]}", lambda: getattr(self, property[0]))
        # Create setter with capitalized first letter
        setattr(self, f"set{property[0][:1].upper() + property[0][1:]}", lambda x: setattr(self, property[0], x))

FreeCAD.Gui.addWorkbench(ThermalWorkbench())