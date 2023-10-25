import FreeCAD
import FreeCADGui

class ThermalWorkbench(FreeCADGui.Workbench):
    """
    Main workbench class.
    It is instantiated when the FreeCAD is started.
    """

    def __init__(self):
        from public.utils import iconPath
        self.__class__.Icon = iconPath("ThermalWorkbench.svg")
        self.__class__.MenuText = "Thermal B3V"
        self.__class__.ToolTip = "A workbench designed to make satellite thermal analysis"

    def Initialize(self):
        """
        This function is executed when the workbench is first activated.
        It is executed once in a FreeCAD session followed by the Activated function.
        """
        import commands.Commander as Commander
        import femcommands.commands
        from constants.global_properties import GLOBAL_PROPERTIES_INPUTS

        # Attributes
        for propertyName, props in GLOBAL_PROPERTIES_INPUTS.items():
            self.createAttributes(propertyName, props)

        # Initialize export and document path
        # Will be set on Activated
        self.exportPath = ""
        self.documentPath = ""

        # List of tools in the workbench toolbar
        thermalList = [
            "THM_Select_Document",
            "THM_Global_Properties",
            "THM_Export_Mesh"
        ]
        # TODO: implement FEM tools
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
        """
        This function is executed whenever the workbench is activated
        """
        if bool(FreeCAD.activeDocument()) and bool(FreeCAD.activeDocument().FileName):
            # TODO: load state
            return

    def Deactivated(self):
        """
        This function is executed whenever the workbench is deactivated
        """
        return

    def ContextMenu(self, recipient):
        """
        This function is executed whenever the user right-clicks on screen
        """
        # "recipient" will be either "view" or "tree"
        self.appendContextMenu("My commands", self.list) # add commands to the context menu

    def GetClassName(self): 
        # This function is mandatory if this is a full Python workbench
        # This is not a template, the returned string should be exactly "Gui::PythonWorkbench"
        return "Gui::PythonWorkbench"
    
    def createAttributes(self, propertyName, props):
        """
        This functions creates the attributes of the workbench
        It creates the setters and getters for each attribute
        """
        # Create attribute for propertyName
        setattr(self, propertyName, props)
        # Create getter with capitalized first letter
        setattr(self, f"get{propertyName[:1].upper() + propertyName[1:]}", lambda: getattr(self, propertyName))
        # Create setter with capitalized first letter
        setattr(self, f"set{propertyName[:1].upper() + propertyName[1:]}", lambda x: setattr(self, propertyName, x))

    def setGlobalPropertieValue(self, propertyName, x):
        """
        This function sets the global property value
        """
        props = getattr(self, propertyName)
        props['value'] = x

    def importProperties(self, path):
        """
        This function imports the properties from a json file
        It only updates the properties defined in the json file
        """
        import json
        from constants.global_properties import GLOBAL_PROPERTIES_INPUTS

        with open(path) as json_file:
            data = json.load(json_file)
            for propertyName in GLOBAL_PROPERTIES_INPUTS:
                if propertyName in data:
                    props = getattr(self, propertyName)
                    props['value'] = data[propertyName]
    
    def getGlobalPropertiesValues(self):
        """
        This function returns the global properties as a dictionary of dictionaries
        { propName: { label, unit, value }, ... }
        """
        from constants.global_properties import GLOBAL_PROPERTIES_INPUTS

        globalProperties = {}
        for propertyName in GLOBAL_PROPERTIES_INPUTS:
            globalProperties[propertyName] = getattr(self, propertyName)
        return globalProperties

    def getExportPath(self):
        """
        This function returns the export path
        """
        return self.exportPath

    def setExportPath(self, path):
        """
        This function sets the export path
        """
        self.exportPath = path

    def setDocumentPath(self, path):
        """
        This functions set the document path
        """
        self.documentPath = path
