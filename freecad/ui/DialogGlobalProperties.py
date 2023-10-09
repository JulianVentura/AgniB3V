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
        layout.addLayout(line)

        self.setLayout(layout)

        # now make the window visible
        self.show()    

    def onInputChange(self, attribute_name, value):
        getattr(self, attribute_name + "Input").setText(value)
        try:
            getattr(self.workbench, "set" + attribute_name[:1].upper() + attribute_name[1:])(float(value))
        except ValueError:
            pass

    def validate_input(self, value):
        # Deletes any non-numeric character except the dot (.)
        cleaned_value = ''.join(c for c in value if c.isdigit() or c == '.')

        # Replaces any dot (.) after the first one with an empty string
        cleaned_value = cleaned_value.replace(',', '.')

        return cleaned_value

    def create_input(self, ui, attribute_name, label, unit, value):
        label = QtGui.QLabel(label + (f" ({unit})" if unit else ""), self)

        input = ui.createWidget("Gui::InputField")
        # input.unit = unit
        input.setText(value)
        input.textEdited.connect(
            lambda value: self.onInputChange(attribute_name, self.validate_input(value))
        )

        setattr(self, attribute_name + "Label", label)
        setattr(self, attribute_name + "Input", input)

    def onOk(self):
        self.close()
