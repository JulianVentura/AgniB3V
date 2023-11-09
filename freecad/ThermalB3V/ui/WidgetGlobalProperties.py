from PySide2.QtWidgets import *
from PySide2.QtCore import *
from PySide2.QtGui import *

class WidgetGlobalProperties(QWidget):
    """
    Widget to set global properties
    """

    def __init__(self, parent, workbench, onClose):
        """
        Initialize the widget.
        It receives the parent widget, the workbench and the onClose callback.
        """
        super().__init__(parent)

        self.workbench = workbench
        self.onClose = onClose
        self.initUI()

    def initUI(self):
        """
        Initialize the UI
        """
        globalProperties = self.workbench.getGlobalPropertiesValues()

        # create inputs
        for property in globalProperties:
            self.createLabel(
                property,
                globalProperties[property]['label'],
                globalProperties[property]['unit'],
                globalProperties[property]['value'],
            )

        # create import button
        importButton = QPushButton('Importar propiedades', self)
        importButton.setDefault(False)
        importButton.setAutoDefault(False)
        importButton.clicked.connect(self.onImportGlobalProperties)
        
        # create ok button
        okButton = QPushButton('Aceptar', self)
        okButton.setDefault(False)
        okButton.setAutoDefault(False)
        okButton.clicked.connect(self.onClose)

        layout = QVBoxLayout()

        line = QHBoxLayout()
        layout.addLayout(line)

        line = QGridLayout()

        # Add inputs to layout
        row = 0

        for property in globalProperties:
            line.addWidget(getattr(self, property + "Label"), row, 0)
            line.addWidget(getattr(self, property + "Input"), row, 1)
            row += 1

        layout.addLayout(line)

        line = QHBoxLayout()
        line.addWidget(importButton)
        line.addStretch()
        line.addWidget(okButton)
        layout.addLayout(line)

        self.setLayout(layout)

    def onImportGlobalProperties(self):
        """
        Imports the global properties from the selected json file
        """
        file_path, _ = QFileDialog.getOpenFileName(None, "Select a file to import", "", "JSON Files (*.json)")
        if file_path:
            self.workbench.importGlobalProperties(file_path)
            # update inputs
            globalProperties = self.workbench.getGlobalPropertiesValues()
            for property in globalProperties:
                # TODO: improve
                try:
                    getattr(self, property + "Input").setValue(float(globalProperties[property]['value']))
                except AttributeError:
                    getattr(self, property + "Input").setText(globalProperties[property]['value'])

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
            qtInput.valueChanged.connect(lambda x: self.workbench.setGlobalPropertieValue(attributeName, x))
        elif type(value) == int:
            qtInput = QLineEdit(self)
            qtInput.setValidator(QIntValidator())
            qtInput.setText(str(value))
            qtInput.textChanged.connect(lambda x: self.workbench.setGlobalPropertieValue(attributeName, int(x)))
        elif type(value) == bool:
            qtInput = QCheckBox(self)
            qtInput.setChecked(value)
            qtInput.stateChanged.connect(lambda x: self.workbench.setGlobalPropertieValue(attributeName, x))
        else:
            qtInput = QLineEdit(self)
            qtInput.setText(value)
            qtInput.textChanged.connect(lambda x: self.workbench.setGlobalPropertieValue(attributeName, x))

        setattr(self, attributeName + "Label", qtLabel)
        setattr(self, attributeName + "Input", qtInput)

