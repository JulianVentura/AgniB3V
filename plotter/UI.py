import sys
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QComboBox,
    QFileDialog,
    QInputDialog,
)
from PyQt5.QtCore import Qt, QTimer
from plotter import (
    plot_all_temperatures,
    parse_results_vtk_series,
    plot_temperature_by_id,
    plot_average_temperature,
    plot_std_temperature,
)
import os


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(50, 50, 50, 50)

        self.label = QLabel("Select a graph type:")
        self.label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.label)

        self.combo_box = QComboBox()
        self.combo_box.addItems(
            [
                "All Temperatures By Time",
                "Temperature By Time",
                "Average Temperature By Time",
                "Standard Deviation By Time",
            ]
        )
        self.layout.addWidget(self.combo_box)

        self.file_button = QPushButton("Choose File")
        self.layout.addWidget(self.file_button, alignment=Qt.AlignCenter)
        self.file_button.clicked.connect(self.open_file_dialog)

        self.button = QPushButton("Show Graph")
        self.layout.addWidget(self.button, alignment=Qt.AlignCenter)
        self.button.clicked.connect(self.show_graph)
        self.button.hide()

        self.loader_label = QLabel("Loading...", self)
        self.loader_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.loader_label)
        self.loader_label.hide()

        self.file_label = QLabel("File Choosen: ", self)
        self.file_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.file_label)
        self.file_label.hide()

        self.setLayout(self.layout)
        self.setWindowTitle("Graph Selector")

        self.results = None

    def show_graph(self):
        graph_type = self.combo_box.currentText()

        if graph_type == "All Temperatures By Time":
            plot_all_temperatures(self.results)
        elif graph_type == "Temperature By Time":
            num, ok = QInputDialog.getInt(self, "ID Selector", "Enter node ID:")
            if ok and num >= 0:
                plot_temperature_by_id(num, self.results)
        elif graph_type == "Average Temperature By Time":
            plot_average_temperature(self.results)
        elif graph_type == "Standard Deviation By Time":
            plot_std_temperature(self.results)

    def open_file_dialog(self):
        self.loader_label.show()
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Choose the .vtk.series file",
            "",
            "All Files (*);;Python Files (*.py)",
            options=options,
        )
        if file_name:
            self.results = parse_results_vtk_series(
                os.path.dirname(file_name), os.path.basename(file_name), self.progress
            )[0]
            self.file_label.setText("File Choosen: " + file_name)
            self.file_label.show()
            self.button.show()
        self.loader_label.hide()

    def progress(self, percentage):
        percentage = int(percentage)
        self.loader_label.setText(f"Loading... {percentage} %")
        self.loader_label.show()
        QApplication.processEvents()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")  # Use Fusion style
    window = MainWindow()
    window.setGeometry(100, 100, 400, 200)  # Set a fixed size for the window
    window.show()
    sys.exit(app.exec_())
