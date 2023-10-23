from PySide2.QtWidgets import *

class WidgetViewFactors(QWidget):
    """
    Class that represents the "View Factors" section
    """
    def __init__(self):
        super().__init__()
        self.InitUI()
    
    def InitUI(self):
        self.view_factors = QWidget()