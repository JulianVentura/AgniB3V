from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
import subprocess

class ProjectWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.setupUi()

    def setupUi(self):
        self.verticalLayout = QVBoxLayout(self)
        self.frame = QFrame(self)
        self.frame.setFrameShape(QFrame.StyledPanel)
        self.frame.setFrameShadow(QFrame.Raised)
        self.verticalLayout_5 = QVBoxLayout(self.frame)
        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.label = QLabel(self.frame)
        font = QFont()
        font.setPointSize(24)
        self.label.setFont(font)
        self.label.setText(QCoreApplication.translate("Dialog", u"Thermal B3V", None))

        self.horizontalSpacer_4 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.verticalLayout_2 = QVBoxLayout()
        self.label_2 = QLabel(self.frame)
        self.label_2.setText(QCoreApplication.translate("Dialog", u"Modelado", None))

        self.horizontalLayout = QHBoxLayout()
        self.pushButton = QPushButton(self.frame)
        self.pushButton.setText(QCoreApplication.translate("Dialog", u"FreeCAD", None))
        self.pushButton.clicked.connect(self.openFreeCAD)

        self.pushButton_2 = QPushButton(self.frame)
        self.pushButton_2.setText(QCoreApplication.translate("Dialog", u"GMAT", None))
        self.pushButton_2.clicked.connect(self.openGMAT)

        self.pushButton_3 = QPushButton(self.frame)
        self.pushButton_3.setText(QCoreApplication.translate("Dialog", u"Visualizar Materiales", None))
        self.pushButton_3.clicked.connect(self.visualizeMaterials)

        self.verticalLayout_3 = QVBoxLayout()
        self.label_3 = QLabel(self.frame)
        self.label_3.setText(QCoreApplication.translate("Dialog", u"Procesamiento", None))

        self.horizontalLayout_2 = QHBoxLayout()
        self.pushButton_4 = QPushButton(self.frame)
        self.pushButton_4.setText(QCoreApplication.translate("Dialog", u"Calcular Factores de Vista", None))
        self.pushButton_4.clicked.connect(self.calculateViewFactors)

        self.pushButton_5 = QPushButton(self.frame)
        self.pushButton_5.setText(QCoreApplication.translate("Dialog", u"Realizar Simulaci\u00f3n", None))
        self.pushButton_5.clicked.connect(self.runSimulation)

        self.pushButton_6 = QPushButton(self.frame)
        self.pushButton_6.setText(QCoreApplication.translate("Dialog", u"Calcular FV y Realizar Simulaci\u00f3n", None))
        self.pushButton_6.clicked.connect(self.calculateViewFactorsAndRunSimulation)

        self.verticalLayout_4 = QVBoxLayout()
        self.label_4 = QLabel(self.frame)
        self.label_4.setText(QCoreApplication.translate("Dialog", u"Postprocesamiento", None))

        self.horizontalLayout_3 = QHBoxLayout()
        self.pushButton_7 = QPushButton(self.frame)
        self.pushButton_7.setText(QCoreApplication.translate("Dialog", u"ParaView", None))
        self.pushButton_7.clicked.connect(self.openParaView)

        self.pushButton_8 = QPushButton(self.frame)
        self.pushButton_8.setText(QCoreApplication.translate("Dialog", u"Plotter", None))
        self.pushButton_8.clicked.connect(self.openPlotter)

        self.horizontalLayout_4.addItem(self.horizontalSpacer_3)
        self.horizontalLayout_4.addWidget(self.label)
        self.horizontalLayout_4.addItem(self.horizontalSpacer_4)
        self.verticalLayout_5.addLayout(self.horizontalLayout_4)
        self.verticalLayout_2.addWidget(self.label_2)
        self.horizontalLayout.addWidget(self.pushButton)
        self.horizontalLayout.addWidget(self.pushButton_2)
        self.horizontalLayout.addWidget(self.pushButton_3)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        self.verticalLayout_5.addLayout(self.verticalLayout_2)
        self.verticalLayout_3.addWidget(self.label_3)
        self.horizontalLayout_2.addWidget(self.pushButton_4)
        self.horizontalLayout_2.addWidget(self.pushButton_5)
        self.horizontalLayout_2.addWidget(self.pushButton_6)
        self.verticalLayout_3.addLayout(self.horizontalLayout_2)
        self.verticalLayout_5.addLayout(self.verticalLayout_3)
        self.verticalLayout_4.addWidget(self.label_4)
        self.horizontalLayout_3.addWidget(self.pushButton_7)
        self.horizontalLayout_3.addWidget(self.pushButton_8)
        self.verticalLayout_4.addLayout(self.horizontalLayout_3)
        self.verticalLayout_5.addLayout(self.verticalLayout_4)
        self.verticalLayout.addWidget(self.frame)

    def openFreeCAD(self):
        """
        Opens FreeCAD application.
        """
        print("Opening FreeCAD")
        subprocess.Popen(["Freecad"])

    def openGMAT(self):
        """
        Opens GMAT application.
        """
        pass

    def visualizeMaterials(self):
        """
        Opens material visualization.
        """
        pass

    def calculateViewFactors(self):
        """
        Calculates view factors.
        """
        pass

    def runSimulation(self):
        """
        Runs solver simulation.
        """
        pass

    def calculateViewFactorsAndRunSimulation(self):
        """
        Calculates view factors and runs solver simulation.
        """
        pass

    def openParaView(self):
        """
        Opens ParaView application.
        """
        pass

    def openPlotter(self):
        """
        Opens plotter application.
        """
        pass
