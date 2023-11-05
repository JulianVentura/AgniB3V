from PySide2.QtWidgets import *
import subprocess
import FreeCAD
from public.utils import workbenchPath
from os import path

class WidgetViewFactors(QWidget):
    """
    Class that represents the "View Factors" section
    """
    def __init__(self, parent, workbench, onCancel):
        super().__init__(parent)
        self.workbench = workbench
        self.onCancel = onCancel
        self.initUI()
    
    def initUI(self):
        """
        Initialize the UI
        """
        # Label and input for export path
        self.raytracePathLabel = QLabel(self)
        self.raytracePathLabel.setText("Seleccionar ubicación del ejecutable (main.py)")
        self.raytracePathInput = QLineEdit(self)
        self.raytracePathInput.setText(self.workbench.getRaytracePath())
        self.pathButton = QToolButton(self)
        self.pathButton.setText("...")
        self.pathButton.clicked.connect(self.onChangePath)

        self.verticalLayout = QVBoxLayout()
        self.verticalLayout_3 = QVBoxLayout(self)
        self.horizontalLayout_4 = QHBoxLayout()

        self.verticalLayout.addWidget(self.raytracePathLabel)
        self.horizontalLayout_4.addWidget(self.raytracePathInput)
        self.horizontalLayout_4.addWidget(self.pathButton)
        self.verticalLayout.addLayout(self.horizontalLayout_4)
        self.verticalLayout_3.addLayout(self.verticalLayout)

        # Spacer
        self.verticalSpacer = QSpacerItem(20, 226, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.verticalLayout_3.addItem(self.verticalSpacer)
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalSpacer = QSpacerItem(318, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(self.horizontalSpacer)

        # Cancel and export buttons
        self.cancelButton = QPushButton('Cancelar', self)
        self.cancelButton.setDefault(False)
        self.cancelButton.setAutoDefault(False)
        self.cancelButton.clicked.connect(self.onCancel)
        self.calculateButton = QPushButton('Calcular', self)
        self.calculateButton.setDefault(False)
        self.calculateButton.setAutoDefault(False)
        self.calculateButton.clicked.connect(self.onCalculateViewFactors)
        self.horizontalLayout_4.addWidget(self.calculateButton)
        self.horizontalLayout_3.addWidget(self.cancelButton)
        self.horizontalLayout_3.addWidget(self.calculateButton)
        self.verticalLayout_3.addLayout(self.horizontalLayout_3)

    def onChangePath(self):
        """
        Changes raytrace path
        """
        fileName, _ = QFileDialog.getOpenFileName(self, "Seleccionar ejecutable", workbenchPath(), "Python files (*.py)")
        if fileName:
            self.raytracePathInput.setText(fileName)
            self.workbench.setRaytracePath(fileName)

    def onCalculateViewFactors(self):
        """
        Execute process to calculate the view factors
        """
        RAYTRACE_COMMAND = "process"
        meshPath = path.join(self.workbench.getExportPath(), "mesh.vtk")
        propsPath = path.join(self.workbench.getExportPath(), "mesh.json")
        raytracingPath = self.workbench.getRaytracePath()

        if not path.isfile(meshPath):
            FreeCAD.Console.PrintError(f"Mesh file {meshPath} not found\n")
            return
        if not path.isfile(propsPath):
            FreeCAD.Console.PrintError(f"Props file {propsPath} not found\n")
            return
        if not path.isfile(raytracingPath):
            FreeCAD.Console.PrintError(f"Raytracing file {raytracingPath} not found\n")
            return
        
        FreeCAD.Console.PrintMessage(f"Reading mesh from {meshPath} and props from {propsPath}\n")
        FreeCAD.Console.PrintMessage(f"Raytracing file {raytracingPath}\n")
        FreeCAD.Console.PrintMessage("Calculating view factors...\n")

        # TODO: get result? Maybe could return different codes depending on the result
        # python3 main.py process <meshPath> <propsPath>
        subprocess.run(["python3", raytracingPath, RAYTRACE_COMMAND, meshPath, propsPath])
        FreeCAD.Console.PrintMessage(f"View factors calculated and written to {propsPath}\n")
