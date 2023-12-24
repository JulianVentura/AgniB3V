import FreeCAD
from PySide2.QtWidgets import *
from PySide2.QtGui import *
from constants import MATERIALS_GROUP
from constants.material_properties import MATERIAL_PROPERTIES
from public.utils import iconPath
from utils.firstForCondition import firstForCondition
from utils.camelCaseToLabel import camelCaseToLabel
from utils.labelToCamelCase import labelToCamelCase
import ObjectsFem

from femviewprovider import view_material_common

class MaterialsInitializer:
    def __init__(self, obj):
        for name, prop in MATERIAL_PROPERTIES.items():
            if type(prop['value']) == float:
                obj.addProperty("App::PropertyFloat", name)
            elif type(prop['value']) == int:
                obj.addProperty("App::PropertyInteger", name)
            elif type(prop['value']) == bool:
                obj.addProperty("App::PropertyBool", name)
            else:
                obj.addProperty("App::PropertyString", name)
            setattr(obj, name, prop['value'])

class MaterialsIcon(view_material_common.VPMaterialCommon):
    def getIcon(self):
        return iconPath("Material.svg")

class WidgetMaterials(QWidget):
    """
    Class that represents the "Materials" section
    """
    def __init__(self, parent, workbench, onClose):
        super().__init__(parent)
        self.workbench = workbench
        self.analysisObject = self.getAnalysisObject(FreeCAD.ActiveDocument)
        self.materialsGroup = firstForCondition(
            self.analysisObject.Group,
            condition=lambda x: x.Name == MATERIALS_GROUP,
        )
        self.materials = self.getMaterials()
        self.onClose = onClose
        self.initUI()
    
    def initUI(self):
        """
        Initialize the UI
        """
        layout = QHBoxLayout(self)

        # Left side of the widget
        self.propertiesLayout = QFormLayout()
        
        # Right side of the widget
        rightSide = QVBoxLayout()
    
        # List of materials
        self.materialList = QListWidget(self)
        self.materialList.addItems(camelCaseToLabel(key) for key in self.materials.keys())
        self.materialList.currentRowChanged.connect(self.showProperties)

        # Create button to add a new material
        addButton = QPushButton("Add Material", self)
        addButton.clicked.connect(self.addMaterial)

        # Create ok button
        okButton = QPushButton("OK", self)
        okButton.setDefault(False)
        okButton.setAutoDefault(False)
        okButton.clicked.connect(self.onClose)

        rightSide.addWidget(self.materialList)
        rightSide.addWidget(okButton)
        rightSide.addWidget(addButton)

        # Add left side and list of materials to the layout
        layout.addLayout(self.propertiesLayout)
        layout.addLayout(rightSide)

    def showProperties(self, index):
        """
        Clear properties and show the properties of the selected material
        """
        # Clear properties
        self.clearProperties()

        # Get selected material
        materialName = labelToCamelCase(self.materialList.item(index).text())
        materialObj = self.materials[materialName]

        # Show properties according to the material
        for prop in MATERIAL_PROPERTIES:
            self.addProperty(materialObj, prop, MATERIAL_PROPERTIES[prop])

    def addProperty(self, materialObj, propName, propDict):
        """
        Add a new property to the list
        """
        def setMaterialProperty(value):
            setattr(materialObj, propName, value)

        # label and unit
        propLabel = propDict["label"]
        propUnit = propDict["unit"]
        propValue = (
            getattr(materialObj, propName, None)
                if getattr(materialObj, propName, None)
                else propDict["value"]
        )

        qtLabel, qtInput = self.createLabel(
            propLabel,
            propUnit,
            propValue,
            setMaterialProperty,
        )

        self.propertiesLayout.addRow(qtLabel, qtInput)

    def clearProperties(self):
        """
        Clear all properties
        """
        for i in reversed(range(self.propertiesLayout.count())):
            item = self.propertiesLayout.itemAt(i)
            if item is not None:
                item.widget().setParent(None)

    def addMaterial(self):
        """
        Add a new material to the list
        """
        activeDocument = FreeCAD.ActiveDocument

        materialLabel, ok = QInputDialog.getText(self, "New material", "Name of the new material:")
        newMaterial = labelToCamelCase(materialLabel)
        if (newMaterial in self.materials) or (newMaterial == ""):
            FreeCAD.Console.PrintError("Material name already exists or is empty\n")
            return

        if ok and newMaterial:
            materialObject = ObjectsFem.makeMaterialSolid(activeDocument, newMaterial)
            MaterialsInitializer(materialObject)
            MaterialsIcon(materialObject.ViewObject)
            mat = materialObject.Material
            # Add needed properties
            self.addFreecadNeededProperties(mat)
            mat["Name"] = newMaterial
            mat["Label"] = newMaterial
            materialObject.Material = mat
            self.materials[newMaterial] = materialObject
            self.materialList.addItem(camelCaseToLabel(newMaterial))
            self.materialsGroup.addObject(materialObject)

    def addFreecadNeededProperties(self, mat):
        """
        Recieves a material and adds the properties needed by FreeCAD
        """
        mat["Density"] = "0 kg/m^3"
        mat["YoungsModulus"] = f"0 MPa"
        mat["PoissonRatio"] = "0.00"
        mat["ThermalConductivity"] = "0 W/m/K"
        mat["ThermalExpansionCoefficient"] = "0 um/m/K"
        mat["SpecificHeat"] = "0 J/kg/K"

    def getMaterials(self):
        """
        Returns the materials of the document
        """
        materials = {}
        objects = self.materialsGroup.Group
        for object in objects:
            if object.TypeId == "App::MaterialObjectPython":
                if "Label" in object.Material:
                    materials[object.Material["Label"]] = object
        return materials
    
    def getAnalysisObject(self, document):
        """
        Returns the Analysis object or None if it does not exist
        """
        objects = document.Objects
        for object in objects:
            if object.TypeId == "Fem::FemAnalysis":
                return object
        return None

    def createLabel(self, label, unit, value, callback):
        """
        Creates a label and an input from the attribute label,
        unit, value and callback
        """
        qtLabel = QLabel(label + (f" ({unit})" if unit else ""), self)
        if type(value) == float:
            qtInput = QDoubleSpinBox(self)
            qtInput.setDecimals(5)
            qtInput.setMaximum(999999999)
            qtInput.setValue(value)
            qtInput.valueChanged.connect(lambda x: callback(x))
        elif type(value) == int:
            qtInput = QLineEdit(self)
            qtInput.setValidator(QIntValidator())
            qtInput.setText(str(value))
            qtInput.textChanged.connect(lambda x: callback(int(x)))
        elif type(value) == bool:
            qtInput = QCheckBox(self)
            qtInput.setChecked(value)
            qtInput.stateChanged.connect(lambda x: callback(x))
        else:
            qtInput = QLineEdit(self)
            qtInput.setText(value)
            qtInput.textChanged.connect(lambda x: callback(x))

        return qtLabel, qtInput
