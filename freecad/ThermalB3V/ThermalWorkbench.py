import FreeCAD, FreeCADGui

class ThermalWorkbench(FreeCADGui.Workbench):

    MenuText = "Thermal B3V"
    ToolTip = "A workbench designed to make satellite thermal analysis"

    def __init__(self):
        from public.utils import iconPath
        self.__class__.Icon = iconPath("ThermalWorkbench.svg")

    def Initialize(self):
        """This function is executed when the workbench is first activated.
        It is executed once in a FreeCAD session followed by the Activated function.
        """
        import commands.Commander as Commander
        import femcommands.commands
        from constants.global_properties import GLOBAL_PROPERTIES_INPUTS

        # Attributes
        for property in GLOBAL_PROPERTIES_INPUTS:
            self.createAttributes(property)

        # List of tools in the workbench toolbar
        thermalList = [
            "THM_Global_Properties",
            "THM_Export_Mesh"
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

    def importProperties(self, path):
        """
        This function imports the properties from a json file
        It only updates the properties defined in the json file
        """
        import json
        from constants.global_properties import GLOBAL_PROPERTIES_INPUTS

        with open(path) as json_file:
            data = json.load(json_file)
            for property in GLOBAL_PROPERTIES_INPUTS:
                if property[0] in data:
                    setattr(self, property[0], data[property[0]])
    
    def getGlobalPropertiesValues(self):
        """
        This function returns the global properties as a dictionary of numbers
        """
        from constants.global_properties import GLOBAL_PROPERTIES_INPUTS

        globalProperties = {}
        for property in GLOBAL_PROPERTIES_INPUTS:
            globalProperties[property[0]] = getattr(self, property[0])
        return globalProperties
    
    def getGlobalPropertiesInfo(self):
        """
        This function returns the global properties info as a dictionary of dictionaries
        """
        from constants.global_properties import GLOBAL_PROPERTIES_INPUTS

        globalProperties = {}
        for property in GLOBAL_PROPERTIES_INPUTS:
            globalProperties[property[0]] = {
                "label": property[1],
                "unit": property[2],
                "value": getattr(self, property[0])
            }
        return globalProperties
