import sys
import pandas as pd
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QTableWidget, QTableWidgetItem, QLabel, QPushButton, QComboBox, QMessageBox
)
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super().__init__(fig)

class InventarioApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistema de Consultoría de Inventario - UGB")
        self.setGeometry(100, 100, 1100, 700)

        # Cargar y analizar datos con Pandas
        self.cargar_datos()
        self.init_ui()

    def cargar_datos(self):
        try:
            self.df = pd.read_csv("inventario_sucursales.csv")
            # Funciones de inspección requeridas (se imprimen en la terminal de VS Code)
            print("=== INFORME DE INSPECCIÓN PANDAS ===")
            print("\n1. Estructura general (.info()):")
            print(self.df.info())
            print("\n2. Tipos de datos (.dtypes):")
            print(self.df.dtypes)
            print("\n3. Estadísticas descriptivas (.describe()):")
            print(self.df.describe())
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo cargar el archivo CSV: {e}")
            sys.exit(1)

    def init_ui(self):
        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)

        # Panel izquierdo: Filtros y Tabla
        left_layout = QVBoxLayout()
        left_layout.addWidget(QLabel("<b>Inventario General por Sucursales</b>"))

        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Filtrar Sucursal:"))
        self.combo_sucursal = QComboBox()
        self.combo_sucursal.addItem("Todas")
        self.combo_sucursal.addItems(self.df["Sucursal"].unique())
        self.combo_sucursal.currentIndexChanged.connect(self.actualizar_vista)
        filter_layout.addWidget(self.combo_sucursal)
        left_layout.addLayout(filter_layout)

        self.table = QTableWidget()
        left_layout.addWidget(self.table)
        self.llenar_tabla(self.df)

        main_layout.addLayout(left_layout, stretch=1)

        # Panel derecho: Gráfico Matplotlib
        right_layout = QVBoxLayout()
        right_layout.addWidget(QLabel("<b>Visualización de Stock por Sucursal</b>"))
        
        self.canvas = MplCanvas(self, width=5, height=4, dpi=100)
        right_layout.addWidget(self.canvas)
        self.generar_grafico(self.df)

        main_layout.addLayout(right_layout, stretch=1)
        self.setCentralWidget(main_widget)

    def llenar_tabla(self, dataframe):
        self.table.setRowCount(len(dataframe))
        self.table.setColumnCount(len(dataframe.columns))
        self.table.setHorizontalHeaderLabels(dataframe.columns)

        for i in range(len(dataframe)):
            for j in range(len(dataframe.columns)):
                self.table.setItem(i, j, QTableWidgetItem(str(dataframe.iat[i, j])))
        self.table.resizeColumnsToContents()

    def generar_grafico(self, dataframe):
        self.canvas.axes.clear()
        stock_sucursal = dataframe.groupby("Sucursal")["Stock"].sum()
        
        sucursales = stock_sucursal.index
        stocks = stock_sucursal.values

        # Paleta de colores variados para cada barra
        colores_disponibles = ['#1f77b4', '#27ae60', '#e74c3c', '#f39c12', '#8e44ad']
        # Tomamos tantos colores como barras se vayan a mostrar
        colores_usados = colores_disponibles[:len(sucursales)]

        self.canvas.axes.bar(sucursales, stocks, color=colores_usados)
        self.canvas.axes.set_title("Stock Total por Sucursal")
        self.canvas.axes.set_xlabel("Sucursal")
        self.canvas.axes.set_ylabel("Unidades")
        self.canvas.axes.tick_params(axis='x', rotation=15)
        self.canvas.figure.tight_layout()
        self.canvas.draw()

    def actualizar_vista(self):
        seleccion = self.combo_sucursal.currentText()
        if seleccion == "Todas":
            df_filtrado = self.df
        else:
            df_filtrado = self.df[self.df["Sucursal"] == seleccion]
        
        self.llenar_tabla(df_filtrado)
        self.generar_grafico(df_filtrado)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = InventarioApp()
    window.show()
    sys.exit(app.exec_())