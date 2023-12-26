from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
import subprocess
import os
from utils.appState import AppState
from utils.constants import ROUTES, RESULTS_SERIES, DOCUMENTATION_URL
from utils.getFileWithExtension import getFileWithExtension
from public.paths import iconPath


class ProjectWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.appState = AppState()
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
        verticalLayout.addLayout(modelSectionLayout, stretch=1)
        verticalLayout.addLayout(processingSectionLayout, stretch=1)
        verticalLayout.addLayout(postprocessingSectionLayout, stretch=1)
        mainLayout.addWidget(frame)

    def getHeaderButtonsLayout(self, frame):
        """
        Returns the header buttons layout.
        """
        headerButtonsLayout = QHBoxLayout()

        goBackButton = QPushButton()
        goBackButton.setText(QCoreApplication.translate("Dialog", "<", None))
        goBackButton.setFixedSize(30, 30)
        goBackButton.clicked.connect(self.goToLanding)

        rightButtonsLayout = QHBoxLayout()

        settingsButton = QPushButton()
        pixmap = QPixmap(iconPath("settings.svg"))
        icon = QIcon(pixmap)
        settingsButton.setIcon(icon)
        settingsButton.setFixedSize(30, 30)
        settingsButton.clicked.connect(self.configureProject)

        documentationButton = QPushButton()
        pixmap = QPixmap(iconPath("documentation.svg"))
        icon = QIcon(pixmap)
        documentationButton.setIcon(icon)
        documentationButton.setFixedSize(30, 30)
        documentationButton.clicked.connect(self.openDocumentation)

        directoryButton = QPushButton()
        pixmap = QPixmap(iconPath("directory.svg"))
        icon = QIcon(pixmap)
        directoryButton.setIcon(icon)
        directoryButton.setFixedSize(30, 30)
        directoryButton.clicked.connect(self.openProjectDirectory)

        rightButtonsLayout.addWidget(directoryButton)
        rightButtonsLayout.addWidget(documentationButton)
        rightButtonsLayout.addWidget(settingsButton)
        headerButtonsLayout.addWidget(goBackButton, alignment=Qt.AlignLeft)
        headerButtonsLayout.addLayout(rightButtonsLayout, alignment=Qt.AlignRight)
        return headerButtonsLayout

    def getHeaderLayout(self, frame):
        """
        Returns the header layout.
        """
        headerLayout = QHBoxLayout()

        horizontalSpacerLeft = QSpacerItem(
            40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum
        )

        imageLabel = QLabel(frame)
        pixmap = QPixmap(iconPath("agni.png"))
        imageLabel.setPixmap(pixmap)
        imageLabel.setScaledContents(True)
        imageLabel.setAlignment(Qt.AlignCenter)
        imageLabel.setFixedSize(pixmap.width()*0.25, pixmap.height()*0.25)

        horizontalSpacerRight = QSpacerItem(
            40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum
        )

        headerLayout.addItem(horizontalSpacerLeft)
        headerLayout.addWidget(imageLabel)
        headerLayout.addItem(horizontalSpacerRight)
        return headerLayout

    def getModelSectionLayout(self, frame):
        """
        Returns the model section layout.
        """
        verticalLayout = QVBoxLayout()
        modelSectionLabel = QLabel(frame)
        modelSectionLabel.setText(
            QCoreApplication.translate("Dialog", "Modelado", None)
        )

        horizontalLayout = QHBoxLayout()
        freecadButton = QPushButton(frame)
        freecadButton.setText(QCoreApplication.translate("Dialog", "FreeCAD", None))
        freecadButton.clicked.connect(self.openFreeCAD)

        gmatButton = QPushButton(frame)
        gmatButton.setText(QCoreApplication.translate("Dialog", "GMAT", None))
        gmatButton.clicked.connect(self.openGMAT)

        visualizeMaterialButton = QPushButton(frame)
        visualizeMaterialButton.setText(
            QCoreApplication.translate("Dialog", "Visualizar Materiales", None)
        )
        visualizeMaterialButton.clicked.connect(self.visualizeMaterials)

        visualizeNormalsButton = QPushButton(frame)
        visualizeNormalsButton.setText(
            QCoreApplication.translate("Dialog", "Visualizar Normales", None)
        )
        visualizeNormalsButton.clicked.connect(self.visualizeNormals)

        verticalLayout.addWidget(modelSectionLabel)
        horizontalLayout.addWidget(gmatButton)
        horizontalLayout.addWidget(freecadButton)
        horizontalLayout.addWidget(visualizeMaterialButton)
        horizontalLayout.addWidget(visualizeNormalsButton)
        verticalLayout.addLayout(horizontalLayout)
        return verticalLayout

    def getProcessingSectionLayout(self, frame):
        """
        Returns the processing section layout.
        """
        verticalLayout = QVBoxLayout()
        dialogSectionLabel = QLabel(frame)
        dialogSectionLabel.setText(
            QCoreApplication.translate("Dialog", "Procesamiento", None)
        )

        horizontalLayout = QHBoxLayout()
        calculateVFButton = QPushButton(frame)
        calculateVFButton.setText(
            QCoreApplication.translate("Dialog", "Calcular Factores de Vista", None)
        )
        calculateVFButton.clicked.connect(self.calculateViewFactors)

        solverButton = QPushButton(frame)
        solverButton.setText(
            QCoreApplication.translate("Dialog", "Realizar Simulaci\u00f3n", None)
        )
        solverButton.clicked.connect(self.runSimulation)

        solverAndVFButton = QPushButton(frame)
        solverAndVFButton.setText(
            QCoreApplication.translate(
                "Dialog", "Calcular Factores de Vista y Realizar Simulaci\u00f3n", None
            )
        )
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
        postProcessingDialog.setText(
            QCoreApplication.translate("Dialog", "Postprocesamiento", None)
        )

        horizontalLayout = QHBoxLayout()
        paraviewButton = QPushButton(frame)
        paraviewButton.setText(QCoreApplication.translate("Dialog", "ParaView", None))
        paraviewButton.clicked.connect(self.openParaView)

        plotterButton = QPushButton(frame)
        plotterButton.setText(QCoreApplication.translate("Dialog", "Plotter", None))
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
        freecadFile = getFileWithExtension(".FCStd", self.appState.projectDirectory)
        cmd = [
            self.appState.globalConfiguration.getExecutable("freecad"),
            freecadFile,
        ]
        subprocess.Popen(cmd)

    def openGMAT(self):
        """
        Opens GMAT application.
        """
        gmat_executable = self.appState.globalConfiguration.getExecutable("gmat")
        gmat_script = getFileWithExtension(".script", self.appState.projectDirectory)
        cmd = [
            gmat_executable,
            gmat_script,
        ]
        subprocess.Popen(cmd)

    def visualizeNormals(self):
        """
        Opens normal visualization.
        """
        cmd = [
            "python3",
            self.appState.globalConfiguration.getExecutable("preprocessor"),
            "viewn",
            self.appState.projectDirectory,
        ]
        subprocess.Popen(cmd)

    def visualizeMaterials(self):
        """
        Opens material visualization.
        """
        cmd = [
            "python3",
            self.appState.globalConfiguration.getExecutable("preprocessor"),
            "viewm",
            self.appState.projectDirectory,
        ]
        subprocess.Popen(cmd)

    def calculateViewFactors(self):
        """
        Calculates view factors.
        """
        cmd = [
            "python3",
            self.appState.globalConfiguration.getExecutable("preprocessor"),
            "process",
            self.appState.projectDirectory,
        ]
        subprocess.Popen(cmd)

    def runSimulation(self):
        """
        Runs solver simulation.
        """
        cmd = [
            self.appState.globalConfiguration.getExecutable("solver"),
            self.appState.projectDirectory,
            self.appState.globalConfiguration.getSolverConfiguration("mode"),
        ]
        subprocess.Popen(cmd)

    def calculateViewFactorsAndRunSimulation(self):
        """
        Calculates view factors and runs solver simulation.
        """
        # run calculate view factors, wait till ends and run simulation
        cmd = [
            "python3",
            self.appState.globalConfiguration.getExecutable("preprocessor"),
            "process",
            self.appState.projectDirectory,
        ]
        subprocess.Popen(cmd).communicate()
        cmd = [
            self.appState.globalConfiguration.getExecutable("solver"),
            self.appState.projectDirectory,
            self.appState.globalConfiguration.getSolverConfiguration("mode"),
        ]
        subprocess.Popen(cmd)

    def openParaView(self):
        """
        Opens ParaView application.
        """
        cmd = [
            self.appState.globalConfiguration.getExecutable("paraview"),
            "--data",
            os.path.join(self.appState.projectDirectory, RESULTS_SERIES),
        ]
        subprocess.Popen(cmd)

    def openPlotter(self):
        """
        Opens plotter application.
        """
        cmd = [
            "python3",
            self.appState.globalConfiguration.getExecutable("plotter"),
            self.appState.projectDirectory + "/results/result.vtk.series",
        ]
        subprocess.Popen(cmd)

    def goToLanding(self):
        """
        Returns to the landing page.
        """
        self.appState.resetRoutes()
        self.parent.setCurrentIndex(ROUTES["landing"])

    def configureProject(self):
        """
        Opens project configuration dialog.
        """
        self.appState.addRoute(ROUTES["project"])
        self.parent.setCurrentIndex(ROUTES["configuration"])

    def openProjectDirectory(self):
        """
        Opens project directory.
        """
        cmd = [
            self.appState.globalConfiguration.getExecutable("fileManager"),
            self.appState.projectDirectory,
        ]
        subprocess.Popen(cmd)

    def openDocumentation(self):
        """
        Opens the documentation in the browser.
        """
        QDesktopServices.openUrl(QUrl(DOCUMENTATION_URL, QUrl.TolerantMode))
