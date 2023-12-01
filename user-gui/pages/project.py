from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
import subprocess
import os
from utils.appState import AppState
from utils.constants import ROUTES

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

        headerButtonsLayout = self.getHeaderButtonsLayout(frame)
        headerLayout = self.getHeaderLayout(frame)
        modelSectionLayout = self.getModelSectionLayout(frame)
        processingSectionLayout = self.getProcessingSectionLayout(frame)
        postprocessingSectionLayout = self.getPostprocessingSectionLayout(frame)

        verticalLayout.addLayout(headerButtonsLayout)
        verticalLayout.addLayout(headerLayout)
        verticalLayout.addLayout(modelSectionLayout)
        verticalLayout.addLayout(processingSectionLayout)
        verticalLayout.addLayout(postprocessingSectionLayout)
        mainLayout.addWidget(frame)

    def getHeaderButtonsLayout(self, frame):
        """
        Returns the header buttons layout.
        """
        headerButtonsLayout = QHBoxLayout()

        goBackButton = QPushButton()
        goBackButton.setText(QCoreApplication.translate("Dialog", u"<", None))
        goBackButton.setFixedSize(30, 30)
        goBackButton.clicked.connect(self.goToLanding)

        rightButtonsLayout = QHBoxLayout()

        configButton = QPushButton()
        configButton.setText(QCoreApplication.translate("Dialog", u"\u2699", None))
        configButton.setFixedSize(30, 30)
        configButton.clicked.connect(self.configureProject)

        directoryButton = QPushButton()
        directoryButton.setText(QCoreApplication.translate("Dialog", u"\U0001F4C2", None))
        directoryButton.setFixedSize(30, 30)
        directoryButton.clicked.connect(self.openProjectDirectory)

        rightButtonsLayout.addWidget(directoryButton)
        rightButtonsLayout.addWidget(configButton)
        headerButtonsLayout.addWidget(goBackButton, alignment=Qt.AlignLeft)
        headerButtonsLayout.addLayout(rightButtonsLayout, alignment=Qt.AlignRight)
        return headerButtonsLayout

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
        gmat_executable = AppState().globalConfiguration.getExecutable("gmat")
        gmat_script = os.path.join(
            AppState().get("projectDirectory"),
            "gmat.script",
        )
        cmd = [
            gmat_executable,
            gmat_script,
        ]
        subprocess.Popen(cmd)

    def visualizeMaterials(self):
        """
        Opens material visualization.
        """
        cmd = [
            "python3",
            AppState().globalConfiguration.getExecutable("preprocessor"),
            "viewm",
            AppState().get("projectDirectory"),
        ]
        subprocess.Popen(cmd)

    def calculateViewFactors(self):
        """
        Calculates view factors.
        """
        cmd = [
            "python3",
            AppState().globalConfiguration.getExecutable("preprocessor"),
            "process",
            AppState().get("projectDirectory"),
        ]
        subprocess.Popen(cmd)

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
        cmd = [
            AppState().globalConfiguration.getExecutable("paraview"),
        ]
        subprocess.Popen(cmd)

    def openPlotter(self):
        """
        Opens plotter application.
        """
        cmd = [
            "python3",
            AppState().globalConfiguration.getExecutable("plotter"),
        ]
        subprocess.Popen(cmd)

    def goToLanding(self):
        """
        Returns to the landing page.
        """
        AppState().resetRoutes()
        self.parent.setCurrentIndex(ROUTES["landing"])

    def configureProject(self):
        """
        Opens project configuration dialog.
        """
        AppState().addRoute(ROUTES["project"])
        self.parent.setCurrentIndex(ROUTES["configuration"])

    def openProjectDirectory(self):
        """
        Opens project directory.
        """
        cmd = [
            "nautilus",
            AppState().projectDirectory,
        ]
        subprocess.Popen(cmd)