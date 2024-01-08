from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
from pages.landing import LandingWidget
from pages.project import ProjectWidget
from pages.newProject import NewProjectWidget
from pages.globalProperties import GlobalPropertiesWidget
from utils.appState import AppState

class PagesWidget(QStackedWidget):
    def __init__(self):
        super().__init__()
        self.addWidget(LandingWidget(self))
        self.addWidget(NewProjectWidget(self))
        self.addWidget(ProjectWidget(self))
        self.addWidget(GlobalPropertiesWidget(self))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.loadTranslations()
        self.setWindowTitle("Agni")
        self.resize(800, 600)
        self.setCentralWidget(PagesWidget())
        self.show()

    def closeEvent(self, event):
        AppState().processManager.joinFinishedThreads()
        if AppState().processManager.areThreadsAlive():
            QMessageBox.critical(
                self,
                "Error",
                "Debes cerrar todos los procesos antes de salir.",
                QMessageBox.Ok,
            )
            event.ignore()
            return
        event.accept()

    def loadTranslations(self):
        translator = QTranslator()
        locale = QLocale.system().name()
        if translator.load(f"translations/agni_{locale}"):
            QCoreApplication.installTranslator(translator)

if __name__ == "__main__":
    AppState()
    app = QApplication([])
    window = MainWindow()
    app.exec_()
