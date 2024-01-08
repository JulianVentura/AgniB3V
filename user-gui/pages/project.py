from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
import subprocess
import os
from utils.appState import AppState
from utils.constants import (
    ROUTES,
    RESULTS_SERIES,
    DOCUMENTATION_URL,
    EXECUTABLES,
    SOLVER_MODES,
    MODES_TRANSLATIONS,
)
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
        horizontalLayout2 = QHBoxLayout()

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

        globalPropertiesButton = QPushButton()
        globalPropertiesButton.setText(
            QCoreApplication.translate("Dialog", "Propiedades Globales", None)
        )
        globalPropertiesButton.clicked.connect(self.openGlobalProperties)

        verticalLayout.addWidget(modelSectionLabel)
        horizontalLayout.addWidget(gmatButton)
        horizontalLayout.addWidget(freecadButton)
        horizontalLayout2.addWidget(visualizeMaterialButton)
        horizontalLayout2.addWidget(visualizeNormalsButton)
        horizontalLayout2.addWidget(globalPropertiesButton)
        verticalLayout.addLayout(horizontalLayout)
        verticalLayout.addLayout(horizontalLayout2)
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
        horizontalLayout2 = QHBoxLayout()

        # create switch to select if want to run cpu o gpu
        solverModeLabel = QLabel(frame)
        solverModeLabel.setText(
            QCoreApplication.translate("Dialog", "Modo de ejecuci\u00f3n", None)
        )
        solverModeLabel.setAlignment(Qt.AlignCenter)
        solverModeComboBox = QComboBox(frame)
        solverModeComboBox.addItems(SOLVER_MODES)
        solverModeComboBox.currentIndexChanged.connect(self.onChangeSolverMode)
        solverModeComboBox.setCurrentIndex(SOLVER_MODES.index(self.appState.solverMode))

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
        horizontalLayout.addWidget(solverModeLabel)
        horizontalLayout2.addWidget(solverAndVFButton, stretch=2)
        horizontalLayout2.addWidget(solverModeComboBox, stretch=1)
        verticalLayout.addLayout(horizontalLayout)
        verticalLayout.addLayout(horizontalLayout2)
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

    def onChangeSolverMode(self, index):
        """
        Changes the solver mode.
        """
        self.appState.solverMode = SOLVER_MODES[index]
    
    def openFreeCAD(self):
        """
        Opens FreeCAD application.
        """
        freecadFile = getFileWithExtension(".FCStd", self.appState.projectDirectory)
        cmd = [
            EXECUTABLES["freecad"],
            freecadFile,
        ]
        self.appState.processManager.runCommand("freecad", cmd)

    def openGMAT(self):
        """
        Opens GMAT application.
        """
        gmat_executable = EXECUTABLES["gmat"]
        gmat_script = getFileWithExtension(".script", self.appState.projectDirectory)
        cmd = [
            gmat_executable,
            gmat_script,
        ]
        self.appState.processManager.runCommand("gmat", cmd)

    def visualizeNormals(self):
        """
        Opens normal visualization.
        """
        cmd = [
            "python3",
            EXECUTABLES["preprocessor"],
            "viewn",
            self.appState.projectDirectory,
        ]
        self.appState.processManager.runCommand("viewn", cmd)

    def visualizeMaterials(self):
        """
        Opens material visualization.
        """
        cmd = [
            "python3",
            EXECUTABLES["preprocessor"],
            "viewm",
            self.appState.projectDirectory,
        ]
        self.appState.processManager.runCommand("viewm", cmd)

    def calculateViewFactors(self):
        """
        Calculates view factors.
        """
        cmd = [
            "python3",
            EXECUTABLES["preprocessor"],
            "process",
            self.appState.projectDirectory,
        ]
        self.appState.processManager.runCommand("process", cmd)

    def runSimulation(self):
        """
        Runs solver simulation.
        """
        cmd = [
            EXECUTABLES["solver"],
            self.appState.projectDirectory,
            MODES_TRANSLATIONS[self.appState.solverMode],
        ]
        self.appState.processManager.runCommand("solver", cmd)

    def calculateViewFactorsAndRunSimulation(self):
        """
        Calculates view factors and runs solver simulation.
        """
        # run calculate view factors, wait till ends and run simulation
        # TODO: fix this, use ProcessManager
        cmd = [
            "python3",
            EXECUTABLES["preprocessor"],
            "process",
            self.appState.projectDirectory,
        ]
        subprocess.Popen(cmd).wait()
        cmd = [
            EXECUTABLES["solver"],
            self.appState.projectDirectory,
            MODES_TRANSLATIONS[self.appState.solverMode],
        ]
        subprocess.Popen(cmd).wait()

    def openParaView(self):
        """
        Opens ParaView application.
        """
        cmd = [
            EXECUTABLES["paraview"],
            "--data",
            os.path.join(self.appState.projectDirectory, RESULTS_SERIES),
        ]
        self.appState.processManager.runCommand("paraview", cmd)

    def openPlotter(self):
        """
        Opens plotter application.
        """
        cmd = [
            "python3",
            EXECUTABLES["plotter"],
            self.appState.projectDirectory + "/results/result.vtk.series",
        ]
        self.appState.processManager.runCommand("plotter", cmd)

    def goToLanding(self):
        """
        Returns to the landing page.
        """
        self.appState.resetRoutes()
        self.parent.setCurrentIndex(ROUTES["landing"])

    def openProjectDirectory(self):
        """
        Opens project directory.
        """
        cmd = [
            EXECUTABLES["fileManager"],
            self.appState.projectDirectory,
        ]
        self.appState.processManager.runCommand("fileManager", cmd)

    def openDocumentation(self):
        """
        Opens the documentation in the browser.
        """
        QDesktopServices.openUrl(QUrl(DOCUMENTATION_URL, QUrl.TolerantMode))

    def openGlobalProperties(self):
        """
        Opens the global properties dialog.
        """
        # Check if properties.json exists
        propertiesPath = os.path.join(self.appState.projectDirectory, "properties.json")
        if not os.path.exists(propertiesPath):
            QMessageBox.critical(
                self,
                "Error",
                "No existe el archivo properties.json. Para crearlo, debe exportar desde FreeCAD.",
                QMessageBox.Ok,
            )
            return
        self.appState.addRoute(ROUTES["project"])
        self.parent.setCurrentIndex(ROUTES["globalProperties"])
