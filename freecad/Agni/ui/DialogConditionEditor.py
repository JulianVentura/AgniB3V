from PySide2.QtWidgets import *
from PySide2.QtCore import *
from ui.WidgetConditions import WidgetConditions

class DialogConditionEditor(QDialog):
    """
    Dialog to edit conditions
    """

    def __init__(self, workbench):
        super().__init__()

        self.workbench = workbench
        self.initUI()

    def initUI(self):
        # create our window
        self.setWindowTitle("Condition Editor")
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.setMinimumWidth(600)
        self.setMinimumHeight(400)
        self.horizontalLayout = QHBoxLayout(self)
        self.frame = QFrame(self)
        self.horizontalLayout_2 = QHBoxLayout(self.frame)

        self.conditionEditor = WidgetConditions(self.frame, self.workbench, self.onClose)

        self.horizontalLayout_2.addWidget(self.conditionEditor)
        self.horizontalLayout.addWidget(self.frame)    
        self.show()

    def onClose(self):
        """Closes the dialog"""
        self.workbench.saveWorkbenchSettings()
        self.close()
