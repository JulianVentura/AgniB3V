from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
import subprocess
from utils.appState import AppState

class ProjectWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.setupUi()

    def setupUi(self):
        """
        Sets up the UI.
        """
        mainLayout = QVBoxLayout(self)
        frame = QFrame(self)
        frame.setFrameShape(QFrame.StyledPanel)
        frame.setFrameShadow(QFrame.Raised)
        verticalLayout = QVBoxLayout(frame)
        goBackButton = QPushButton(frame)
        goBackButton.setText(QCoreApplication.translate("Dialog", u"<", None))
        goBackButton.setFixedSize(30, 30)
        goBackButton.clicked.connect(self.goBack)

        headerLayout = self.getHeaderLayout(frame)
        modelSectionLayout = self.getModelSectionLayout(frame)
        processingSectionLayout = self.getProcessingSectionLayout(frame)
        postprocessingSectionLayout = self.getPostprocessingSectionLayout(frame)

        verticalLayout.addLayout(headerLayout)
        verticalLayout.addLayout(modelSectionLayout)
        verticalLayout.addLayout(processingSectionLayout)
        verticalLayout.addLayout(postprocessingSectionLayout)
        mainLayout.addWidget(frame)

    def getHeaderLayout(self, frame):
        """
        Returns the header layout.
        """
        headerLayout = QHBoxLayout()

        horizontalSpacerLeft = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        title = QLabel(frame)
        font = QFont()
        font.setPointSize(24)
        title.setFont(font)
        title.setText(QCoreApplication.translate("Dialog", u"Thermal B3V", None))

        horizontalSpacerRight = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        headerLayout.addItem(horizontalSpacerLeft)
        headerLayout.addWidget(title)
        headerLayout.addItem(horizontalSpacerRight)
        return headerLayout

    def getModelSectionLayout(self, frame):
        """
        Returns the model section layout.
        """
        verticalLayout = QVBoxLayout()
        modelSectionLabel = QLabel(frame)
        modelSectionLabel.setText(QCoreApplication.translate("Dialog", u"Modelado", None))

        horizontalLayout = QHBoxLayout()
        freecadButton = QPushButton(frame)
        freecadButton.setText(QCoreApplication.translate("Dialog", u"FreeCAD", None))
        freecadButton.clicked.connect(self.openFreeCAD)

        gmatButton = QPushButton(frame)
        gmatButton.setText(QCoreApplication.translate("Dialog", u"GMAT", None))
        gmatButton.clicked.connect(self.openGMAT)

        visualizeMaterialButton = QPushButton(frame)
        visualizeMaterialButton.setText(QCoreApplication.translate("Dialog", u"Visualizar Materiales", None))
        visualizeMaterialButton.clicked.connect(self.visualizeMaterials)

        verticalLayout.addWidget(modelSectionLabel)
        horizontalLayout.addWidget(freecadButton)
        horizontalLayout.addWidget(gmatButton)
        horizontalLayout.addWidget(visualizeMaterialButton)
        verticalLayout.addLayout(horizontalLayout)
        return verticalLayout

    def getProcessingSectionLayout(self, frame):
        """
        Returns the processing section layout.
        """
        verticalLayout = QVBoxLayout()
        dialogSectionLabel = QLabel(frame)
        dialogSectionLabel.setText(QCoreApplication.translate("Dialog", u"Procesamiento", None))

        horizontalLayout = QHBoxLayout()
        calculateVFButton = QPushButton(frame)
        calculateVFButton.setText(QCoreApplication.translate("Dialog", u"Calcular Factores de Vista", None))
        calculateVFButton.clicked.connect(self.calculateViewFactors)

        solverButton = QPushButton(frame)
        solverButton.setText(QCoreApplication.translate("Dialog", u"Realizar Simulaci\u00f3n", None))
        solverButton.clicked.connect(self.runSimulation)

        solverAndVFButton = QPushButton(frame)
        solverAndVFButton.setText(QCoreApplication.translate("Dialog", u"Calcular Factores de Vista y Realizar Simulaci\u00f3n", None))
        solverAndVFButton.clicked.connect(self.calculateViewFactorsAndRunSimulation) 

        verticalLayout.addWidget(dialogSectionLabel)
        horizontalLayout.addWidget(calculateVFButton)
        horizontalLayout.addWidget(solverButton)
        verticalLayout.addLayout(horizontalLayout)
        verticalLayout.addWidget(solverAndVFButton)
        return verticalLayout       

    def getPostprocessingSectionLayout(self, frame):
        """
        Returns the postprocessing section layout.
        """
        verticalLayout = QVBoxLayout()
        postProcessingDialog = QLabel(frame)
        postProcessingDialog.setText(QCoreApplication.translate("Dialog", u"Postprocesamiento", None))

        horizontalLayout = QHBoxLayout()
        paraviewButton = QPushButton(frame)
        paraviewButton.setText(QCoreApplication.translate("Dialog", u"ParaView", None))
        paraviewButton.clicked.connect(self.openParaView)

        plotterButton = QPushButton(frame)
        plotterButton.setText(QCoreApplication.translate("Dialog", u"Plotter", None))
        plotterButton.clicked.connect(self.openPlotter)

        verticalLayout.addWidget(postProcessingDialog)
        horizontalLayout.addWidget(paraviewButton)
        horizontalLayout.addWidget(plotterButton)
        verticalLayout.addLayout(horizontalLayout)
        return verticalLayout

    def openFreeCAD(self):
        """
        Opens FreeCAD application.
        """
        print("Opening FreeCAD")
        subprocess.Popen(["Freecad"])

    def openGMAT(self):
        """
        Opens GMAT application.
        """
        pass

    def visualizeMaterials(self):
        """
        Opens material visualization.
        """
        cmd = [
            "python3",
            "/home/guidobotta/dev/tpp/TrabajoProfesional/standalone-raytrace/main.py",
            "viewm",
            AppState().get("projectDirectory"),
        ]
        subprocess.Popen(cmd)

    def calculateViewFactors(self):
        """
        Calculates view factors.
        """
        pass

    def runSimulation(self):
        """
        Runs solver simulation.
        """
        pass

    def calculateViewFactorsAndRunSimulation(self):
        """
        Calculates view factors and runs solver simulation.
        """
        pass

    def openParaView(self):
        """
        Opens ParaView application.
        """
        pass

    def openPlotter(self):
        """
        Opens plotter application.
        """
        cmd = [
            "python3",
            "/home/guidobotta/dev/tpp/TrabajoProfesional/plotter/UI.py",
        ]
        subprocess.Popen(cmd)

    def goBack(self):
        """
        Returns to the landing page.
        """
        self.parent.setCurrentIndex(0)
