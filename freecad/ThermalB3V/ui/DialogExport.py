from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

from ui.WidgetExportable import WidgetExportable
from ui.WidgetGlobalProperties import WidgetGlobalProperties
from ui.WidgetViewFactors import WidgetViewFactors
from ui.WidgetMaterials import WidgetMaterials

class DialogExport(QDialog):
    """
    Dialog to show preprocess result before exporting
    """

    def __init__(self, workbench, onExport):
        """
        Initialize the dialog.
        It receives the workbench and the onExport callback.
        """
        super().__init__()

        self.workbench = workbench
        self.onExport = onExport
        self.initUI()

    def initUI(self):
        """
        Initialize the UI
        """
        self.setWindowTitle("Global Properties")
        self.setWindowFlags(Qt.WindowStaysOnTopHint)

        # Create sections
        exportableSection = WidgetExportable(
            self,
            self.workbench.getExportPath(),
            self.workbench.setExportPath,
            self.onCancel,
            self.onExport,
        )
        globalPropertiesSection = WidgetGlobalProperties(
            self,
            self.workbench,
            self.onCancel
        )
        viewFactorsSection = WidgetViewFactors(
            self,
            self.workbench,
            self.onCancel,
        )
        materialsSection = WidgetMaterials(self)

        self.horizontalLayout = QHBoxLayout(self)
        self.frame = QFrame(self)
        self.horizontalLayout_2 = QHBoxLayout(self.frame)

        self.tabWidget = QTabWidget(self.frame)
        self.addTabs(
            (exportableSection, "Exportable"),
            (globalPropertiesSection, "Prop. Globales"),
            (viewFactorsSection, "Factores de Vista"),
            (materialsSection, "Materiales"),
        )
        self.horizontalLayout_2.addWidget(self.tabWidget)
        self.horizontalLayout.addWidget(self.frame)    
        self.tabWidget.setCurrentIndex(0)

        self.show()

    def addTabs(self, *args):
        """
        Add tabs to the tab widget
        """
        for (tab, title) in args:
            self.tabWidget.addTab(tab, title)
    
    def onCancel(self):
        """
        Close the dialog
        """
        self.workbench.saveWorkbenchSettings()
        self.close()
