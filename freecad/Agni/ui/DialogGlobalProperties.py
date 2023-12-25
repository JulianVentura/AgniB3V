from PySide2.QtWidgets import *
from PySide2.QtCore import *
from ui.WidgetGlobalProperties import WidgetGlobalProperties

class DialogGlobalProperties(QDialog):
    """
    Dialog to set global properties
    """

    def __init__(self, workbench):
        super().__init__()

        self.workbench = workbench
        self.initUI()

    def initUI(self):
        # create our window
        self.setWindowTitle("Global Properties")
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.setMinimumWidth(400)
        self.horizontalLayout = QHBoxLayout(self)
        self.frame = QFrame(self)
        self.horizontalLayout_2 = QHBoxLayout(self.frame)

        self.globalProperties = WidgetGlobalProperties(self.frame, self.workbench, self.onClose)

        self.horizontalLayout_2.addWidget(self.globalProperties)
        self.horizontalLayout.addWidget(self.frame)    
        self.show()

    def onClose(self):
        """Closes the dialog"""
        self.workbench.saveWorkbenchSettings()
        self.close()
