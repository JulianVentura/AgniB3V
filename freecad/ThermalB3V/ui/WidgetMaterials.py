from PySide2.QtWidgets import *

class WidgetMaterials(QWidget):
    """
    Class that represents the "Materials" section
    """
    def __init__(self, parent):
        super().__init__(parent)
    
    def InitUI(self):
        self.materials = QWidget()
