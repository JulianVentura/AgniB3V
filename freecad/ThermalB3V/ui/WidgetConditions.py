import FreeCAD
from PySide2.QtWidgets import *
from constants import CONDITIONS_GROUP
from constants.condition_properties import CONDITION_PROPERTIES
from public.utils import iconPath
from utils.firstForCondition import firstForCondition
from utils.camelCaseToLabel import camelCaseToLabel
from utils.labelToCamelCase import labelToCamelCase
import ObjectsFem

from femviewprovider import view_material_common

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
            self.addProperty(conditionObj , prop)

    def addProperty(self, conditionObj, prop):
        """
        Add a new property to the list
        """
        def setConditionProperty(value):
            mat = conditionObj.Material
            mat[prop] = str(value)
            conditionObj.Material = mat

        qtLabel = QLabel(str(prop), self)
        qtInput = QDoubleSpinBox(self)
        # TODO: configurable?
        qtInput.setDecimals(5)
        qtInput.setMaximum(999999999)
        if prop in conditionObj.Material:
            qtInput.setValue(float(conditionObj.Material[prop]))
        else:
            qtInput.setValue(0)
            
        qtInput.valueChanged.connect(setConditionProperty)
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
            ConditionsIcon(conditionObject.ViewObject)
            mat = conditionObject.Material
            # Initialize properties
            for prop in CONDITION_PROPERTIES:
                mat[prop] = "0"
            
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
