import csv
import sys
import pandas as pd
import matplotlib.pyplot as plt
from PySide6.QtCore import Slot
from datetime import datetime
from PySide6.QtWidgets import (QApplication, QFormLayout, QHBoxLayout, QMainWindow, QPushButton,
                               QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QFileDialog,
                               QCalendarWidget, QListWidget, QAbstractItemView, QMessageBox)
from PyQt6.QtCore import QStandardPaths


class Widget(QWidget):
    def __init__(self):
        super().__init__()
        self.items = 0
        self._data = self.add_element()
        self._dataStats = self.fecha_columna()
        # Left
        self.table = QTableWidget()
        self.table.setColumnCount(len(self._data.columns))
        self.table.setRowCount(len(self._data.index))
        self.columnas = ['pH bocatoma', 'pH salida', 'Macro 1', 'Macro 2', 'Q T -entrada',
                         'Macro 3', 'Macro 4', 'Q T -salida', 'Sensor de nivel', 'V horario E',
                         'V horario S', 'V regulacion', 'V real']
        self.table.setHorizontalHeaderLabels(['Fecha', 'Hora', 'pH bocatoma', 'pH salida', 'Macro 1',
                                              'Macro 2', 'Q T -entrada', 'Macro 3', 'Macro 4', 'Q T -salida',
                                              'Sensor de nivel', 'V horario E', 'V horario S', 'V regulacion',
                                              'V real'])
        # self.table.horizontalHeader().setSectionResizeMode(QHeaderView.style())
        self.table_stats = QTableWidget()
        self.table_stats.setColumnCount(len(self.columnas))
        self.table_stats.setHorizontalHeaderLabels(self.columnas)
        self.table_stats.setRowCount(len(self._dataStats.index))


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
        self.fill_table_stats()

    def modificar_fecha(self, fecha):
        return datetime.strftime(datetime(fecha[2], fecha[1], fecha[0]), '%d/%m/%Y')

    def obtener_fechas(self):
        # Obtener la fecha actual
        fecha_actual = pd.Timestamp.now()

        # Crear una lista para almacenar las listas de días pasados de los últimos 11 meses
        meses_dias_pasados = []

        # Calcular y agregar las listas de días pasados de los últimos 11 meses
        for mes in pd.date_range(fecha_actual - pd.DateOffset(months=11), fecha_actual, freq='M'):
            meses_dias_pasados.append({
                'mes': mes.strftime('%B'),
                'año': mes.year,
                'días_pasados': (fecha_actual - mes).days
            })

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

        with open(self.file, 'r') as f:
            dialect = csv.Sniffer().sniff(f.read())
        self.df = pd.read_csv(self.file, delimiter=dialect.delimiter)

        return self.df

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
        indices = {'pH bocatoma': 2, 'pH salida': 3, 'Macro 1': 4, 'Macro 2': 5, 'Q T -entrada': 6,
                         'Macro 3': 7, 'Macro 4': 8, 'Q T -salida': 9, 'Sensor de nivel': 10, 'V horario E': 11,
                         'V horario S': 12, 'V regulacion': 13, 'V real': 14}
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

    def fecha_columna(self):
        data = self._data[['Fecha']].to_dict()
        mes = []
        for d in range(len(data['Fecha'])):
            fecha = data['Fecha'][d]
            partes = fecha.split("/")
            del partes[0]
            mes.append(partes[0] + "/" + partes[1])
        copia = self._data
        copia['mes'] = mes
        self.mes_sinrepetir = set(mes)
        return copia[copia['mes'] == '08/2023']

    def fill_table_stats(self, data=None):
        data = self.fecha_columna() if not data else data
        data = pd.DataFrame(data)
        data = data.drop(['Fecha', 'Hora'], axis=1)
        columnas = list(data.columns)
        col = columnas.pop()
        num_filas = len(self.mes_sinrepetir)
        self.table_stats.setHorizontalHeaderLabels(columnas)
        self.table_stats.setRowCount(num_filas)
        promedio = pd.DataFrame(data[data['mes'].isin(['08/2023'])])
        #promedio.set_index('mes')
        pro = promedio[columnas].mean()
        n = 0
        for i in range(0, num_filas):
            for j in columnas:
                self.table_stats.setItem(i, n, QTableWidgetItem(str(pro[j])))
                n = n + 1




    @Slot()
    def plot_data(self):
        columnas = self.table.columnCount()
        filas = self.table.rowCount()
        columnas_visibles = []
        filas_visibles = []

        for i in range(columnas - 1):
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

        try:
            for h in encabezados:
                dato = self.df[h][filas_visibles]
                plt.plot(eje_x, dato.tolist(), label=h)
            plt.xlabel("Horas")
            plt.ylabel("Magnitud")
            plt.title("Gráfica de variables")
            plt.xticks(eje_x, rotation=90, fontsize=6)
            plt.legend()
            plt.show()
        except Exception as e:
            print(e)
            QMessageBox.warning(self, "Error", "Seleccione al menos una variable para graficar.")

        if len(encabezados) == 0:
            QMessageBox.warning(self, "Error", "Seleccione al menos una variable para graficar.")


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
