import sys
import pandas as pd
import matplotlib.pyplot as plt
from PySide6.QtCore import Slot
from datetime import datetime, timedelta
from PySide6.QtWidgets import (QApplication, QFormLayout, QHBoxLayout, QMainWindow, QPushButton,
                               QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QFileDialog,
                               QCalendarWidget, QListWidget, QAbstractItemView)
from PyQt6.QtCore import QStandardPaths


class Widget(QWidget):
    def __init__(self):
        super().__init__()
        self.items = 0
        self._data = self.add_element()
        self._dataStats = self.add_stats()
        # Left
        self.table = QTableWidget()
        self.table.setColumnCount(len(self._data.columns))
        self.table.setRowCount(len(self._data.index))
        self.columnas = ['pH salida', 'pH bocatoma', 'Cloro residual', 'Dosificacion de cloro',
                         'Bascula 1', 'Bascula 2', 'Detector de fugas', 'Turbiedad', 'Macro 1', 'Macro 2',
                         'Macro 3', 'Macro 4', 'Sensor de nivel']
        self.table.setHorizontalHeaderLabels(
            ['Fecha', 'Hora', 'pH salida', 'pH bocatoma', 'Cloro residual', 'Dosificacion de cloro',
             'Bascula 1', 'Bascula 2', 'Detector de fugas', 'Turbiedad', 'Macro 1', 'Macro 2',
             'Macro 3', 'Macro 4', 'Sensor de nivel'])
        # self.table.horizontalHeader().setSectionResizeMode(QHeaderView.style())
        self.table_stats = QTableWidget()
        #self.table_stats.setColumnCount(len(self._dataStats.columns))
        #self.table_stats.setRowCount(len(self._dataStats.index))


        # Chart
        # self.chart_view = QChartView()
        # self.chart_view.setRenderHint(QPainter.Antialiasing)
        # self.chart = QChart()

        self.limpiar = QPushButton("Limpiar")
        self.clear = QPushButton("Clear")
        self.plot = QPushButton("Plot")

        # Calendar
        self.calendar = QCalendarWidget()
        self.calendar.setFixedSize(320, 250)
        self.calendar.clicked.connect(self.check_calendar)

        # List widget
        self.list_vars = QListWidget()
        self.list_vars.setFixedSize(220, 250)
        self.list_vars.addItems(self.columnas)
        self.list_vars.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        self.list_vars.clicked.connect(self.lista_filtro)

        self.right = QVBoxLayout()
        self.right_right = QHBoxLayout()
        self.form_layout = QFormLayout()
        self.form_layout.addWidget(self.table)
        # self.right.addLayout(self.form_layout)
        self.right_right.addWidget(self.calendar)
        self.right_right.addWidget(self.list_vars)
        self.right.addLayout(self.right_right)
        self.right.addWidget(self.limpiar)
        self.right.addWidget(self.plot)
        self.right.addWidget(self.table_stats)
        self.right.addWidget(self.clear)

        # QWidget Layout
        self.layout = QHBoxLayout(self)
        self.layout.addWidget(self.table)
        self.layout.addLayout(self.right)

        # Signals and Slots
        self.limpiar.clicked.connect(self.limpiar_filtros)
        self.plot.clicked.connect(self.plot_data)
        # self.clear.clicked.connect(self.clear_table)

        # Fill example data
        self.fill_table()

    def modificar_fecha(self, fecha):
        fecha = fecha[::-1]
        fecha2 = []
        for f in fecha:
            lol = str(f)
            if len(lol) > 1:
                pass
            else:
                lol = '0' + lol
            fecha2.append(lol)
        fecha3 = fecha2[0] + '/' + fecha2[1] + '/' + fecha2[2]
        return fecha3

    def obtener_fechas(self):
        # Obtener la fecha actual
        fecha_actual = datetime.now()

        # Crear una lista para almacenar las listas de días pasados de los últimos 11 meses
        meses_dias_pasados = []

        # Calcular y agregar las listas de días pasados de los últimos 11 meses
        for _ in range(11):
            year = fecha_actual.year
            month = fecha_actual.month

            # Calcular el número de días pasados en el mes actual
            dias_pasados = fecha_actual.day - 1

            meses_dias_pasados.append({
                'mes': fecha_actual.strftime('%B'),
                'año': year,
                'días_pasados': dias_pasados
            })

            # Retroceder al mes anterior
            fecha_actual = fecha_actual.replace(day=1) - timedelta(days=1)


        return meses_dias_pasados


    @Slot()
    def limpiar_filtros(self):
        columnas = self.table.columnCount()
        filas = self.table.rowCount()
        for i in range(columnas):
            self.table.showColumn(i)
        for i in range(filas):
            self.table.showRow(i)

        self.list_vars.reset()

    @Slot()
    def add_element(self):
        options = QFileDialog.Option.DontUseNativeDialog
        initial_dir = QStandardPaths.writableLocation(
            QStandardPaths.StandardLocation.DocumentsLocation
        )
        file_types = "Csv files (*.csv)"
        self.file, _ = QFileDialog.getOpenFileName(self, "Open File", initial_dir, file_types)

        self.df = pd.read_csv(self.file)
        dias = 0

        for mes_info in self.obtener_fechas():
            dias = dias + mes_info['días_pasados']
        print(dias)
        return self.df

    def add_stats(self):
        fechas = self.obtener_fechas()



    @Slot()
    def check_calendar(self):
        fecha = self.calendar.selectedDate().getDate()
        fecha3 = self.modificar_fecha(fecha)
        num_row = self.table.rowCount()

        for i in range(num_row):
            fecha4 = self.table.item(i, 0).text()
            if fecha4 == fecha3:
                self.table.showRow(i)
            else:
                self.table.hideRow(i)
        print(fecha3)

    @Slot()
    def lista_filtro(self):
        indices = {'pH salida': 2, 'pH bocatoma': 3, 'Cloro residual': 4, 'Dosificacion de cloro': 5,
                   'Bascula 1': 6, 'Bascula 2': 7, 'Detector de fugas': 8, 'Turbiedad': 9, 'Macro 1': 10, 'Macro 2': 11,
                   'Macro 3': 12, 'Macro 4': 13, 'Sensor de nivel': 14}
        ls_seleccionados = self.list_vars.selectedItems()
        for indice in indices:
            self.table.hideColumn(indices[indice])
        for item in ls_seleccionados:
            self.table.showColumn(indices[item.text()])

    def fill_table(self, data=None):
        data = self._data if not data else data
        for i in range(len(self._data.index)):
            for j in range(len(self._data.columns)):
                item = self._data.iloc[i, j]
                self.table.setItem(i, j, QTableWidgetItem(str(item)))

    @Slot()
    def plot_data(self):
        columnas = self.table.columnCount()
        filas = self.table.rowCount()
        columnas_visibles = []
        filas_visibles = []

        for i in range(columnas):
            if self.table.isColumnHidden(i):
                pass
            else:
                columnas_visibles.append(i)
        for i in range(filas):
            if self.table.isRowHidden(i):
                pass
            else:
                filas_visibles.append(i)
        eje_x = self.df['Hora'][filas_visibles]
        headers = self.df.columns
        encabezados = []

        for i in columnas_visibles:
            encabezados.append(headers[i])
        del encabezados[0]
        del encabezados[0]

        plt.figure(layout='constrained')
        plt.style.use("Solarize_Light2")
        for h in encabezados:
            dato = self.df[h][filas_visibles]
            plt.plot(eje_x, dato.tolist(), label=h)
        plt.xlabel("Horas")
        plt.ylabel("Magnitud")
        plt.title("Grafica de variables")
        plt.legend()
        dato = []
        plt.show()


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
    window.resize(1080, 840)
    window.show()

    # Execute application
    sys.exit(app.exec())
