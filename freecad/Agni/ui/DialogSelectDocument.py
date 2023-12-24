import FreeCAD
import FreeCADGui
from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
from constants import CONFIG_GROUP

class DialogSelectDocument(QDialog):
    """
    Dialog to select document
    """

    def __init__(self, workbench):
        super().__init__()

        self.workbench = workbench
        self.initUI()

    def initUI(self):
        """
        Initialize the UI
        """
        self.setWindowTitle("Select document")
        self.setMinimumSize(QSize(600, 300))
        # Create a horizontal layout for the Dialog
        self.horizontalLayout = QHBoxLayout(self)
        # Create a container frame for the Dialog
        self.container = QFrame(self)
        self.container.setFrameShape(QFrame.StyledPanel)
        self.container.setFrameShadow(QFrame.Raised)
        # Create a vertical layout for the container frame
        self.verticalLayout_7 = QVBoxLayout(self.container)
        # Create a radio button for selecting an existing document
        self.radioExisting = QRadioButton(self.container)
        self.radioExisting.setText("Select existing document")
        self.radioExisting.setChecked(True)
        self.verticalLayout_7.addWidget(self.radioExisting)
        # Create a horizontal layout for the existing document input
        self.horizontalLayout_2 = QHBoxLayout()
        self.existingInput = QLineEdit(self.container)
        self.existingInput.setPlaceholderText("Select directory")
        self.horizontalLayout_2.addWidget(self.existingInput)
        self.existingButton = QToolButton(self.container)
        self.existingButton.setText("...")
        self.existingButton.clicked.connect(self.onExistingButton)
        self.horizontalLayout_2.addWidget(self.existingButton)
        self.verticalLayout_7.addLayout(self.horizontalLayout_2)
        # Create a radio button for creating a new document
        self.radioNew = QRadioButton(self.container)
        self.radioNew.setText("Create new document")
        self.verticalLayout_7.addWidget(self.radioNew)
        # Create a line edit for the new document name input
        self.newNameInput = QLineEdit(self.container)
        self.newNameInput.setText("")
        self.newNameInput.setPlaceholderText("Document name")
        self.verticalLayout_7.addWidget(self.newNameInput)
        # Create a horizontal layout for the new document directory input
        self.newHorizontal = QHBoxLayout()
        self.newInput = QLineEdit(self.container)
        self.newInput.setPlaceholderText("Select directory")
        self.newHorizontal.addWidget(self.newInput)
        self.newButton = QToolButton(self.container)
        self.newButton.setText("...")
        self.newButton.clicked.connect(self.onNewButton)
        self.newHorizontal.addWidget(self.newButton)
        self.verticalLayout_7.addLayout(self.newHorizontal)
        # Create a radio button for creating a new document
        self.radioCurrent = QRadioButton(self.container)
        self.radioCurrent.setText("Save current document")
        self.radioCurrent.setEnabled(bool(FreeCAD.ActiveDocument))
        self.verticalLayout_7.addWidget(self.radioCurrent)
        # Create label that is shown only if no active document
        self.noActiveDocumentLabel = QLabel(self.container)
        self.noActiveDocumentLabel.setText("No active document")
        self.noActiveDocumentLabel.setVisible(not bool(FreeCAD.ActiveDocument))
        self.noActiveDocumentLabel.setStyleSheet("color: #ff9999; font-style: italic; font-size: 10px;")
        self.verticalLayout_7.addWidget(self.noActiveDocumentLabel)
        # Create a line edit for the current document name input
        self.currentNameInput = QLineEdit(self.container)
        self.currentNameInput.setText("")
        self.currentNameInput.setPlaceholderText("Document name")
        self.currentNameInput.setEnabled(bool(FreeCAD.ActiveDocument))
        self.verticalLayout_7.addWidget(self.currentNameInput)
        # Create a horizontal layout for the current document directory input
        self.currentHorizontal = QHBoxLayout()
        self.currentInput = QLineEdit(self.container)
        self.currentInput.setPlaceholderText("Select directory")
        self.currentHorizontal.addWidget(self.currentInput)
        self.currentButton = QToolButton(self.container)
        self.currentButton.setText("...")
        self.currentButton.setEnabled(bool(FreeCAD.ActiveDocument))
        self.currentButton.clicked.connect(self.onCurrentButton)
        self.currentHorizontal.addWidget(self.currentButton)
        self.verticalLayout_7.addLayout(self.currentHorizontal)
        # Create a vertical spacer for the Dialog
        self.verticalSpacer = QSpacerItem(20, 181, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.verticalLayout_7.addItem(self.verticalSpacer)
        # Create a horizontal layout for the Dialog buttons
        self.horizontalLayout_12 = QHBoxLayout()
        self.horizontalSpacer = QSpacerItem(37, 17, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.horizontalLayout_12.addItem(self.horizontalSpacer)
        self.cancelButton = QPushButton(self.container)
        self.cancelButton.setText("Cancel")
        self.cancelButton.clicked.connect(self.onCancel)
        self.horizontalLayout_12.addWidget(self.cancelButton)
        self.okButton = QPushButton(self.container)
        self.okButton.setText("OK")
        self.okButton.clicked.connect(self.onOk)
        self.horizontalLayout_12.addWidget(self.okButton)
        self.verticalLayout_7.addLayout(self.horizontalLayout_12)
        # Add the container frame to the horizontal layout of the Dialog
        self.horizontalLayout.addWidget(self.container)
    
    def onOk(self):
        """
        Depending on which radio is selected, it opens or creates (and saves)
        a FreeCAD document
        """
        if self.radioExisting.isChecked():
            directoryWithName = self.existingInput.text()
            if not directoryWithName:
                FreeCAD.Console.PrintError("No directory selected\n")
                return
            directory = directoryWithName[:directoryWithName.rfind("/")]
            FreeCAD.Console.PrintMessage(f"Opening existing document from {directoryWithName}\n")
            FreeCAD.openDocument(directoryWithName)
        elif self.radioNew.isChecked():
            directory = self.newInput.text()
            documentName = self.newNameInput.text()
            directoryWithName = f"{directory}/{documentName}.FCStd"
            if not directory:
                FreeCAD.Console.PrintError("No directory selected\n")
                return
            if not documentName:
                FreeCAD.Console.PrintError("No document name selected\n")
                return
            FreeCAD.Console.PrintMessage(f"Creating new document {documentName} in {directoryWithName}\n")
            FreeCAD.newDocument(documentName)
            FreeCAD.setActiveDocument(documentName)
            # TODO: Document is not saving correctly (manual save is needed)
            FreeCAD.ActiveDocument.saveAs(directoryWithName)
        else:
            directory = self.currentInput.text()
            documentName = self.currentNameInput.text()
            directoryWithName = f"{directory}/{documentName}.FCStd"
            if not directory:
                FreeCAD.Console.PrintError("No directory selected\n")
                return
            if not documentName:
                FreeCAD.Console.PrintError("No document name selected\n")
                return
            FreeCAD.Console.PrintMessage(f"Saving current document {documentName} in {directoryWithName}\n")
            # TODO: Document is not saving correctly (manual save is needed)
            FreeCAD.ActiveDocument.saveAs(directoryWithName)

        # Save document path in workbench
        self.workbench.setDocumentPath(directory) # TODO: ¿remove?
        self.workbench.setExportPath(directory)

        # Load or create workbench settings
        if bool(FreeCAD.activeDocument()):
            if bool(FreeCAD.activeDocument().getObject(CONFIG_GROUP)):
                configGroup = FreeCAD.activeDocument().getObject(CONFIG_GROUP)
                self.workbench.loadWorkbenchSettings(configGroup)
            else:
                self.workbench.saveWorkbenchSettings()

        self.close()

    def onCancel(self):
        """
        It closes the dialog
        """
        FreeCAD.Console.PrintError("Need to select an existing document or save one to use this workbench\n")
        self.close()

    def onNewButton(self):
        """
        Set directory where is going to be created the new document
        """
        directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        if (directory):
            FreeCAD.Console.PrintMessage(f"Setting new document path to {directory}\n")
            self.newInput.setText(directory)
    
    def onExistingButton(self):
        """
        Set filePath where is the document that is going to be opened
        """
        filePath, _ = QFileDialog.getOpenFileName(None, "Select a file to import", "", "FreeCAD Files (*.FCStd)")
        if (filePath):
            FreeCAD.Console.PrintMessage(f"Setting existing document path to {filePath}\n")
            self.existingInput.setText(filePath)
    
    def onCurrentButton(self):
        """
        Set directory where is going to be saved the current document
        """
        directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        if (directory):
            FreeCAD.Console.PrintMessage(f"Setting current document path to {directory}\n")
            self.currentInput.setText(directory)
