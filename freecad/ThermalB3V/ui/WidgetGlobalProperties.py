from PySide2.QtWidgets import *
from PySide2.QtCore import *

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
        globalProperties = self.workbench.getGlobalPropertiesInfo()

        # create inputs
        for property in globalProperties:
            self.createLabel(
                property,
                globalProperties[property]['label'],
                globalProperties[property]['unit'],
                str(globalProperties[property]['value']),
            )

        # create import button
        importButton = QPushButton('Import properties', self)
        importButton.setDefault(False)
        importButton.setAutoDefault(False)
        importButton.clicked.connect(self.onImportProperties)
        
        # create close button
        closeButton = QPushButton('Close', self)
        closeButton.setDefault(False)
        closeButton.setAutoDefault(False)
        closeButton.clicked.connect(self.onClose)

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
        line.addStretch()
        line.addWidget(closeButton)
        line.addWidget(importButton)
        layout.addLayout(line)

        self.setLayout(layout)

    def onImportProperties(self):
        """
        Imports the global properties from the selected json file
        """
        file_path, _ = QFileDialog.getOpenFileName(None, "Select a file to import", "", "JSON Files (*.json)")
        if file_path:
            self.workbench.importProperties(file_path)
            # update inputs
            globalProperties = self.workbench.getGlobalPropertiesInfo()
            for property in globalProperties:
                getattr(self, property + "Input").setText(str(globalProperties[property]['value']))

    def createLabel(self, attributeName, label, unit, value):
        """
        Creates a label and it value from the attribute name, label, unit and value
        """
        qtLabel = QLabel(label + (f" ({unit})" if unit else ""), self)
        qtInput = QLabel(value, self)

        setattr(self, attributeName + "Label", qtLabel)
        setattr(self, attributeName + "Input", qtInput)

