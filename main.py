#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import time
from PyQt5.QtWidgets import (QApplication, QMainWindow, QFileDialog, QTableWidgetItem,
                             QMessageBox, QSplitter, QHBoxLayout, QWidget, QVBoxLayout,
                             QLabel, QProgressBar)
from PyQt5.QtGui import QColor, QSyntaxHighlighter, QTextCharFormat, QBrush, QFont, QIcon
from PyQt5.QtCore import QRegExp, Qt, QSize, QTimer

# Importar nuestros componentes
from vista.home import Ui_home
from analizador_lexico import prueba, tabla_simbolos
from analizador_sintactico import prueba_sintactica
from arbol_derivacion import construir_arbol_derivacion
from visualizador_arbol_mejorado import visualizar_arbol_derivacion_mejorado


# Resaltador de sintaxis para Java mejorado
class JavaHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super(JavaHighlighter, self).__init__(parent)

        self.highlighting_rules = []

        # Formato para palabras clave
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("#569CD6"))
        keyword_format.setFontWeight(QFont.Bold)

        # Palabras clave de Java
        java_keywords = [
            "abstract", "assert", "boolean", "break", "byte", "case", "catch",
            "char", "class", "const", "continue", "default", "do", "double",
            "else", "enum", "extends", "final", "finally", "float", "for", "if",
            "implements", "import", "instanceof", "int", "interface", "long",
            "native", "new", "package", "private", "protected", "public", "return",
            "short", "static", "strictfp", "super", "switch", "synchronized",
            "this", "throw", "throws", "transient", "try", "void", "volatile", "while"
        ]

        for keyword in java_keywords:
            pattern = QRegExp("\\b" + keyword + "\\b")
            rule = (pattern, keyword_format)
            self.highlighting_rules.append(rule)

        # Formato para tipos de dato
        type_format = QTextCharFormat()
        type_format.setForeground(QColor("#4EC9B0"))
        type_format.setFontWeight(QFont.Bold)

        # Tipos primitivos y comunes
        types = ["String", "Object", "List", "Map", "Set"]
        for type_name in types:
            pattern = QRegExp("\\b" + type_name + "\\b")
            rule = (pattern, type_format)
            self.highlighting_rules.append(rule)

        # Formato para literales
        literal_format = QTextCharFormat()
        literal_format.setForeground(QColor("#B5CEA8"))

        # true, false, null
        literals = ["true", "false", "null"]
        for literal in literals:
            pattern = QRegExp("\\b" + literal + "\\b")
            rule = (pattern, literal_format)
            self.highlighting_rules.append(rule)

        # Formato para números
        number_format = QTextCharFormat()
        number_format.setForeground(QColor("#B5CEA8"))
        pattern = QRegExp("\\b[0-9]+\\b")
        rule = (pattern, number_format)
        self.highlighting_rules.append(rule)

        # Formato para cadenas
        string_format = QTextCharFormat()
        string_format.setForeground(QColor("#CE9178"))
        pattern = QRegExp("\".*\"")
        pattern.setMinimal(True)
        rule = (pattern, string_format)
        self.highlighting_rules.append(rule)

        # Formato para caracteres
        char_format = QTextCharFormat()
        char_format.setForeground(QColor("#CE9178"))
        pattern = QRegExp("'.'")
        rule = (pattern, char_format)
        self.highlighting_rules.append(rule)

        # Formato para comentarios de una línea
        singleline_comment_format = QTextCharFormat()
        singleline_comment_format.setForeground(QColor("#608B4E"))
        pattern = QRegExp("//[^\n]*")
        rule = (pattern, singleline_comment_format)
        self.highlighting_rules.append(rule)

        # Formato para comentarios multilinea
        self.multiline_comment_format = QTextCharFormat()
        self.multiline_comment_format.setForeground(QColor("#608B4E"))

        self.comment_start_expression = QRegExp("/\\*")
        self.comment_end_expression = QRegExp("\\*/")

    def highlightBlock(self, text):
        # Aplicar reglas de resaltado
        for pattern, format in self.highlighting_rules:
            expression = QRegExp(pattern)
            index = expression.indexIn(text)
            while index >= 0:
                length = expression.matchedLength()
                self.setFormat(index, length, format)
                index = expression.indexIn(text, index + length)

        # Procesar comentarios multilinea
        self.setCurrentBlockState(0)

        start_index = 0
        if self.previousBlockState() != 1:
            start_index = self.comment_start_expression.indexIn(text)

        while start_index >= 0:
            end_index = self.comment_end_expression.indexIn(text, start_index)

            if end_index == -1:
                self.setCurrentBlockState(1)
                comment_length = len(text) - start_index
            else:
                comment_length = end_index - start_index + self.comment_end_expression.matchedLength()

            self.setFormat(start_index, comment_length, self.multiline_comment_format)
            start_index = self.comment_start_expression.indexIn(text, start_index + comment_length)


class Main(QMainWindow):
    """Clase principal de la aplicación"""

    def __init__(self):
        """Inicialización de la app"""
        QMainWindow.__init__(self)

        # Instanciar la UI
        self.home = Ui_home()
        self.home.setupUi(self)

        # Configurar tema oscuro para la aplicación
        self.setStyleSheet("""
            QMainWindow, QWidget { background-color: #1E1E1E; color: #DCDCDC; }
            QTableWidget { gridline-color: #2D2D30; }
            QHeaderView::section { background-color: #252526; color: #DCDCDC; }
            QPushButton { background-color: #0E639C; color: white; border: none; padding: 5px; }
            QPushButton:hover { background-color: #1177BB; }
            QPushButton:pressed { background-color: #0A4C7D; }
            QTabWidget::pane { border: 1px solid #3E3E42; }
            QTabBar::tab { background-color: #252526; color: #DCDCDC; padding: 6px 10px; }
            QTabBar::tab:selected { background-color: #0E639C; }
            QTreeWidget { border: 1px solid #3E3E42; }
            QTextEdit, QPlainTextEdit { background-color: #1E1E1E; color: #DCDCDC; border: 1px solid #3E3E42; }
        """)

        # Aplicar resaltador de sintaxis de Java
        self.highlighter = JavaHighlighter(self.home.tx_ingreso.document())

        # Conectar eventos
        self.home.bt_lexico.clicked.connect(self.ev_lexico)
        self.home.bt_sintactico.clicked.connect(self.ev_sintactico)
        self.home.bt_archivo.clicked.connect(self.ev_archivo)
        self.home.bt_limpiar.clicked.connect(self.ev_limpiar)
        self.home.bt_simbolos.clicked.connect(self.mostrar_tabla_simbolos)
        self.home.bt_arbol.clicked.connect(self.generar_arbol)

        # Conectar atajos de teclado
        self.home.shortcut_run_lexical.activated.connect(self.ev_lexico)
        self.home.shortcut_run_syntactic.activated.connect(self.ev_sintactico)
        self.home.shortcut_open.activated.connect(self.ev_archivo)
        self.home.shortcut_clear.activated.connect(self.ev_limpiar)
        self.home.shortcut_tree.activated.connect(self.generar_arbol)

        # Mostrar información de la aplicación
        self.home.estado.showMessage("Analizador de código Java - Listo para analizar")

        # Variable para verificar si se ha realizado análisis sintáctico
        self.analisis_sintactico_realizado = False

        # Inicializar una barra de progreso temporal
        self.progress_bar = None

        # Configurar el árbol para que use todo el espacio disponible
        self.home.treeWidget.header().setStretchLastSection(True)
        self.home.treeWidget.setAnimated(True)

        # Mejora visual en tablas
        self.configurar_tablas()

        # Establecer título de la ventana
        self.setWindowTitle("Analizador Java - Visualizador de Árboles de Derivación")

    def configurar_tablas(self):
        """Configura las tablas para mejor visualización"""
        # Tabla léxica
        self.home.tb_lexico.setAlternatingRowColors(False)
        self.home.tb_lexico.horizontalHeader().setStretchLastSection(True)
        self.home.tb_lexico.verticalHeader().setVisible(False)

        # Tabla de símbolos
        self.home.tb_simbolos.setAlternatingRowColors(False)
        self.home.tb_simbolos.horizontalHeader().setStretchLastSection(True)
        self.home.tb_simbolos.verticalHeader().setVisible(False)

    def mostrar_progreso(self, titulo, duracion=2000):
        """Muestra una barra de progreso temporal"""
        # Si ya existe una barra de progreso, la eliminamos
        if self.progress_bar:
            # Aquí está el cambio: usar 'estado' en lugar de 'statusbar'
            self.home.estado.removeWidget(self.progress_bar)

        # Crear nueva barra de progreso
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(100)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat(f"{titulo} %p%")
        self.progress_bar.setValue(0)

        # Añadir a la barra de estado
        self.home.estado.addWidget(self.progress_bar)

        # Simular progreso con un temporizador
        for i in range(1, 101):
            # Convierte explícitamente a entero usando int()
            QTimer.singleShot(int(i * duracion / 100), lambda val=i: self.progress_bar.setValue(val))

        # Eliminar después de completar
        QTimer.singleShot(int(duracion + 100), lambda: self.home.estado.removeWidget(self.progress_bar))

    def ev_lexico(self):
        """
        Manejo del análisis léxico
        """
        self.home.tb_lexico.setRowCount(0)
        codigo = self.home.tx_ingreso.toPlainText().strip()

        if not codigo:
            QMessageBox.warning(self, "Advertencia", "No hay código para analizar.")
            return

        # Mostrar barra de progreso
        self.mostrar_progreso("Análisis léxico en progreso", 1000)

        # Realizar el análisis léxico
        try:
            inicio = time.time()

            # Realizar análisis
            tabla_simbolos.limpiar()
            resultados = prueba(codigo)

            fin = time.time()
            tiempo_analisis = round((fin - inicio) * 1000, 2)  # en milisegundos

            # Llenar la tabla con los resultados
            self.home.tb_lexico.setRowCount(len(resultados))

            # Contadores para estadísticas
            total_tokens = len(resultados)
            tokens_por_tipo = {}
            errores = 0

            # Alternar colores para filas
            usar_fondo_oscuro = True

            for i, token in enumerate(resultados):
                # Alternar colores de fondo para mejorar legibilidad
                if usar_fondo_oscuro:
                    color_fondo = QColor("#1E1E1E")  # Fondo oscuro para filas impares
                    color_texto = QColor("#FFFFFF")  # Texto blanco para fondo oscuro
                else:
                    color_fondo = QColor("#2D2D2D")  # Fondo ligeramente más claro para filas pares
                    color_texto = QColor("#FFFFFF")  # Texto blanco para fondo claro

                usar_fondo_oscuro = not usar_fondo_oscuro  # Alternar para siguiente fila

                # Formato nuevo (diccionario)
                linea = str(token.get("linea", "0"))
                tipo = token.get("tipo", "DESCONOCIDO")
                valor = str(token.get("valor", ""))
                lexema = valor  # El lexema es el valor del token
                patron = self.obtener_patron(tipo)  # Obtener el patrón basado en el tipo

                # Actualizar estadísticas
                if tipo in tokens_por_tipo:
                    tokens_por_tipo[tipo] += 1
                else:
                    tokens_por_tipo[tipo] = 1

                if tipo == "ERROR":
                    color_fondo = QColor("#7E2D40")  # Fondo rojo para errores
                    color_texto = QColor("#FFFFFF")  # Texto blanco para errores
                    errores += 1

                # Crear items para la tabla
                item_linea = QTableWidgetItem(linea)
                item_tipo = QTableWidgetItem(tipo)
                item_lexema = QTableWidgetItem(lexema)
                item_patron = QTableWidgetItem(patron)

                # Aplicar colores
                item_linea.setBackground(QBrush(color_fondo))
                item_tipo.setBackground(QBrush(color_fondo))
                item_lexema.setBackground(QBrush(color_fondo))
                item_patron.setBackground(QBrush(color_fondo))

                item_linea.setForeground(QBrush(color_texto))
                item_tipo.setForeground(QBrush(color_texto))
                item_lexema.setForeground(QBrush(color_texto))
                item_patron.setForeground(QBrush(color_texto))

                # Agregar a la tabla
                self.home.tb_lexico.setItem(i, 0, item_linea)
                self.home.tb_lexico.setItem(i, 1, item_tipo)
                self.home.tb_lexico.setItem(i, 2, item_lexema)
                self.home.tb_lexico.setItem(i, 3, item_patron)

            # Ajustar tamaño de las columnas
            self.home.tb_lexico.resizeColumnsToContents()

            # Mostrar mensaje en la barra de estado
            self.home.estado.showMessage(
                f"Análisis léxico completado: {total_tokens} tokens encontrados | "
                f"{errores} errores | {tiempo_analisis} ms"
            )

            # Cambiar a la pestaña de análisis léxico
            self.home.analysisTabs.setCurrentIndex(0)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error durante el análisis léxico: {str(e)}")
            self.home.estado.showMessage(f"Error: {str(e)}")

    def obtener_patron(self, tipo):
        """
        Devuelve el patrón de expresión regular correspondiente al tipo de token
        """
        patrones = {
            "IDENTIFICADOR": r'[a-zA-Z_][a-zA-Z_0-9]*',
            "ENTERO": r'\d+',
            "DECIMAL": r'\d+\.\d+',
            "CADENA": r'"[^"]*"',
            "CARACTER": r"'[^']'",
            "SUMA": r'\+',
            "RESTA": r'-',
            "MULT": r'\*',
            "DIV": r'/',
            "MODULO": r'%',
            "INCREMENTO": r'\+\+',
            "DECREMENTO": r'--',
            "ASIGNAR": r'=',
            "IGUAL": r'==',
            "MENORQUE": r'<',
            "MAYORQUE": r'>',
            "MENORIGUAL": r'<=',
            "MAYORIGUAL": r'>=',
            "DISTINTO": r'!=',
            "AND": r'&&',
            "OR": r'\|\|',
            "NOT": r'!',
            "PARIZQ": r'\(',
            "PARDER": r'\)',
            "LLAIZQ": r'{',
            "LLADER": r'}',
            "CORIZQ": r'\[',
            "CORDER": r'\]',
            "PUNTOCOMA": r';',
            "COMA": r',',
            "PUNTO": r'\.'
        }

        # Palabras reservadas
        palabras_reservadas = [
            "CLASS", "PUBLIC", "PRIVATE", "PROTECTED", "STATIC", "FINAL",
            "VOID", "INT", "FLOAT", "DOUBLE", "BOOLEAN", "CHAR", "STRING",
            "IF", "ELSE", "FOR", "WHILE", "DO", "SWITCH", "CASE", "DEFAULT",
            "BREAK", "CONTINUE", "RETURN", "SYSTEM", "OUT", "PRINTLN", "PRINT"
        ]

        if tipo in palabras_reservadas:
            return "Palabra reservada"

        return patrones.get(tipo, "Desconocido")

    def ev_sintactico(self):
        """
        Manejo del análisis sintáctico
        """
        # Limpiar el área de texto
        self.home.tx_sintactico.clear()

        # Obtener el código fuente
        codigo = self.home.tx_ingreso.toPlainText().strip()

        if not codigo:
            QMessageBox.warning(self, "Advertencia", "No hay código para analizar.")
            return

        # Mostrar barra de progreso
        self.mostrar_progreso("Análisis sintáctico en progreso", 1500)

        # Realizar el análisis sintáctico
        try:
            inicio = time.time()

            tabla_simbolos.limpiar()
            resultados = prueba_sintactica(codigo)

            fin = time.time()
            tiempo_analisis = round((fin - inicio) * 1000, 2)  # en milisegundos

            # Mostrar los resultados
            html_output = "<html><body style='color:#DCDCDC; font-family: Consolas, monospace;'>"

            # Contar errores y advertencias
            errores = sum(1 for item in resultados if "Error" in item)
            advertencias = sum(1 for item in resultados if "Advertencia" in item)

            for item in resultados:
                if "Error" in item:
                    html_output += f"<p style='color:#FF6B68; margin: 5px 0;'>{item}</p>"
                elif "Advertencia" in item:
                    html_output += f"<p style='color:#FFA500; margin: 5px 0;'>{item}</p>"
                else:
                    html_output += f"<p style='margin: 5px 0;'>{item}</p>"

            html_output += "</body></html>"
            self.home.tx_sintactico.setHtml(html_output)

            # Verificar si hay errores
            tiene_errores = any("Error" in item for item in resultados)

            # Establecer el estado para el árbol de derivación
            self.analisis_sintactico_realizado = not tiene_errores

            # Habilitar o deshabilitar el botón de generar árbol
            self.home.bt_arbol.setEnabled(self.analisis_sintactico_realizado)

            # Mostrar mensaje en la barra de estado
            if tiene_errores:
                self.home.estado.showMessage(
                    f"Análisis sintáctico completado con {errores} errores y {advertencias} advertencias | "
                    f"{tiempo_analisis} ms | No se puede generar árbol."
                )
            else:
                self.home.estado.showMessage(
                    f"Análisis sintáctico completado correctamente | {advertencias} advertencias | "
                    f"{tiempo_analisis} ms | Puede generar el árbol."
                )

            # Cambiar a la pestaña de análisis sintáctico
            self.home.analysisTabs.setCurrentIndex(1)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error durante el análisis sintáctico: {str(e)}")
            self.home.estado.showMessage(f"Error: {str(e)}")
            self.analisis_sintactico_realizado = False
            self.home.bt_arbol.setEnabled(False)

    def generar_arbol(self):
        """
        Genera y muestra el árbol de derivación mejorado
        """
        # Obtener el código fuente
        codigo = self.home.tx_ingreso.toPlainText().strip()

        if not codigo:
            QMessageBox.warning(self, "Advertencia", "No hay código para analizar.")
            return

        # Verificar si se ha realizado el análisis sintáctico
        if not self.analisis_sintactico_realizado:
            respuesta = QMessageBox.question(
                self,
                "Realizar análisis sintáctico",
                "Es necesario realizar un análisis sintáctico antes de generar el árbol. ¿Desea realizar el análisis sintáctico ahora?",
                QMessageBox.Yes | QMessageBox.No
            )

            if respuesta == QMessageBox.Yes:
                self.ev_sintactico()
                # Si hay errores, no continuamos
                if not self.analisis_sintactico_realizado:
                    return
            else:
                return

        # Mostrar barra de progreso
        self.mostrar_progreso("Generando árbol de derivación", 2000)

        # Limpiar el árbol anterior
        self.home.treeWidget.clear()

        # Establecer estilo para el encabezado del árbol
        self.home.treeWidget.setHeaderLabel("Árbol de Derivación Sintáctica")
        header_font = QFont("Consolas", 12, QFont.Bold)
        self.home.treeWidget.headerItem().setFont(0, header_font)
        self.home.treeWidget.headerItem().setForeground(0, QBrush(QColor('#F89406')))  # Naranja

        try:
            inicio = time.time()

            # Generar árbol mejorado
            resultado = visualizar_arbol_derivacion_mejorado(codigo, self.home.treeWidget)

            fin = time.time()
            tiempo_generacion = round((fin - inicio) * 1000, 2)  # en milisegundos

            if not resultado:
                QMessageBox.warning(
                    self,
                    "Error al generar árbol",
                    "No se pudo generar el árbol de derivación debido a errores sintácticos. " +
                    "Corrija los errores antes de intentar generar el árbol."
                )
                return

            # Contar nodos del árbol
            def contar_nodos(item, nivel=0):
                count = 1  # El ítem actual
                max_nivel = nivel
                for i in range(item.childCount()):
                    child_count, child_max_nivel = contar_nodos(item.child(i), nivel + 1)
                    count += child_count
                    max_nivel = max(max_nivel, child_max_nivel)
                return count, max_nivel

            # Contar nodos totales y profundidad máxima
            total_nodos = 0
            profundidad_maxima = 0
            root = self.home.treeWidget.invisibleRootItem()
            for i in range(root.childCount()):
                nodos, prof = contar_nodos(root.child(i))
                total_nodos += nodos
                profundidad_maxima = max(profundidad_maxima, prof)

            # Cambiar a la pestaña del árbol
            self.home.analysisTabs.setCurrentIndex(3)

            # Actualizar la barra de estado
            self.home.estado.showMessage(
                f"Árbol generado: {total_nodos} nodos | Profundidad: {profundidad_maxima} niveles | "
                f"Tiempo: {tiempo_generacion} ms"
            )

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al generar el árbol de derivación: {str(e)}")
            self.home.estado.showMessage(f"Error: {str(e)}")

    def mostrar_tabla_simbolos(self):
        """
        Muestra la tabla de símbolos actual
        """
        # Limpiar la tabla
        self.home.tb_simbolos.setRowCount(0)

        # Obtener la tabla de símbolos actual
        simbolos = tabla_simbolos.obtener_todos()

        if not simbolos:
            self.home.estado.showMessage("No hay símbolos definidos en la tabla de símbolos")
            return

        # Llenar la tabla con los símbolos
        self.home.tb_simbolos.setRowCount(len(simbolos))

        for i, (nombre, info) in enumerate(simbolos.items()):
            # Crear items para cada columna
            item_nombre = QTableWidgetItem(nombre)
            item_tipo = QTableWidgetItem(info.get("tipo", ""))
            item_valor = QTableWidgetItem(str(info.get("valor", "")))
            item_linea = QTableWidgetItem(str(info.get("linea", "")))
            item_alcance = QTableWidgetItem(info.get("alcance", "global"))

            # Aplicar colores basados en el tipo
            if info.get("tipo") == "INT":
                color_fondo = QColor("#143D59")  # Azul oscuro
            elif info.get("tipo") == "FLOAT" or info.get("tipo") == "DOUBLE":
                color_fondo = QColor("#1D566E")  # Azul verdoso
            elif info.get("tipo") == "STRING":
                color_fondo = QColor("#4B1E3F")  # Púrpura oscuro
            elif info.get("tipo") == "BOOLEAN":
                color_fondo = QColor("#2B3A42")  # Gris azulado
            else:
                color_fondo = QColor("#2D2D30")  # Gris oscuro predeterminado

            color_texto = QColor("#FFFFFF")  # Texto blanco

            # Aplicar colores y formato negrita
            item_nombre.setBackground(QBrush(color_fondo))
            item_tipo.setBackground(QBrush(color_fondo))
            item_valor.setBackground(QBrush(color_fondo))
            item_linea.setBackground(QBrush(color_fondo))
            item_alcance.setBackground(QBrush(color_fondo))

            item_nombre.setForeground(QBrush(color_texto))
            item_tipo.setForeground(QBrush(color_texto))
            item_valor.setForeground(QBrush(color_texto))
            item_linea.setForeground(QBrush(color_texto))
            item_alcance.setForeground(QBrush(color_texto))

            # Aplicar formato negrita
            font = item_nombre.font()
            font.setBold(True)
            item_nombre.setFont(font)

            # Alinear valores numéricos a la derecha
            if info.get("tipo") in ["INT", "FLOAT", "DOUBLE"]:
                item_valor.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                item_linea.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)

            # Agregar a la tabla
            self.home.tb_simbolos.setItem(i, 0, item_nombre)
            self.home.tb_simbolos.setItem(i, 1, item_tipo)
            self.home.tb_simbolos.setItem(i, 2, item_valor)
            self.home.tb_simbolos.setItem(i, 3, item_linea)
            self.home.tb_simbolos.setItem(i, 4, item_alcance)

        # Ajustar tamaño de las columnas
        self.home.tb_simbolos.resizeColumnsToContents()

        # Mostrar mensaje en la barra de estado
        self.home.estado.showMessage(f"Tabla de símbolos: {len(simbolos)} símbolos encontrados")

        # Cambiar a la pestaña de la tabla de símbolos
        self.home.analysisTabs.setCurrentIndex(2)

    def ev_archivo(self):
        """
        Manejo de carga de archivos
        """
        opciones = QFileDialog.Options()
        nombre_archivo, _ = QFileDialog.getOpenFileName(
            self,
            "Abrir Archivo Java",
            "",
            "Archivos Java (*.java);;Archivos de Texto (*.txt);;Todos los archivos (*)",
            options=opciones
        )

        if nombre_archivo:
            try:
                with open(nombre_archivo, 'r', encoding='utf-8') as archivo:
                    contenido = archivo.read()
                    self.home.tx_ingreso.setText(contenido)

                # Mostrar el nombre del archivo en la barra de estado
                nombre_base = os.path.basename(nombre_archivo)
                self.home.estado.showMessage(f"Archivo cargado: {nombre_base}")

                # Actualizar el título de la ventana con el nombre del archivo
                self.setWindowTitle(f"Analizador Java - {nombre_base}")

            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo abrir el archivo: {str(e)}")

    def ev_limpiar(self):
        """
        Limpiar todos los campos
        """
        self.home.tx_ingreso.clear()
        self.home.tb_lexico.setRowCount(0)
        self.home.tx_sintactico.clear()
        self.home.tb_simbolos.setRowCount(0)
        self.home.treeWidget.clear()  # Limpiar también el árbol
        tabla_simbolos.limpiar()  # Limpiar la tabla de símbolos
        self.home.estado.showMessage("Todos los campos han sido limpiados")
        self.analisis_sintactico_realizado = False  # Reiniciar estado
        self.home.bt_arbol.setEnabled(True)  # Restaurar el botón

        # Restaurar título predeterminado
        self.setWindowTitle("Analizador Java - Visualizador de Árboles de Derivación")


def iniciar():
    # Instanciar la aplicación
    app = QApplication(sys.argv)

    # Establecer estilo de la aplicación
    app.setStyle("Fusion")  # Usar el estilo Fusion que se ve bien en tema oscuro

    # Establecer paleta de colores oscura para toda la aplicación
    palette = app.palette()
    palette.setColor(palette.Window, QColor(30, 30, 30))
    palette.setColor(palette.WindowText, QColor(220, 220, 220))
    palette.setColor(palette.Base, QColor(15, 15, 15))
    palette.setColor(palette.AlternateBase, QColor(35, 35, 35))
    palette.setColor(palette.ToolTipBase, QColor(30, 30, 30))
    palette.setColor(palette.ToolTipText, QColor(220, 220, 220))
    palette.setColor(palette.Text, QColor(220, 220, 220))
    palette.setColor(palette.Button, QColor(53, 53, 53))
    palette.setColor(palette.ButtonText, QColor(220, 220, 220))
    palette.setColor(palette.BrightText, QColor(255, 255, 255))
    palette.setColor(palette.Highlight, QColor(42, 130, 218))
    palette.setColor(palette.HighlightedText, QColor(0, 0, 0))
    app.setPalette(palette)

    # Crear y mostrar la ventana principal
    ventana = Main()
    ventana.show()

    # Ejecutar el loop de eventos
    sys.exit(app.exec_())


if __name__ == '__main__':
    iniciar()