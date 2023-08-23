import sys
import pandas as pd
from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import (QApplication, QFormLayout,
                               QHBoxLayout, QLineEdit, QMainWindow,
                               QPushButton, QTableWidget, QTableWidgetItem,
                               QVBoxLayout, QWidget, QFileDialog)
from PySide6.QtCharts import QChartView, QPieSeries, QChart
from PyQt6.QtCore import QStandardPaths


class Widget(QWidget):
    def __init__(self):
        super().__init__()
        self.items = 0
        self._data = self.add_element()
        # Left
        self.table = QTableWidget()
        self.table.setColumnCount(len(self._data.columns))
        self.table.setRowCount(len(self._data.index))
        self.table.setHorizontalHeaderLabels(['Fecha', 'Hora', 'pH salida', 'pH bocatoma', 'Cloro residual', 'Dosificacion de cloro',
                    'Bascula 1', 'Bascula 2', 'Detector de fugas', 'Turbiedad', 'Macro 1', 'Macro 2',
                    'Macro 3', 'Macro 4', 'Sensor de nivel'])
        #self.table.horizontalHeader().setSectionResizeMode(QHeaderView.style())

        # Chart
        self.chart_view = QChartView()
        self.chart_view.setRenderHint(QPainter.Antialiasing)

        # Right
        self.description = QLineEdit()
        self.description.setClearButtonEnabled(True)
        self.price = QLineEdit()
        self.price.setClearButtonEnabled(True)

        self.add = QPushButton("Add")
        self.clear = QPushButton("Clear")
        self.plot = QPushButton("Plot")

        # Disabling 'Add' button
        self.add.setEnabled(False)

        self.right = QVBoxLayout()
        self.form_layout = QFormLayout()
        self.form_layout.addWidget(self.table)
        self.right.addLayout(self.form_layout)
        self.right.addWidget(self.add)
        self.right.addWidget(self.plot)
        self.right.addWidget(self.chart_view)
        self.right.addWidget(self.clear)

        # QWidget Layout
        self.layout = QHBoxLayout(self)
        self.layout.addWidget(self.table)
        self.layout.addLayout(self.right)

        # Signals and Slots
        self.add.clicked.connect(self.add_element)
        self.plot.clicked.connect(self.plot_data)
        self.clear.clicked.connect(self.clear_table)
        self.description.textChanged.connect(self.check_disable)
        self.price.textChanged.connect(self.check_disable)

        # Fill example data
        self.fill_table()

    @Slot()
    def add_element(self):
        options = QFileDialog.Option.DontUseNativeDialog
        initial_dir = QStandardPaths.writableLocation(
            QStandardPaths.StandardLocation.DocumentsLocation
        )
        file_types = "Csv files (*.csv)"
        self.file, _ = QFileDialog.getOpenFileName(self, "Open File", initial_dir, file_types)

        self.df = pd.read_csv(self.file)
        return self.df


    @Slot()
    def check_disable(self, s):
        enabled = bool(self.description.text() and self.price.text())
        self.add.setEnabled(enabled)

    @Slot()
    def plot_data(self):
        # Get table information
        series = QPieSeries()
        for i in range(self.table.rowCount()):
            text = self.table.item(i, 0).text()
            number = self.table.item(i, 1).text()
            series.append(text, number)

        chart = QChart()
        chart.addSeries(series)
        chart.legend().setAlignment(Qt.AlignLeft)
        self.chart_view.setChart(chart)

    def fill_table(self, data=None):
        data = self._data if not data else data
        for i in range(len(self._data.index)):
            for j in range(len(self._data.columns)):
                item = self._data.iloc[i, j]
                self.table.setItem(i, j, QTableWidgetItem(str(item)))

    @Slot()
    def clear_table(self):
        self.table.setRowCount(0)
        self.items = 0


class MainWindow(QMainWindow):
    def __init__(self, widget):
        super().__init__()
        self.setWindowTitle("Tutorial")

        # Menu
        self.menu = self.menuBar()
        self.file_menu = self.menu.addMenu("File")

        # Exit QAction
        exit_action = self.file_menu.addAction("Exit", self.close)
        exit_action.setShortcut("Ctrl+Q")

        self.setCentralWidget(widget)


if __name__ == "__main__":
    # Qt Application
    app = QApplication(sys.argv)
    # QWidget
    widget = Widget()
    # QMainWindow using QWidget as central widget
    window = MainWindow(widget)
    window.resize(800, 600)
    window.show()

    # Execute application
    sys.exit(app.exec())