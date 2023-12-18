import sys
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QComboBox,
    QFileDialog,
    QInputDialog,
    QMessageBox,
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QTimer
from plotter import (
    plot_all_temperatures,
    parse_results_vtk_series,
    parse_results_xls,
    parse_results_xml,
    plot_temperature_by_id,
    plot_average_temperature,
    plot_std_temperature,
)
import os


class MainWindow(QWidget):
    def __init__(self, initial_file_path=None):
        super().__init__()

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(50, 50, 50, 50)

        self.label = QLabel("Select a graph type:")
        self.label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.label)

        self.combo_box = QComboBox()
        self.combo_box.addItems(
            [
                "All Temperatures Over Time",
                "Temperature Over Time",
                "Average Temperature Over Time",
                "Standard Deviation Over Time",
            ]
        )
        self.layout.addWidget(self.combo_box)

        self.file_button = QPushButton("Choose File")
        self.layout.addWidget(self.file_button, alignment=Qt.AlignCenter)
        self.file_button.clicked.connect(self.open_file_dialog)

        reload_icon = QIcon.fromTheme("view-refresh")
        self.reload_button = QPushButton(reload_icon, "Reload")
        self.layout.addWidget(self.reload_button, alignment=Qt.AlignCenter)
        self.reload_button.clicked.connect(self.reload)
        self.reload_button.hide()

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
        self.file = initial_file_path

    def load_initial(self):
        """
        Loads the initial data and results based on the selected file.
        If a file is selected, it retrieves the results and updates the UI accordingly.
        """
        if self.file:
            self.get_results(self.file)
            self.loader_label.hide()
            self.reload_button.show()

    def show_graph(self):
        """
        Displays a graph based on the selected graph type.

        The graph type is determined by the current text of the combo box.
        The available graph types are:
        - "All Temperatures Over Time": Plots all temperatures over time.
        - "Temperature Over Time": Plots the temperature over time for a specific node ID.
        - "Average Temperature Over Time": Plots the average temperature over time.
        - "Standard Deviation Over Time": Plots the standard deviation of temperatures over time.
        """
        graph_type = self.combo_box.currentText()

        if graph_type == "All Temperatures Over Time":
            plot_all_temperatures(self.results)
        elif graph_type == "Temperature Over Time":
            num, ok = QInputDialog.getInt(self, "ID Selector", "Enter node ID:")
            if ok and num >= 0:
                plot_temperature_by_id(num, self.results)
        elif graph_type == "Average Temperature Over Time":
            plot_average_temperature(self.results)
        elif graph_type == "Standard Deviation Over Time":
            plot_std_temperature(self.results)

    def open_file_dialog(self):
        """
        Opens a file dialog to choose a .vtk.series file.
        After selecting the file, it calls the get_results method with the selected file name.
        """
        self.loader_label.show()
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Choose the .vtk.series file",
            "",
            "All Files (*);;Python Files (*.py)",
            options=options,
        )
        self.get_results(file_name)

        self.loader_label.hide()
        self.reload_button.show()

    def progress(self, percentage):
        """
        Update the progress label with the given percentage.

        Args:
            percentage (int): The progress percentage.

        Returns:
            None
        """
        percentage = int(percentage)
        self.loader_label.setText(f"Loading... {percentage} %")
        self.loader_label.show()
        QApplication.processEvents()

    def reload(self):
        """
        Reloads the results from the specified file and updates the UI.
        """
        self.loader_label.show()
        file_name = self.file
        self.get_results(file_name)
        self.loader_label.hide()

    def get_results(self, file_name):
        """
        Retrieves and parses the results from the specified file.

        Args:
            file_name (str): The name of the file to retrieve the results from.

        Raises:
            Exception: If the file type is invalid.

        Returns:
            None
        """
        if file_name:
            try:
                extension = os.path.splitext(file_name)[1]
                if extension == ".series":
                    self.results = parse_results_vtk_series(
                        os.path.dirname(file_name),
                        os.path.basename(file_name),
                        self.progress,
                    )[0]
                elif extension == ".xlsx":
                    self.results = parse_results_xls(
                        os.path.dirname(file_name),
                        os.path.basename(file_name),
                        self.progress,
                    )[0]
                elif extension == ".xml":
                    self.results = parse_results_xml(
                        os.path.dirname(file_name),
                        os.path.basename(file_name),
                        self.progress,
                    )[0]
                else:
                    raise Exception("Invalid file type")
                self.file = file_name
                self.file_label.setText("Chosen File: " + file_name)
                self.file_label.show()
                self.button.show()
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error",
                    e.args[0],
                )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")  # Use Fusion style
    initial_file_path = None
    if len(sys.argv) > 1:
        initial_file_path = sys.argv[1]
    window = MainWindow(initial_file_path)
    window.setGeometry(100, 100, 400, 200)  # Set a fixed size for the window
    window.show()
    window.load_initial()
    sys.exit(app.exec_())
