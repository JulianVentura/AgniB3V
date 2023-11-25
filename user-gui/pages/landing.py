from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

class LandingWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.setupUi()

    def setupUi(self):
        mainLayout = QHBoxLayout(self)
        frame = QFrame(self)
        frame.setFrameShape(QFrame.StyledPanel)
        frame.setFrameShadow(QFrame.Raised)
        verticalLayout = QVBoxLayout(frame)

        headerLayout = self.getHeaderLayout(frame)
        bodyLayout = self.getBodyLayout(frame)

        verticalLayout.addLayout(headerLayout)
        verticalLayout.addLayout(bodyLayout)

        mainLayout.addWidget(frame)
        
    def getHeaderLayout(self, frame):
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
        self.parent.setCurrentIndex(1)

    def onOpenProjectClicked(self):
        """
        Shows a dialog to select a directory and redirects to the project page
        if the directory is valid.
        """
        directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        if directory and self._validateDirectory(directory):
            # TODO: cargar proyecto
            self.parent.setCurrentIndex(2)

    def _validateDirectory(self, directory):
        # TODO: validar si es un directorio valido
        # es decir, que tenga los archivos necesarios
        return True
