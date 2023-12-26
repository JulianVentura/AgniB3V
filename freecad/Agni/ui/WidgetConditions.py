import FreeCAD
from PySide2.QtWidgets import *
from PySide2.QtGui import *
from constants import CONDITIONS_GROUP
from constants.condition_properties import CONDITION_PROPERTIES
from public.utils import iconPath
from utils.firstForCondition import firstForCondition
from utils.camelCaseToLabel import camelCaseToLabel
from utils.labelToCamelCase import labelToCamelCase
import ObjectsFem

from femviewprovider import view_material_common

class ConditionsInitializer:
    def __init__(self, obj):
        for name, prop in CONDITION_PROPERTIES.items():
            if type(prop['value']) == float:
                obj.addProperty("App::PropertyFloat", name)
            elif type(prop['value']) == int:
                obj.addProperty("App::PropertyInteger", name)
            elif type(prop['value']) == bool:
                obj.addProperty("App::PropertyBool", name)
            else:
                obj.addProperty("App::PropertyString", name)
            setattr(obj, name, prop['value'])

class ConditionsIcon(view_material_common.VPMaterialCommon):
    def getIcon(self):
        return iconPath("Condition.svg")

class WidgetConditions(QWidget):
    """
    Class that represents the "Conditions" section
    """
    def __init__(self, parent, workbench, onClose):
        super().__init__(parent)
        self.workbench = workbench
        self.analysisObject = self.getAnalysisObject(FreeCAD.ActiveDocument)
        self.conditionsGroup = firstForCondition(
            self.analysisObject.Group,
            condition=lambda x: x.Name == CONDITIONS_GROUP,
        )
        self.conditions = self.getConditions()
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
    
        # List of conditions
        self.conditionList = QListWidget(self)
        self.conditionList.addItems(camelCaseToLabel(key) for key in self.conditions.keys())
        self.conditionList.currentRowChanged.connect(self.showProperties)

        # Create button to add a new condition
        addButton = QPushButton("Add Condition", self)
        addButton.clicked.connect(self.addCondition)

        # Create ok button
        okButton = QPushButton('OK', self)
        okButton.setDefault(False)
        okButton.setAutoDefault(False)
        okButton.clicked.connect(self.onClose)

        rightSide.addWidget(self.conditionList)
        rightSide.addWidget(okButton)
        rightSide.addWidget(addButton)

        # Add left side and list of conditions to the layout
        layout.addLayout(self.propertiesLayout)
        layout.addLayout(rightSide)

    def showProperties(self, index):
        """
        Clear properties and show the properties of the selected condition
        """
        # Clear properties
        self.clearProperties()

        # Get selected condition
        conditionName = labelToCamelCase(self.conditionList.item(index).text())
        conditionObj = self.conditions[conditionName]

        # Show properties according to the condition
        for prop in CONDITION_PROPERTIES:
            self.addProperty(conditionObj, prop, CONDITION_PROPERTIES[prop])

    def addProperty(self, conditionObj, propName, propDict):
        """
        Add a new property to the list
        """
        def setConditionProperty(value):
            setattr(conditionObj, propName, value)

        # label and unit
        propLabel = propDict["label"]
        propUnit = propDict["unit"]
        propValue = (
            getattr(conditionObj, propName, None)
                if getattr(conditionObj, propName, None)
                else propDict["value"]
        )

        qtLabel, qtInput = self.createLabel(
            propLabel,
            propUnit,
            propValue,
            setConditionProperty,
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

    def addCondition(self):
        """
        Add a new condition to the list
        """
        activeDocument = FreeCAD.ActiveDocument
        
        conditionLabel, ok = QInputDialog.getText(self, "New Condition", "Name of the new condition:")
        newCondition = labelToCamelCase(conditionLabel)
        if (newCondition in self.conditions) or (newCondition == ""):
            FreeCAD.Console.PrintError("Condition name already exists or is empty\n")
            return

        if ok and newCondition:
            conditionObject = ObjectsFem.makeMaterialSolid(activeDocument, newCondition)
            ConditionsInitializer(conditionObject)
            ConditionsIcon(conditionObject.ViewObject)
            mat = conditionObject.Material
            # Add needed properties
            self.addFreecadNeededProperties(mat)
            mat["Name"] = newCondition
            mat["Label"] = newCondition
            conditionObject.Material = mat
            self.conditions[newCondition] = conditionObject
            self.conditionList.addItem(camelCaseToLabel(newCondition))
            self.conditionsGroup.addObject(conditionObject)

    def addFreecadNeededProperties(self, mat):
        """
        Recieves a condition and adds the properties needed by FreeCAD
        """
        mat["Density"] = "0 kg/m^3"
        mat["YoungsModulus"] = f"0 MPa"
        mat["PoissonRatio"] = "0.00"
        mat["ThermalConductivity"] = "0 W/m/K"
        mat["ThermalExpansionCoefficient"] = "0 um/m/K"
        mat["SpecificHeat"] = "0 J/kg/K"
    
    def getConditions(self):
        """
        Returns the conditions of the document
        """
        conditions = {}
        objects = self.conditionsGroup.Group
        for object in objects:
            if object.TypeId == "App::MaterialObjectPython":
                if "Label" in object.Material:
                    conditions[object.Material["Label"]] = object
        return conditions

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
