import FreeCAD
from PySide2.QtWidgets import *

class WidgetExportable(QWidget):
    """
    Class that represents the "Exportable" section
    """

    def __init__(self, parent, exportPath, onExportPathChange, onCancel, onExport):
        super().__init__(parent)

        self.exportPath = exportPath
        self.onExportPathChange = onExportPathChange
        self.onCancel = onCancel
        self.onExport = onExport
        self.initUI()
    
    def initUI(self):
        # Label and input for export path
        self.directoryLabel = QLabel(self)
        self.directoryLabel.setText("Directorio")
        self.directoryInput = QLineEdit(self)
        self.directoryInput.setText(self.exportPath)
        self.toolButton = QToolButton(self)
        self.toolButton.setText("...")
        self.toolButton.clicked.connect(self.onToolButton)

        self.verticalLayout = QVBoxLayout()
        self.verticalLayout_3 = QVBoxLayout(self)
        self.horizontalLayout_4 = QHBoxLayout()

        self.verticalLayout.addWidget(self.directoryLabel)
        self.horizontalLayout_4.addWidget(self.directoryInput)
        self.horizontalLayout_4.addWidget(self.toolButton)
        self.verticalLayout.addLayout(self.horizontalLayout_4)
        self.verticalLayout_3.addLayout(self.verticalLayout)

        # Spacer
        self.verticalSpacer = QSpacerItem(20, 226, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.verticalLayout_3.addItem(self.verticalSpacer)
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalSpacer = QSpacerItem(318, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(self.horizontalSpacer)

        # Cancel and export buttons
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

    def onToolButton(self):
        """
        Set directory where is going to be exported
        """
        directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        if (directory):
            FreeCAD.Console.PrintMessage(f"Changing export path to {directory}\n")
            self.directoryInput.setText(directory)
            self.onExportPathChange(directory)
