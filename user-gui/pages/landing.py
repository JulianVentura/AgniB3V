from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
from utils.appState import AppState
from utils.constants import ROUTES
from public.paths import iconPath

class LandingWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.appState = AppState()
        self.parent = parent
        self.setupUi()

    def setupUi(self):
        """
        Sets up the UI.
        """
        mainLayout = QHBoxLayout(self)
        frame = QFrame(self)
        frame.setFrameShape(QFrame.StyledPanel)
        frame.setFrameShadow(QFrame.Raised)
        verticalLayout = QVBoxLayout(frame)

        headerButtonsLayout = self.getHeaderButtonsLayout(frame)
        headerLayout = self.getHeaderLayout(frame)
        bodyLayout = self.getBodyLayout(frame)

        verticalLayout.addLayout(headerButtonsLayout)
        verticalLayout.addLayout(headerLayout)
        verticalLayout.addLayout(bodyLayout, stretch=1)

        mainLayout.addWidget(frame)

    def getHeaderButtonsLayout(self, frame):
        """
        Returns the header buttons layout.
        """
        headerButtonsLayout = QHBoxLayout()
        rightButtonsLayout = QHBoxLayout()
        rightButtonsLayout.setAlignment(Qt.AlignRight)

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
    
    def getBodyLayout(self, frame):
        """
        Returns the body layout.
        """
        bodyLayout = QVBoxLayout()
        verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        openExistingButton = QPushButton(frame)
        openExistingButton.setText(QCoreApplication.translate("Dialog", u"Abrir Proyecto", None))
        openExistingButton.clicked.connect(self.onOpenProjectClicked)

        newProyectButton = QPushButton(frame)
        newProyectButton.setText(QCoreApplication.translate("Dialog", u"Nuevo Proyecto", None))
        newProyectButton.clicked.connect(self.onNewProjectClicked)

        verticalSpacer = QSpacerItem(20, 168, QSizePolicy.Minimum, QSizePolicy.Expanding)

        bodyLayout.addItem(verticalSpacer_2)
        bodyLayout.addWidget(openExistingButton)
        bodyLayout.addWidget(newProyectButton)
        bodyLayout.addItem(verticalSpacer)
        return bodyLayout
    
    def onNewProjectClicked(self):
        """
        Redirects to the new project page.
        """
        self.appState.addRoute(ROUTES["landing"])
        self.parent.setCurrentIndex(ROUTES["newProject"])

    def onOpenProjectClicked(self):
        """
        Shows a dialog to select a directory and redirects to the project page
        if the directory is valid.
        """
        directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        if directory and self._validateDirectory(directory):
            # TODO: cargar proyecto
            self.appState.openProject(directory)
            self.appState.addRoute(ROUTES["landing"])
            self.parent.setCurrentIndex(ROUTES["project"])

    def _validateDirectory(self, directory):
        """
        Validates if the directory is valid.
        That is, if it has the necessary files.
        """
        # TODO: validar si es un directorio valido
        # es decir, que tenga los archivos necesarios
        return True
    
    def configureProject(self):
        """
        Opens project configuration dialog.
        """
        self.appState.addRoute(ROUTES["landing"])
        self.parent.setCurrentIndex(ROUTES["configuration"])

    def openDocumentation(self):
        """
        Opens the documentation in the browser.
        """
        QDesktopServices.openUrl(QUrl("https://thermalb3v.github.io/", QUrl.TolerantMode))
