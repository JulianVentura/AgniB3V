from PySide2.QtWidgets import *
from PySide2.QtCore import *
from ui.WidgetMaterials import WidgetMaterials

class DialogMaterialEditor(QDialog):
    """
    Dialog to edit materials
    """

    def __init__(self, workbench):
        super().__init__()

        self.workbench = workbench
        self.initUI()

    def initUI(self):
        # create our window
        self.setWindowTitle("Material Editor")
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.setMinimumWidth(600)
        self.setMinimumHeight(400)
        self.horizontalLayout = QHBoxLayout(self)
        self.frame = QFrame(self)
        self.horizontalLayout_2 = QHBoxLayout(self.frame)

        self.materialEditor = WidgetMaterials(self.frame, self.workbench, self.onClose)

        self.horizontalLayout_2.addWidget(self.materialEditor)
        self.horizontalLayout.addWidget(self.frame)    
        self.show()

    def onClose(self):
        """Closes the dialog"""
        self.workbench.saveWorkbenchSettings()
        self.close()
