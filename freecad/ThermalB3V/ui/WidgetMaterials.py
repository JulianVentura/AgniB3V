from PySide2.QtWidgets import *

class WidgetMaterials(QWidget):
    """
    Class that represents the "Materials" section
    """
    def __init__(self):
        super().__init__()
        self.InitUI()
    
    def InitUI(self):
        self.materials = QWidget()
