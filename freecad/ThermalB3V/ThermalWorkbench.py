import FreeCAD
import FreeCADGui
import json

class WorkbenchSettings:
    properties = {}

    @classmethod
    def addProperty(cls, prop, value):
        cls.properties[prop] = value

    def __init__(self, obj):
        obj.Proxy = self
        for prop, value in WorkbenchSettings.properties.items():
            if getattr(obj, prop, None) == None:
                if type(value) == float:
                    obj.addProperty("App::PropertyFloat", prop)
                elif type(value) == int:
                    obj.addProperty("App::PropertyInteger", prop)
                elif type(value) == bool:
                    obj.addProperty("App::PropertyBool", prop)
                else:
                    obj.addProperty("App::PropertyString", prop)
            setattr(obj, prop, value)

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

        self.attributes = []

        # Initialize global properties
        for propertyName, props in GLOBAL_PROPERTIES_INPUTS.items():
            self.createAttributes(propertyName, props)

        # Initialize export and document path
        # Will be set on Activated
        self.createAttributes("exportPath", "")
        self.createAttributes("documentPath", "")

        # Initialize raytrace path
        self.createAttributes("raytracePath", "")

        # Initialize materials
        self.createAttributes("materials", {})

        # List of tools for workbench initialization toolbar
        workbenchInitList = [
            "THM_Select_Document",
            "THM_Initialize_Properties",
        ]

        # List of tools in the FEM toolbar
        femList = [
            "THM_Create_Analysis",
            "THM_Material_Editor",
            "THM_Create_FEM_Mesh",
            "THM_Create_FEM_Mesh_Region",
        ]

        # List of tools in the workbench toolbar
        thermalList = [
            "THM_Global_Properties",
            "THM_Export_Mesh",
        ]

        self.appendToolbar("Document", workbenchInitList)
        self.appendToolbar("FEM", femList)
        self.appendToolbar("Thermal", thermalList)

        Commander.addCommands(self)

    def Activated(self):
        """
        This function is executed whenever the workbench is activated
        """
        from constants import CONFIG_GROUP
        if bool(FreeCAD.ActiveDocument):
            if bool(FreeCAD.ActiveDocument.getObject(CONFIG_GROUP)):
                configGroup = FreeCAD.ActiveDocument.getObject(CONFIG_GROUP)
                self.loadWorkbenchSettings(configGroup)
            else:
                self.saveWorkbenchSettings()

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
        # add commands to the context menu
        # self.appendContextMenu("My commands", self.list)
        return

    def GetClassName(self): 
        # This function is mandatory if this is a full Python workbench
        # This is not a template, the returned string should be exactly "Gui::PythonWorkbench"
        return "Gui::PythonWorkbench"
    
    def createAttributes(self, propertyName, value):
        """
        This functions creates the attributes of the workbench
        It creates the setters and getters for each attribute
        """
        self.attributes.append(propertyName)
        # Create attribute for propertyName
        setattr(self, propertyName, value)
        # Create getter with capitalized first letter
        setattr(self, f"get{propertyName[:1].upper() + propertyName[1:]}", lambda: getattr(self, propertyName))
        # Create setter with capitalized first letter
        setattr(self, f"set{propertyName[:1].upper() + propertyName[1:]}", lambda x: setattr(self, propertyName, x))

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

    def setGlobalPropertieValue(self, propertyName, value):
        """
        This function sets the global property value
        """
        props = getattr(self, propertyName)
        props['value'] = value

    def importGlobalProperties(self, path):
        """
        This function imports the properties from a json file
        It only updates the properties defined in the json file
        """
        with open(path) as json_file:
            data = json.load(json_file)
            for propertyName in self.getGlobalPropertiesValues():
                if propertyName in data:
                    self.setGlobalPropertieValue(propertyName, data[propertyName])
    
    def saveWorkbenchSettings(self):
        """
        It saves the workbench settings in an object in configGroup
        """
        from constants import CONFIG_GROUP, CONFIG_OBJECT
        import FreeCAD

        FreeCAD.Console.PrintMessage("Saving workbench settings\n")
        configGroup = FreeCAD.ActiveDocument.getObject(CONFIG_GROUP)

        if not configGroup:
            FreeCAD.Console.PrintMessage("Creating config group\n")
            configGroup = FreeCAD.ActiveDocument.addObject("App::DocumentObjectGroupPython", CONFIG_GROUP)

        # Set properties in workbenchSettings
        for propertyName, props in self.getGlobalPropertiesValues().items():
            WorkbenchSettings.addProperty(propertyName, props['value'])
        WorkbenchSettings.addProperty("exportPath", self.exportPath)
        WorkbenchSettings.addProperty("documentPath", self.documentPath)
        WorkbenchSettings.addProperty("raytracePath", self.raytracePath)

        # Check if workbenchSettings exists
        FreeCAD.Console.PrintMessage("Getting if workbench settings exist\n")
        workbenchSettings = FreeCAD.ActiveDocument.getObject(CONFIG_OBJECT)

        if not workbenchSettings:
            FreeCAD.Console.PrintMessage("Workbench settings do not exist. Creating new one\n")
            # Create new App::FeaturePython object, asign WorkbenchSettings and asign it to the group
            workbenchSettings = FreeCAD.ActiveDocument.addObject("App::FeaturePython", CONFIG_OBJECT)
            configGroup.addObject(workbenchSettings)

        WorkbenchSettings(workbenchSettings)
        FreeCAD.ActiveDocument.recompute()
    
    def loadWorkbenchSettings(self, configGroup):
        """
        It loads the workbench settings from an object in configGroup
        """
        from constants import CONFIG_OBJECT
        FreeCAD.Console.PrintMessage("Loading workbench settings\n")
        workbenchSettings = configGroup.getObject(CONFIG_OBJECT)

        FreeCAD.Console.PrintMessage("Loading global properties\n")
        # Load global properties
        for propertyName in self.getGlobalPropertiesValues():
            if (propValue := getattr(workbenchSettings, propertyName, None)) != None:
                self.setGlobalPropertieValue(propertyName, propValue)
        
        FreeCAD.Console.PrintMessage("Loading export and document path\n")
        # Load export and document path
        if (propValue := getattr(workbenchSettings, "exportPath", None)) != None:
            self.setExportPath(propValue)
        if (propValue := getattr(workbenchSettings, "documentPath", None)) != None:
            self.setDocumentPath(propValue)
        if (propValue := getattr(workbenchSettings, "raytracePath", None)) != None:
            self.setRaytracePath(propValue)
