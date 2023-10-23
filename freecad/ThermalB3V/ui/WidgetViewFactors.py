from PySide2.QtWidgets import *

class WidgetViewFactors(QWidget):
    """
    Class that represents the "View Factors" section
    """
    def __init__(self, parent):
        super().__init__(parent)
        self.InitUI()
    
    def InitUI(self):
        self.view_factors = QWidget()