from PySide2.QtWidgets import *
from PySide2.QtCore import *
from utils.appState import AppState
from copy import deepcopy

class ConfigurationWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__()

        self.parent = parent
        self.newSettings = {}
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
        headerButtonsLayout = self.getHeaderButtonsLayout()
        verticalLayout.addLayout(headerButtonsLayout, 0)

        settings = AppState().getGlobalConfiguration()
        self.newSettings = deepcopy(settings)
        for category in settings:
            verticalCategoryLayout = QVBoxLayout()
            verticalCategoryLayout.setContentsMargins(0, 20, 0, 0)
            categoryTitle = QLabel(frame)
            categoryTitle.setText(QCoreApplication.translate("Dialog", category, None))
            categoryTitle.setStyleSheet("font-weight: bold;")
            verticalCategoryLayout.addWidget(categoryTitle)

            for prop in settings[category]:
                propertyLayout = QHBoxLayout()
                propertyLayout.setAlignment(Qt.AlignLeft)

                propertyLabel = QLabel(frame)
                propertyLabel.setText(QCoreApplication.translate("Dialog", prop, None))

                propertyLineEdit = QLineEdit(frame)
                propertyLineEdit.setText(settings[category][prop])
                propertyLineEdit.textChanged.connect(
                    lambda text, category=category, prop=prop: self.onTextChanged(category, prop, text)
                )

                propertyLayout.addWidget(propertyLabel, 1)
                propertyLayout.addWidget(propertyLineEdit, 7)
                verticalCategoryLayout.addLayout(propertyLayout)
            
            verticalLayout.addLayout(verticalCategoryLayout)
        
        saveButton = QPushButton(frame)
        saveButton.setText(QCoreApplication.translate("Dialog", u"Guardar", None))
        saveButton.clicked.connect(self.goBack)
        
        verticalLayout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        verticalLayout.addWidget(saveButton, 1)
        mainLayout.addWidget(frame)

    def getHeaderButtonsLayout(self):
        """
        Returns the header buttons layout.
        """
        headerButtonsLayout = QHBoxLayout()

        goBackButton = QPushButton()
        goBackButton.setText(QCoreApplication.translate("Dialog", u"<", None))
        goBackButton.setFixedSize(30, 30)
        goBackButton.clicked.connect(self.goBack)

        headerButtonsLayout.addWidget(goBackButton, alignment=Qt.AlignLeft)
        return headerButtonsLayout
    
    def saveConfiguration(self):
        """
        Saves the configuration.
        """
        AppState().setGlobalConfiguration(self.newSettings)
        
    def onTextChanged(self, category, prop, text):
        self.newSettings[category][prop] = text

    def goBack(self):
        """
        Goes back to the project page.
        """
        self.saveConfiguration()
        self.parent.setCurrentIndex(AppState().popLastRoute())
        