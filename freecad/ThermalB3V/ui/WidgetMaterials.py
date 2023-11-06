import FreeCAD
from PySide2.QtWidgets import *
from constants.material_properties import MATERIAL_PROPERTIES
import ObjectsFem

class WidgetMaterials(QWidget):
    """
    Class that represents the "Materials" section
    """
    def __init__(self, parent, workbench):
        super().__init__(parent)
        self.workbench = workbench
        self.materials = self.getMaterials(FreeCAD.ActiveDocument)
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
        self.materialList.addItems(key for key in self.materials.keys())
        self.materialList.currentRowChanged.connect(self.showProperties)

        # Add button to add a new material
        addButton = QPushButton("Añadir Material", self)
        addButton.clicked.connect(self.addMaterial)

        rightSide.addWidget(self.materialList)
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
        materialName = self.materialList.item(index).text()
        materialObj = self.materials[materialName]

        # Show properties according to the material
        for prop in MATERIAL_PROPERTIES:
            self.addProperty(materialObj , prop)

    def addProperty(self, materialObj, prop):
        """
        Add a new property to the list
        """
        def setMaterialProperty(value):
            mat = materialObj.Material
            mat[prop] = str(value)
            materialObj.Material = mat

        qtLabel = QLabel(str(prop), self)
        qtInput = QDoubleSpinBox(self)
        # TODO: configurable?
        qtInput.setDecimals(5)
        qtInput.setMaximum(999999999)
        if prop in materialObj.Material:
            qtInput.setValue(float(materialObj.Material[prop]))
        else:
            qtInput.setValue(0)
            
        qtInput.valueChanged.connect(setMaterialProperty)
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
        analysisObject = self.getAnalysisObject(activeDocument)
        if analysisObject is None:
            FreeCAD.Console.PrintError("Analysis object does not exist\n")
            return

        newMaterial, ok = QInputDialog.getText(self, 'Nuevo Material', 'Nombre del nuevo material:')

        if ok and newMaterial:
            materialObject = ObjectsFem.makeMaterialSolid(activeDocument, newMaterial)            
            mat = materialObject.Material
            # Initialize properties
            for prop in MATERIAL_PROPERTIES:
                mat[prop] = "0"
            
            mat["Name"] = newMaterial
            mat["Label"] = newMaterial
            materialObject.Material = mat
            self.materials[newMaterial] = materialObject
            self.materialList.addItem(newMaterial)
            analysisObject.addObject(materialObject)

    def getAnalysisObject(self, document):
        """
        Returns the Analysis object or None if it does not exist
        """
        objects = document.Objects
        for object in objects:
            if object.TypeId == "Fem::FemAnalysis":
                return object
        return None
    
    def getMaterials(self, document):
        """
        Returns the materials of the document
        """
        materials = {}
        objects = document.Objects
        for object in objects:
            if object.TypeId == "App::MaterialObjectPython":
                if "Label" in object.Material:
                    materials[object.Material["Label"]] = object
        return materials
