import csv
import sys
import pandas as pd
import matplotlib.pyplot as plt
from PySide6.QtCore import Slot
# from datetime import datetime
from PySide6.QtWidgets import (QApplication, QFormLayout, QHBoxLayout, QMainWindow, QPushButton,
                               QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QFileDialog,
                               QCalendarWidget, QListWidget, QAbstractItemView, QMessageBox)
from PyQt6.QtCore import QStandardPaths


class Widget(QWidget):
    def __init__(self):
        super().__init__()
        self.items = 0
        self._data = self.procesar_csv()
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
        return f"{str(fecha[2]).zfill(2)}/{str(fecha[1]).zfill(2)}/{str(fecha[0]).zfill(2)}"

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
        self.df = pd.read_csv(self.file, delimiter=dialect.delimiter, skiprows=1)

        return self.df

    def procesar_csv(self):
        # Leer el archivo CSV sin encabezados
        df = self.add_element()

        # Asigna los nombres de las columnas
        df.columns = ['columna 1', 'pH bocatoma', 'pH salida', 'Macro 1', 'Macro 2', 'Macro 3', 'Macro 4', 'Sensor de nivel']

        # Ahora puedes dividir la primera columna (que ahora se llama 'columna1')
        df[['fecha', 'hora']] = df['columna 1'].str.split(' ', expand=True)

        # eliminar la columna original
        df = df.drop(columns=['columna 1'])

        dfnuevo = df.iloc[:, :-2]
        dfnuevo = dfnuevo.apply(pd.to_numeric)
        dfnuevo = dfnuevo / 100

        df[dfnuevo.columns] = dfnuevo

        # Reordena las columnas para que 'fecha' y 'hora' sean las dos primeras
        df = df[['fecha', 'hora'] + [c for c in df.columns if c not in ['fecha', 'hora']]]

        # Convierte la fecha al formato deseado
        df['fecha'] = pd.to_datetime(df['fecha']).dt.strftime('%d/%m/%Y')

        # Asegúrate de que la hora esté en el formato correcto
        df['hora'] = pd.to_datetime(df['hora'], format='%H:%M:%S').dt.time

        df['Q T -entrada'] = df['Macro 1'] + df['Macro 2']
        df['Q T -entrada'] = df['Q T -entrada'].round(2)
        df['Q T -salida'] = df['Macro 3'] + df['Macro 4']
        df['Q T -salida'] = df['Q T -salida'].round(2)
        # Agrega una nueva columna que es la suma del dato actual y el dato anterior en 'Macro 1+2'
        df['V horario E'] = df['Q T -entrada'] + df['Q T -entrada'].shift(1)
        df['V horario E'] = df['V horario E'].fillna(df['Q T -entrada'] * 7200 / 1000)


        # Agrega una nueva columna que es la suma del dato actual y el dato anterior en 'Macro 3+4'
        df['V horario S'] = df['Q T -salida'] + df['Q T -salida'].shift(1)
        df['V horario S'] = df['V horario S'].fillna(df['Q T -salida'] * 7200 / 1000)


        # Multiplica todas las filas excepto la primera por 3,6 en 'Macro 1+2 acumulado'
        df.loc[1:, 'V horario E'] *= 3.6
        df['V horario E'] = df['V horario E'].round(2)

        # Multiplica todas las filas excepto la primera por 3,6 en 'Macro 3+4 acumulado'
        df.loc[1:, 'V horario S'] *= 3.6
        df['V horario S'] = df['V horario S'].round(2)

        # Crea una nueva columna que es la suma del dato de la fila anterior y la resta de 'Macro 1+2 acumulado' y 'Macro 3+4 acumulado'
        df['V regulacion'] = df['V horario E'] - df['V horario S']
        df['V real'] = df['V regulacion']
        df['V regulacion'] = df['V regulacion'].shift(1) + df['V regulacion']
        df['V regulacion'] = df['V regulacion'].round(2)
        df['V real'] = df['V real'].shift(1) + df['V real']
        df['V real'] = df['V real'].round(2)

        return df

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




    @Slot()
    def plot_data(self):
        columnas_visibles = [i for i in range(self.table.columnCount() - 1) if not self.table.isColumnHidden(i)]
        filas_visibles = [i for i in range(self.table.rowCount()) if not self.table.isRowHidden(i)]

        eje_x = self.df['Hora'][filas_visibles]
        headers = self.df.columns
        encabezados = [headers[i] for i in columnas_visibles if i > 1]

        try:
            for h in encabezados:
                dato = self.df[h][filas_visibles]
                plt.plot(eje_x, dato.tolist(), label=h, marker="o", linestyle="None")
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
