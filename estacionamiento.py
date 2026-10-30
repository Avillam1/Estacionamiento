import sys
import json
import math
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                             QTableWidget, QTableWidgetItem, QMessageBox, 
                             QHeaderView, QTabWidget, QDateTimeEdit)
from PyQt5.QtCore import Qt, QDateTime

class EstacionamientoApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistema de Gestión de Estacionamiento v4.0")
        self.setGeometry(100, 100, 950, 750)
        
        self.archivo_json = 'estacionamiento.json'
        
        self.cargar_datos()
        self.initUI()
        self.aplicar_estilos()

    def aplicar_estilos(self):
        estilo = """
            QMainWindow { background-color: #f0f2f5; }
            QLabel { font-size: 14px; color: #333; }
            QLabel#titulo { font-size: 18px; font-weight: bold; color: #2c3e50; padding: 5px 0px; }
            QLabel#estadisticas { font-size: 16px; font-weight: bold; color: #16a085; }
            QLineEdit, QDateTimeEdit { padding: 8px; border: 1px solid #bdc3c7; border-radius: 4px; font-size: 14px; background-color: white; }
            QLineEdit:focus, QDateTimeEdit:focus { border: 2px solid #3498db; }
            QPushButton { color: white; border-radius: 4px; padding: 10px; font-size: 14px; font-weight: bold; }
            QPushButton#btn_entrada { background-color: #27ae60; }
            QPushButton#btn_entrada:hover { background-color: #2ecc71; }
            QPushButton#btn_salida { background-color: #e74c3c; }
            QPushButton#btn_salida:hover { background-color: #e67e22; }
            QPushButton#btn_guardar { background-color: #34495e; }
            QPushButton#btn_guardar:hover { background-color: #4f5f6f; }
            QPushButton#btn_calcular { background-color: #2980b9; }
            QPushButton#btn_calcular:hover { background-color: #3498db; }
            QTableWidget { background-color: white; gridline-color: #ecf0f1; border: 1px solid #bdc3c7; border-radius: 4px;}
            QHeaderView::section { background-color: #34495e; color: white; padding: 5px; font-weight: bold; border: none; }
            QTabWidget::pane { border: 1px solid #bdc3c7; background: white; border-radius: 4px; }
            QTabBar::tab { background: #ecf0f1; padding: 10px 20px; margin-right: 2px; border-top-left-radius: 4px; border-top-right-radius: 4px; }
            QTabBar::tab:selected { background: #3498db; color: white; font-weight: bold; }
        """
        self.setStyleSheet(estilo)

    def initUI(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout_principal = QVBoxLayout(central_widget)

        # Sistema de pestañas
        self.tabs = QTabWidget()
        self.tab_operaciones = QWidget()
        self.tab_historial = QWidget()
        self.tab_config = QWidget()
        
        self.tabs.addTab(self.tab_operaciones, "🚗 Operaciones")
        self.tabs.addTab(self.tab_historial, "📊 Historial y Finanzas")
        self.tabs.addTab(self.tab_config, "⚙️ Configuración y Divisas")

        self.configurar_tab_operaciones()
        self.configurar_tab_historial()
        self.configurar_tab_config()

        layout_principal.addWidget(self.tabs)
        
        # Barra de estado inferior
        self.label_estado = QLabel("Puestos disponibles: Calculando...")
        self.label_estado.setObjectName("estadisticas")
        layout_principal.addWidget(self.label_estado)
        
        self.actualizar_interfaz()

    def configurar_tab_operaciones(self):
        layout = QVBoxLayout(self.tab_operaciones)
        layout_controles = QHBoxLayout()
        
        # Panel Entrada
        layout_entrada = QVBoxLayout()
        lbl_in = QLabel("REGISTRO DE ENTRADA")
        lbl_in.setObjectName("titulo")
        layout_entrada.addWidget(lbl_in)
        
        self.input_placa_in = QLineEdit()
        self.input_placa_in.setPlaceholderText("Placa (Ej. ABC-123)")
        self.input_Carro = QLineEdit()
        self.input_Carro.setPlaceholderText("Carro")
        
        # Nuevo Selector de Fecha/Hora de Entrada
        layout_entrada.addWidget(QLabel("Fecha/Hora de Entrada:"))
        self.input_hora_in = QDateTimeEdit(QDateTime.currentDateTime())
        self.input_hora_in.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
        self.input_hora_in.setCalendarPopup(True)
        layout_entrada.addWidget(self.input_hora_in)
        
        btn_entrada = QPushButton("✅ Registrar Entrada")
        btn_entrada.setObjectName("btn_entrada")
        btn_entrada.clicked.connect(self.registrar_entrada)
        
        layout_entrada.addWidget(self.input_placa_in)
        layout_entrada.addWidget(self.input_Carro)
        layout_entrada.addWidget(btn_entrada)
        layout_entrada.addStretch()

        # Panel Salida
        layout_salida = QVBoxLayout()
        lbl_out = QLabel("REGISTRO DE SALIDA")
        lbl_out.setObjectName("titulo")
        layout_salida.addWidget(lbl_out)
        
        self.input_placa_out = QLineEdit()
        self.input_placa_out.setPlaceholderText("Placa a retirar")
        
        # Nuevo Selector de Fecha/Hora de Salida
        layout_salida.addWidget(QLabel("Fecha/Hora de Salida:"))
        self.input_hora_out = QDateTimeEdit(QDateTime.currentDateTime())
        self.input_hora_out.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
        self.input_hora_out.setCalendarPopup(True)
        layout_salida.addWidget(self.input_hora_out)
        
        btn_salida = QPushButton("💳 Procesar Salida y Cobrar")
        btn_salida.setObjectName("btn_salida")
        btn_salida.clicked.connect(self.registrar_salida)
        
        layout_salida.addWidget(self.input_placa_out)
        layout_salida.addWidget(btn_salida)
        layout_salida.addStretch()

        layout_controles.addLayout(layout_entrada)
        layout_controles.addSpacing(40)
        layout_controles.addLayout(layout_salida)
        
        # Tabla de Activos
        self.tabla_vehiculos = QTableWidget(0, 3) 
        self.tabla_vehiculos.setHorizontalHeaderLabels(["Placa", "Carro", "Hora de Entrada"])
        self.tabla_vehiculos.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla_vehiculos.setEditTriggers(QTableWidget.NoEditTriggers)
        
        layout.addLayout(layout_controles)
        lbl_activos = QLabel("VEHÍCULOS ACTUALMENTE ESTACIONADOS")
        lbl_activos.setObjectName("titulo")
        layout.addWidget(lbl_activos)
        layout.addWidget(self.tabla_vehiculos)

    def configurar_tab_historial(self):
        layout = QVBoxLayout(self.tab_historial)
        
        self.label_ingresos = QLabel("Ingresos Totales: $0.00 | Bs. 0.00")
        self.label_ingresos.setObjectName("estadisticas")
        layout.addWidget(self.label_ingresos)

        self.tabla_historial = QTableWidget(0, 5)
        self.tabla_historial.setHorizontalHeaderLabels(["Placa", "Carro", "Entrada", "Salida", "Cobrado ($)"])
        self.tabla_historial.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla_historial.setEditTriggers(QTableWidget.NoEditTriggers)
        
        layout.addWidget(self.tabla_historial)

    def configurar_tab_config(self):
        layout = QHBoxLayout(self.tab_config)
        
        # Ajustes del Sistema
        col_izquierda = QVBoxLayout()
        lbl_ajustes = QLabel("AJUSTES DE TARIFAS Y TASAS")
        lbl_ajustes.setObjectName("titulo")
        col_izquierda.addWidget(lbl_ajustes)
        
        col_izquierda.addWidget(QLabel("Tarifa por Hora (USD $):"))
        self.input_tarifa = QLineEdit()
        col_izquierda.addWidget(self.input_tarifa)
        
        col_izquierda.addWidget(QLabel("Tasa de Cambio del Dólar (Bs. / $):"))
        self.input_tasa = QLineEdit()
        col_izquierda.addWidget(self.input_tasa)
        
        btn_guardar_config = QPushButton("💾 Guardar Configuración")
        btn_guardar_config.setObjectName("btn_guardar")
        btn_guardar_config.clicked.connect(self.guardar_configuracion)
        col_izquierda.addWidget(btn_guardar_config)
        col_izquierda.addStretch()
        
        # Calculadora Rápida
        col_derecha = QVBoxLayout()
        lbl_calc = QLabel("CALCULADORA RÁPIDA DE DIVISAS")
        lbl_calc.setObjectName("titulo")
        col_derecha.addWidget(lbl_calc)
        
        col_derecha.addWidget(QLabel("Monto en Dólares ($):"))
        self.input_calc_usd = QLineEdit()
        self.input_calc_usd.setPlaceholderText("Ej. 10.50")
        col_derecha.addWidget(self.input_calc_usd)
        
        btn_calcular = QPushButton("🧮 Calcular a Bolívares")
        btn_calcular.setObjectName("btn_calcular")
        btn_calcular.clicked.connect(self.calcular_divisas)
        col_derecha.addWidget(btn_calcular)
        
        self.label_resultado_calc = QLabel("Resultado: Bs. 0.00")
        self.label_resultado_calc.setObjectName("titulo")
        col_derecha.addWidget(self.label_resultado_calc)
        col_derecha.addStretch()
        
        layout.addLayout(col_izquierda)
        layout.addSpacing(60)
        layout.addLayout(col_derecha)

    def cargar_datos(self):
        try:
            with open(self.archivo_json, 'r') as file:
                self.datos = json.load(file)
                if "historial" not in self.datos:
                    self.datos["historial"] = []
                if "configuracion" not in self.datos:
                    self.datos["configuracion"] = {}
                if "tarifa_por_hora" not in self.datos["configuracion"]:
                    self.datos["configuracion"]["tarifa_por_hora"] = 2.50
                if "tasa_bolivar" not in self.datos["configuracion"]:
                    self.datos["configuracion"]["tasa_bolivar"] = 36.50
        except FileNotFoundError:
            self.datos = {
                "configuracion": {"capacidad_maxima": 50, "tarifa_por_hora": 2.50, "tasa_bolivar": 36.50}, 
                "vehiculos_activos": {},
                "historial": []
            }
            self.guardar_datos()

    def guardar_datos(self):
        with open(self.archivo_json, 'w') as file:
            json.dump(self.datos, file, indent=4)

    def actualizar_interfaz(self):
        config = self.datos["configuracion"]
        if not self.input_tarifa.hasFocus():
            self.input_tarifa.setText(str(config["tarifa_por_hora"]))
        if not self.input_tasa.hasFocus():
            self.input_tasa.setText(str(config["tasa_bolivar"]))

        vehiculos = self.datos.get("vehiculos_activos", {})
        self.tabla_vehiculos.setRowCount(0) 
        for row, (placa, info) in enumerate(vehiculos.items()):
            self.tabla_vehiculos.insertRow(row)
            self.tabla_vehiculos.setItem(row, 0, QTableWidgetItem(placa))
            self.tabla_vehiculos.setItem(row, 1, QTableWidgetItem(info["Carro"]))
            self.tabla_vehiculos.setItem(row, 2, QTableWidgetItem(info["hora_entrada"]))

        capacidad = config.get("capacidad_maxima", 50)
        ocupados = len(vehiculos)
        self.label_estado.setText(f"🚗 Puestos ocupados: {ocupados} | 🟢 Disponibles: {capacidad - ocupados} de {capacidad}")

        historial = self.datos.get("historial", [])
        self.tabla_historial.setRowCount(0)
        ingresos_usd = 0.0

        for row, registro in enumerate(reversed(historial)):
            self.tabla_historial.insertRow(row)
            self.tabla_historial.setItem(row, 0, QTableWidgetItem(registro["placa"]))
            self.tabla_historial.setItem(row, 1, QTableWidgetItem(registro["Carro"]))
            self.tabla_historial.setItem(row, 2, QTableWidgetItem(registro["hora_entrada"]))
            self.tabla_historial.setItem(row, 3, QTableWidgetItem(registro["hora_salida"]))
            
            cobro_usd = registro["total_pagado"]
            ingresos_usd += cobro_usd
            
            item_cobro = QTableWidgetItem(f"${cobro_usd:.2f}")
            item_cobro.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.tabla_historial.setItem(row, 4, item_cobro)

        ingresos_bs = ingresos_usd * config["tasa_bolivar"]
        self.label_ingresos.setText(f"💰 Ingresos Totales: ${ingresos_usd:.2f} | Bs. {ingresos_bs:.2f}")

    def guardar_configuracion(self):
        try:
            nueva_tarifa = float(self.input_tarifa.text().strip())
            nueva_tasa = float(self.input_tasa.text().strip())
            
            if nueva_tarifa < 0 or nueva_tasa <= 0:
                raise ValueError
                
            self.datos["configuracion"]["tarifa_por_hora"] = nueva_tarifa
            self.datos["configuracion"]["tasa_bolivar"] = nueva_tasa
            self.guardar_datos()
            self.actualizar_interfaz()
            self.mostrar_alerta("Éxito", "Configuración de tarifas y tasas actualizada correctamente.")
        except ValueError:
            self.mostrar_alerta("Error", "Por favor introduce valores numéricos válidos.")

    def calcular_divisas(self):
        try:
            monto_usd = float(self.input_calc_usd.text().strip())
            tasa_actual = self.datos["configuracion"]["tasa_bolivar"]
            resultado_bs = monto_usd * tasa_actual
            self.label_resultado_calc.setText(f"Resultado: Bs. {resultado_bs:.2f}")
        except ValueError:
            self.mostrar_alerta("Error", "Introduce un monto numérico válido en dólares.")

    def mostrar_alerta(self, titulo, mensaje):
        msg = QMessageBox()
        msg.setWindowTitle(titulo)
        msg.setText(mensaje)
        msg.exec_()

    def registrar_entrada(self):
        placa = self.input_placa_in.text().strip().upper()
        Carro = self.input_Carro.text().strip()
        
        if not placa or not Carro:
            self.mostrar_alerta("Error", "Por favor, llena todos los campos.")
            return
            
        if placa in self.datos["vehiculos_activos"]:
            self.mostrar_alerta("Error", "Este vehículo ya está registrado.")
            return

        capacidad = self.datos["configuracion"].get("capacidad_maxima", 50)
        if len(self.datos["vehiculos_activos"]) >= capacidad:
            self.mostrar_alerta("Aviso", "El estacionamiento está lleno.")
            return

        # Captura la fecha y hora configurada manualmente en el widget
        hora_entrada_usuario = self.input_hora_in.dateTime().toPyDateTime().strftime("%Y-%m-%d %H:%M:%S")
        
        self.datos["vehiculos_activos"][placa] = {
            "Carro": Carro,
            "hora_entrada": hora_entrada_usuario
        }
        
        self.guardar_datos()
        self.actualizar_interfaz()
        
        self.input_placa_in.clear()
        self.input_Carro.clear()
        # Refrescar los selectores a la hora actual del sistema
        self.input_hora_in.setDateTime(QDateTime.currentDateTime())
        self.input_hora_out.setDateTime(QDateTime.currentDateTime())
        self.input_placa_in.setFocus()

    def registrar_salida(self):
        placa = self.input_placa_out.text().strip().upper()
        
        if not placa:
            return
            
        if placa not in self.datos["vehiculos_activos"]:
            self.mostrar_alerta("Error", "No se encontró la placa en el estacionamiento.")
            return

        vehiculo = self.datos["vehiculos_activos"][placa]
        formato_fecha = "%Y-%m-%d %H:%M:%S"
        
        # Recupera la entrada del JSON y lee la salida seleccionada manualmente en el widget
        hora_entrada = datetime.strptime(vehiculo["hora_entrada"], formato_fecha)
        hora_salida = self.input_hora_out.dateTime().toPyDateTime()
        
        # Validación de consistencia temporal
        if hora_salida < hora_entrada:
            self.mostrar_alerta("Error", "La hora de salida no puede ser anterior a la hora de entrada.")
            return
        
        diferencia = hora_salida - hora_entrada
        horas_totales = math.ceil(diferencia.total_seconds() / 3600)
        if horas_totales == 0: horas_totales = 1 
            
        tarifa_usd = self.datos["configuracion"]["tarifa_por_hora"]
        tasa_bs = self.datos["configuracion"]["tasa_bolivar"]
        
        total_usd = horas_totales * tarifa_usd
        total_bs = total_usd * tasa_bs

        registro_historial = {
            "placa": placa,
            "Carro": vehiculo["Carro"],
            "hora_entrada": vehiculo["hora_entrada"],
            "hora_salida": hora_salida.strftime(formato_fecha),
            "total_pagado": total_usd
        }
        self.datos["historial"].append(registro_historial)

        del self.datos["vehiculos_activos"][placa]
        self.guardar_datos()
        self.actualizar_interfaz()
        self.input_placa_out.clear()
        
        # Refrescar selectores
        self.input_hora_in.setDateTime(QDateTime.currentDateTime())
        self.input_hora_out.setDateTime(QDateTime.currentDateTime())

        recibo = (f"🚗 Vehículo: {placa}\n"
                  f"👤 Carro: {vehiculo['Carro']}\n"
                  f"⏱️ Tiempo facturado: {horas_totales} hora(s)\n"
                  f"----------------------------------------\n"
                  f"💵 TOTAL A COBRAR (USD): ${total_usd:.2f}\n"
                  f"🇻🇪 TOTAL A COBRAR (BS):  Bs. {total_bs:.2f}\n\n"
                  f"(Tasa aplicada: Bs. {tasa_bs:.2f} por $)")
                  
        self.mostrar_alerta("Recibo de Salida Procesado", recibo)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle("Fusion") 
    ventana = EstacionamientoApp()
    ventana.show()
    sys.exit(app.exec_())
