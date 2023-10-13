import FreeCAD
import FreeCADGui

from PySide import QtGui, QtCore
from PySide2.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QGridLayout
from constants.global_properties import GLOBAL_PROPERTIES_INPUTS

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

        # create inputs
        for property in GLOBAL_PROPERTIES_INPUTS:
            self.create_input(
                ui,
                property[0],
                property[1],
                property[2],
                f"{getattr(self.workbench, property[0])}",
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

        for property in GLOBAL_PROPERTIES_INPUTS:
            line.addWidget(getattr(self, property[0] + "Label"), row, 0)
            line.addWidget(getattr(self, property[0] + "Input"), row, 1)
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
            for property in GLOBAL_PROPERTIES_INPUTS:
                getattr(self, property[0] + "Input").setText(f"{getattr(self.workbench, property[0])}")

    def create_input(self, ui, attribute_name, label, unit, value):
        label = QtGui.QLabel(label + (f" ({unit})" if unit else ""), self)
        input = QtGui.QLabel(value, self)

        setattr(self, attribute_name + "Label", label)
        setattr(self, attribute_name + "Input", input)

    def onOk(self):
        """Closes the dialog"""
        self.close()
