import FreeCAD
import FreeCADGui

from PySide import QtGui, QtCore
from PySide2.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QGridLayout

class DialogGlobalProperties(QDialog):
    """
    Dialog to set global properties
    """

    def __init__(self, workbench):
        super().__init__()

        self.workbench = workbench
        self.initUI()

    def initUI(self):
        ui = FreeCADGui.UiLoader()

        # create our window
        self.setWindowTitle("Global Properties")
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)

        globalProperties = self.workbench.getGlobalPropertiesInfo()

        # create inputs
        for property in globalProperties:
            self.create_input(
                ui,
                property,
                globalProperties[property]['label'],
                globalProperties[property]['unit'],
                str(globalProperties[property]['value']),
            )

        # create import button
        importButton = QtGui.QPushButton('Import properties', self)
        importButton.setDefault(False)
        importButton.setAutoDefault(False)
        importButton.clicked.connect(self.onImportProperties)
        
        # create OK button
        okButton = QtGui.QPushButton('OK', self)
        okButton.setDefault(False)
        okButton.setAutoDefault(False)
        okButton.clicked.connect(self.onOk)

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
        line.addWidget(okButton)
        line.addWidget(importButton)
        layout.addLayout(line)

        self.setLayout(layout)

        # now make the window visible
        self.show() 

    def onImportProperties(self):
        """Imports the global properties from the selected json file"""
        file_path, _ = QtGui.QFileDialog.getOpenFileName(None, "Select a file to import", "", "JSON Files (*.json)")
        if file_path:
            self.workbench.importProperties(file_path)
            # update inputs
            globalProperties = self.workbench.getGlobalPropertiesInfo()
            for property in globalProperties:
                getattr(self, property + "Input").setText(str(globalProperties[property]['value']))

    def create_input(self, ui, attribute_name, label, unit, value):
        qtLabel = QtGui.QLabel(label + (f" ({unit})" if unit else ""), self)
        qtInput = QtGui.QLabel(value, self)

        setattr(self, attribute_name + "Label", qtLabel)
        setattr(self, attribute_name + "Input", qtInput)

    def onOk(self):
        """Closes the dialog"""
        self.close()
