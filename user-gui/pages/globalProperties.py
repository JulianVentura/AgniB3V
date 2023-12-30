from PySide2.QtGui import QShowEvent
from PySide2.QtWidgets import *
from PySide2.QtCore import *
from PySide2.QtGui import *
from utils.CustomJsonEncoder import CustomJsonEncoder
from utils.appState import AppState
from utils.constants import GLOBAL_PROPERTIES_INPUTS
import json
import os

class GlobalPropertiesWidget(QWidget):
    """
    Widget to set global properties
    """

    def __init__(self, parent):
        """
        Initialize the widget.
        It receives the parent widget.
        """
        super().__init__(parent)

        self.parent = parent
        self.appState = AppState()
        self.properties = {}

    def showEvent(self, event: QShowEvent) -> None:
        """
        Executed when the widget is shown.
        """
        self.loadProperties()
        self.setupUi()

        return super().showEvent(event)

    def setupUi(self):
        """
        Initialize the UI.
        """
        # create inputs
        for property in GLOBAL_PROPERTIES_INPUTS:
            self.createLabel(
                property,
                GLOBAL_PROPERTIES_INPUTS[property]['label'],
                GLOBAL_PROPERTIES_INPUTS[property]['unit'],
                self.properties[property],
            )
        
        # create ok button
        okButton = QPushButton('OK', self)
        okButton.setDefault(False)
        okButton.setAutoDefault(False)
        okButton.clicked.connect(self.onSave)

        layout = QVBoxLayout()

        line = QHBoxLayout()
        layout.addLayout(line)

        line = QGridLayout()

        # Add inputs to layout
        row = 0

        for property in GLOBAL_PROPERTIES_INPUTS:
            line.addWidget(getattr(self, property + "Label"), row, 0)
            line.addWidget(getattr(self, property + "Input"), row, 1)
            row += 1

        layout.addLayout(line)

        line = QHBoxLayout()
        line.addStretch()
        line.addWidget(okButton)
        layout.addLayout(line)

        self.setLayout(layout)

    def loadProperties(self):
        """
        Reads the properties from the json file
        """
        propertiesPath = os.path.join(self.appState.projectDirectory, 'properties.json')
        with open(propertiesPath, 'r') as json_file:
            propertiesJson = json.load(json_file)
            self.properties = propertiesJson['global_properties']
    
    def setGlobalPropertieValue(self, attributeName, value):
        """
        Sets the global property value
        """
        self.properties[attributeName] = value
    
    def createLabel(self, attributeName, label, unit, value):
        """
        Creates a label and it value from the attribute name, label, unit and value
        """
        qtLabel = QLabel(label + (f" ({unit})" if unit else ""), self)
        if type(value) == float:
            qtInput = QDoubleSpinBox(self)
            qtInput.setDecimals(5)
            qtInput.setMaximum(999999999)
            qtInput.setValue(value)
            qtInput.valueChanged.connect(lambda x: self.setGlobalPropertieValue(attributeName, x))
        elif type(value) == int:
            qtInput = QLineEdit(self)
            qtInput.setValidator(QIntValidator())
            qtInput.setText(str(value))
            qtInput.textChanged.connect(lambda x: self.setGlobalPropertieValue(attributeName, int(x)))
        elif type(value) == bool:
            qtInput = QCheckBox(self)
            qtInput.setChecked(value)
            qtInput.stateChanged.connect(lambda x: self.setGlobalPropertieValue(attributeName, x))
        else:
            qtInput = QLineEdit(self)
            qtInput.setText(value)
            qtInput.textChanged.connect(lambda x: self.setGlobalPropertieValue(attributeName, x))

        setattr(self, attributeName + "Label", qtLabel)
        setattr(self, attributeName + "Input", qtInput)

    def onSave(self):
        """
        Saves the global properties
        """
        propertiesPath = os.path.join(self.appState.projectDirectory, 'properties.json')
        with open(propertiesPath, 'r') as json_file:
            propertiesJson = json.load(json_file)
            propertiesJson['global_properties'].update(self.properties)
        
        with open(propertiesPath, 'w') as json_file:
            json.dump(
                propertiesJson,
                json_file,
                indent=4,
                cls=CustomJsonEncoder,
            )

        self.goBack()

    def goBack(self):
        """
        Goes back to the project page.
        """
        self.parent.setCurrentIndex(self.appState.popLastRoute())
