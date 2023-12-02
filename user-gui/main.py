from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
from pages.landing import LandingWidget
from pages.project import ProjectWidget
from pages.newProject import NewProjectWidget
from pages.configuration import ConfigurationWidget
from utils.appState import AppState

class PagesWidget(QStackedWidget):
    def __init__(self):
        super().__init__()
        self.addWidget(LandingWidget(self))
        self.addWidget(NewProjectWidget(self))
        self.addWidget(ProjectWidget(self))
        self.addWidget(ConfigurationWidget(self))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.loadTranslations()
        self.setWindowTitle("ThermalB3V")
        self.resize(800, 600)
        self.setCentralWidget(PagesWidget())
        self.show()

    def loadTranslations(self):
        translator = QTranslator()
        locale = QLocale.system().name()
        if translator.load(f"translations/thermal_{locale}"):
            QCoreApplication.installTranslator(translator)

if __name__ == "__main__":
    AppState()
    app = QApplication([])
    window = MainWindow()
    app.exec_()