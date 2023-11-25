from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
import os

class NewProjectWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.setupUi()

    def setupUi(self):
        self.mainLayout = QVBoxLayout(self)
        self.frame = QFrame(self)
        self.frame.setFrameShape(QFrame.StyledPanel)
        self.frame.setFrameShadow(QFrame.Raised)
        self.verticalLayout_5 = QVBoxLayout(self.frame)
        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.label = QLabel(self.frame)
        font = QFont()
        font.setPointSize(24)
        self.label.setFont(font)
        self.label.setText(QCoreApplication.translate("Dialog", u"Thermal B3V", None))

        self.horizontalSpacer_4 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.horizontalLayout = QHBoxLayout()
        self.verticalLayout = QVBoxLayout()
        self.label_2 = QLabel(self.frame)
        self.label_2.setText(QCoreApplication.translate("Dialog", u"Directorio", None))

        self.label_3 = QLabel(self.frame)
        self.label_3.setText(QCoreApplication.translate("Dialog", u"Nombre del Proyecto", None))

        self.verticalLayout_3 = QVBoxLayout()
        self.lineEdit = QLineEdit(self.frame)
        self.lineEdit_2 = QLineEdit(self.frame)

        self.frame1 = QFrame(self.frame)
        self.verticalLayout_4 = QVBoxLayout(self.frame1)
        self.verticalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.toolButton = QToolButton(self.frame1)
        self.toolButton.setAutoFillBackground(False)
        self.toolButton.setText(QCoreApplication.translate("Dialog", u"...", None))
        self.toolButton.clicked.connect(self.onSelectDirectory)

        self.verticalSpacer = QSpacerItem(20, 146, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.pushButton = QPushButton(self.frame)
        self.pushButton.clicked.connect(self.onNewProject)
        self.pushButton.setText(QCoreApplication.translate("Dialog", u"Crear Proyecto", None))
        
        self.horizontalSpacer_5 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_4.addItem(self.horizontalSpacer_3)
        self.horizontalLayout_4.addWidget(self.label)
        self.horizontalLayout_4.addItem(self.horizontalSpacer_4)
        self.verticalLayout_5.addLayout(self.horizontalLayout_4)
        self.verticalLayout_5.addItem(self.verticalSpacer_2)
        self.verticalLayout.addWidget(self.label_2)
        self.verticalLayout.addWidget(self.label_3)
        self.horizontalLayout.addLayout(self.verticalLayout)
        self.verticalLayout_3.addWidget(self.lineEdit)
        self.verticalLayout_3.addWidget(self.lineEdit_2)
        self.horizontalLayout.addLayout(self.verticalLayout_3)
        self.verticalLayout_4.addWidget(self.toolButton)
        self.horizontalLayout.addWidget(self.frame1, 0, Qt.AlignTop)
        self.verticalLayout_5.addLayout(self.horizontalLayout)
        self.verticalLayout_5.addItem(self.verticalSpacer)
        self.horizontalLayout_3.addItem(self.horizontalSpacer_2)
        self.horizontalLayout_3.addWidget(self.pushButton)
        self.horizontalLayout_3.addItem(self.horizontalSpacer_5)
        self.verticalLayout_5.addLayout(self.horizontalLayout_3)

        self.mainLayout.addWidget(self.frame)

    def onSelectDirectory(self):
        """
        Set directory where is going to be exported.
        """
        directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        if directory:
            self.lineEdit.setText(directory)
    
    def onNewProject(self):
        """
        Checks if the directory exists and creates it if it doesn't and
        checks if the project name is valid and creates the project if it is.
        Finally, it redirects to the project page.
        """
        # TODO: ver si vale la pena tener un estado global y cargar el proyecto
        directory = self.lineEdit.text()
        projectName = self.lineEdit_2.text()
        
        if not self._validateDirectoryAndName(directory, projectName):
            return
        
        # Create project directory
        projectDirectory = os.path.join(directory, projectName)
        try:
            os.mkdir(projectDirectory)
        except:
            QMessageBox.warning(self, "Error", "No se pudo crear el proyecto")
            return
        
        # TODO: copiar templates
        
        self.parent.setCurrentIndex(2)

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