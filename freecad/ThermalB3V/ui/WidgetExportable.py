from PySide2.QtWidgets import *

class WidgetExportable(QWidget):
    """
    Class that represents the "Exportable" section
    """

    def __init__(self, onCancel, onExport):
        super().__init__()
        self.onCancel = onCancel
        self.onExport = onExport
        self.initUI()
    
    def initUI(self):
        self.verticalLayout_3 = QVBoxLayout(self)
        self.verticalLayout = QVBoxLayout()
        self.directoryLabel = QLabel(self)
        self.directoryLabel.setText("Directorio")
        self.verticalLayout.addWidget(self.directoryLabel)
        self.horizontalLayout_4 = QHBoxLayout()
        self.lineEdit_2 = QLineEdit(self)
        self.horizontalLayout_4.addWidget(self.lineEdit_2)
        self.toolButton = QToolButton(self)
        self.toolButton.setText("...")
        self.horizontalLayout_4.addWidget(self.toolButton)
        self.verticalLayout.addLayout(self.horizontalLayout_4)
        self.verticalLayout_3.addLayout(self.verticalLayout)
        self.verticalSpacer = QSpacerItem(20, 226, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.verticalLayout_3.addItem(self.verticalSpacer)
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalSpacer = QSpacerItem(318, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(self.horizontalSpacer)
        self.cancelButton = QPushButton('Cancelar', self)
        self.cancelButton.setDefault(False)
        self.cancelButton.setAutoDefault(False)
        self.cancelButton.clicked.connect(self.onCancel)
        self.exportButton = QPushButton('Exportar', self)
        self.exportButton.setDefault(False)
        self.exportButton.setAutoDefault(False)
        self.exportButton.clicked.connect(self.onExport)
        self.horizontalLayout_4.addWidget(self.exportButton)
        self.horizontalLayout_3.addWidget(self.cancelButton)
        self.horizontalLayout_3.addWidget(self.exportButton)
        self.verticalLayout_3.addLayout(self.horizontalLayout_3)