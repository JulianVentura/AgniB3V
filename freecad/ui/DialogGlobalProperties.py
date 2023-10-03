import FreeCAD
import FreeCADGui

from PySide import QtGui, QtCore
from PySide2.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QGridLayout

class DialogGlobalProperties(QDialog):
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

        # Beta angle
        print(self.workbench.getBetaAngle())
        self.create_input(
            ui,
            "betaAngle",
            "Beta angle",
            "deg",
            f"{self.workbench.betaAngle} deg",
            self.onBetaAngleChange,
        )

        # Orbit height
        print(self.workbench.getOrbitHeight())
        self.create_input(
            ui,
            "orbitHeight",
            "Orbit height",
            "km",
            f"{self.workbench.orbitHeight} km",
            self.onOrbitHeightChange,
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

        row = 0
        line.addWidget(self.betaAngleLabel, row, 0, 1, 2)
        line.addWidget(self.betaAngleInput, row, 1)
        row += 1

        line.addWidget(self.orbitHeightLabel, row, 0)
        line.addWidget(self.orbitHeightInput, row, 1)
        row += 1

        layout.addLayout(line)

        line = QHBoxLayout()
        line.addStretch()
        line.addWidget(okButton)
        layout.addLayout(line)

        self.setLayout(layout)

        # now make the window visible
        self.show()    

    def onBetaAngleChange(self, value):
        self.betaAngleInput.setText(value)
        try:
            print(value)
            self.workbench.setBetaAngle(float(value))
            print("Salio bien")
        except ValueError:
            pass

    def onOrbitHeightChange(self, value):
        self.orbitHeightInput.setText(value)
        try:
            print(value)
            self.workbench.setOrbitHeight(float(value))
            print("Salio bien")
        except ValueError:
            pass

    def validate_input(self, value):
        # Elimina cualquier carácter no numérico excepto el punto (.)
        cleaned_value = ''.join(c for c in value if c.isdigit() or c == '.')

        # Reemplaza la coma (,) con el punto (.) para garantizar que sea un número válido
        cleaned_value = cleaned_value.replace(',', '.')

        return cleaned_value

    def create_input(self, ui, attribute_name, label, unit, value, change_function):
        label = QtGui.QLabel(label, self)

        input = ui.createWidget("Gui::InputField")
        input.unit = unit
        input.setText(value)
        input.textEdited.connect(lambda value: change_function(self.validate_input(value)))

        setattr(self, attribute_name + "Label", label)
        setattr(self, attribute_name + "Input", input)

    def onOk(self):
        self.close()
