from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
import os
from utils.appState import AppState
from utils.setUpNewProject import setUpNewProject
from utils.constants import DOCUMENTATION_URL, ROUTES
from public.paths import iconPath

class NewProjectWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.appState = AppState()
        self.parent = parent
        self.setupUi()

    def setupUi(self):
        mainLayout = QVBoxLayout(self)
        frame = QFrame(self)
        frame.setFrameShape(QFrame.StyledPanel)
        frame.setFrameShadow(QFrame.Raised)
        verticalLayout = QVBoxLayout(frame)

        headerButtonsLayout = self.getHeaderButtonsLayout(frame)
        headerLayout = self.getHeaderLayout(frame)
        bodyLayout = self.getBodyLayout(frame)

        verticalLayout.addLayout(headerButtonsLayout)
        verticalLayout.addLayout(headerLayout)
        verticalLayout.addLayout(bodyLayout)
        mainLayout.addWidget(frame)

    def getHeaderButtonsLayout(self, frame):
        """
        Returns the header buttons layout.
        """
        headerButtonsLayout = QHBoxLayout()
        rightButtonsLayout = QHBoxLayout()
        rightButtonsLayout.setAlignment(Qt.AlignRight)

        goBackButton = QPushButton()
        goBackButton.setText(QCoreApplication.translate("Dialog", u"<", None))
        goBackButton.setFixedSize(30, 30)
        goBackButton.clicked.connect(self.goToLanding)
        
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

        horizontalSpacerLeft = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        imageLabel = QLabel(frame)
        pixmap = QPixmap(iconPath("agni.png"))
        imageLabel.setPixmap(pixmap)
        imageLabel.setScaledContents(True)
        imageLabel.setAlignment(Qt.AlignCenter)
        imageLabel.setFixedSize(pixmap.width()*0.25, pixmap.height()*0.25)

        horizontalSpacerRight = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        headerLayout.addItem(horizontalSpacerLeft)
        headerLayout.addWidget(imageLabel)
        headerLayout.addItem(horizontalSpacerRight)
        return headerLayout
    
    def getBodyLayout(self, frame):
        verticalLayout = QVBoxLayout()
        verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        horizontalLayout = QHBoxLayout()
        labelLayout = QVBoxLayout()
        directoryLabel = QLabel(frame)
        directoryLabel.setText(QCoreApplication.translate("Dialog", u"Directorio", None))

        projectNameLabel = QLabel(frame)
        projectNameLabel.setText(QCoreApplication.translate("Dialog", u"Nombre del Proyecto", None))

        lineEditLayout = QVBoxLayout()
        self.directoryEdit = QLineEdit(frame)
        self.projectNameEdit = QLineEdit(frame)

        dirButtonFrame = QFrame(frame)
        dirButtonLayout = QVBoxLayout(dirButtonFrame)
        dirButtonLayout.setContentsMargins(0, 0, 0, 0)
        directoryButton = QToolButton(dirButtonFrame)
        directoryButton.setAutoFillBackground(False)
        directoryButton.setText(QCoreApplication.translate("Dialog", u"...", None))
        directoryButton.clicked.connect(self.onSelectDirectory)

        verticalSpacer_2 = QSpacerItem(20, 146, QSizePolicy.Minimum, QSizePolicy.Expanding)

        createButtonLayout = QHBoxLayout()
        horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        createButton = QPushButton(frame)
        createButton.clicked.connect(self.onNewProject)
        createButton.setText(QCoreApplication.translate("Dialog", u"Crear Proyecto", None))
        
        horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        labelLayout.addWidget(directoryLabel)
        labelLayout.addWidget(projectNameLabel)
        horizontalLayout.addLayout(labelLayout)
        lineEditLayout.addWidget(self.directoryEdit)
        lineEditLayout.addWidget(self.projectNameEdit)
        horizontalLayout.addLayout(lineEditLayout)
        dirButtonLayout.addWidget(directoryButton)
        horizontalLayout.addWidget(dirButtonFrame, 0, Qt.AlignTop)
        createButtonLayout.addItem(horizontalSpacer)
        createButtonLayout.addWidget(createButton)
        createButtonLayout.addItem(horizontalSpacer_2)
        verticalLayout.addItem(verticalSpacer)
        verticalLayout.addLayout(horizontalLayout)
        verticalLayout.addItem(verticalSpacer_2)
        verticalLayout.addLayout(createButtonLayout)

        return verticalLayout

    def onSelectDirectory(self):
        """
        Set directory where is going to be exported.
        """
        directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        if directory:
            self.directoryEdit.setText(directory)
    
    def onNewProject(self):
        """
        Checks if the directory exists and creates it if it doesn't and
        checks if the project name is valid and creates the project if it is.
        Finally, it redirects to the project page.
        """
        directory = self.directoryEdit.text()
        projectName = self.projectNameEdit.text()
        
        if not self._validateDirectoryAndName(directory, projectName):
            return
        
        newProjectDirectory = os.path.join(directory, projectName)
        if not setUpNewProject(newProjectDirectory):
            QMessageBox.warning(self, "Error", "No se pudo crear el proyecto")
            return
        
        self.appState.openProject(newProjectDirectory)
        self.appState.addRoute(ROUTES["newProject"])
        self.parent.setCurrentIndex(ROUTES["project"])

    def _validateDirectoryAndName(self, directory, projectName) -> bool:
        """
        Checks if the directory exists and creates it if it doesn't and
        checks if the project name is valid and creates the project if it is.
        Returns True if the directory and project name are valid, False otherwise.
        """
        if directory == "":
            QMessageBox.warning(self, "Error", "No se ha seleccionado un directorio")
            return False

        if projectName == "":
            QMessageBox.warning(self, "Error", "No se ha seleccionado un nombre de proyecto")
            return False
        
        if not os.path.isdir(directory):
            QMessageBox.information(self, "Atención", "El directorio no existe, se creará")
            try:
                os.mkdir(directory)
            except:
                QMessageBox.warning(self, "Error", "No se pudo crear el directorio")
                return False
        
        return True
    
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
        self.appState.addRoute(ROUTES["newProject"])
        self.parent.setCurrentIndex(ROUTES["configuration"])

    def openDocumentation(self):
        """
        Opens the documentation in the browser.
        """
        QDesktopServices.openUrl(QUrl(DOCUMENTATION_URL, QUrl.TolerantMode))
