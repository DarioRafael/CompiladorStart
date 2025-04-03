#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QTableWidgetItem, QMessageBox
from PyQt5.QtGui import QColor, QSyntaxHighlighter, QTextCharFormat, QFont
from PyQt5.QtCore import QRegExp

# Importar nuestros componentes
from vista.home import Ui_home
from analizador_lexico import prueba, tabla_simbolos
from analizador_sintactico import prueba_sintactica


# Resaltador de sintaxis para Java
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

        # Aplicar resaltador de sintaxis de Java
        self.highlighter = JavaHighlighter(self.home.tx_ingreso.document())

        # Conectar eventos
        self.home.bt_lexico.clicked.connect(self.ev_lexico)
        self.home.bt_sintactico.clicked.connect(self.ev_sintactico)
        self.home.bt_archivo.clicked.connect(self.ev_archivo)
        self.home.bt_limpiar.clicked.connect(self.ev_limpiar)
        self.home.bt_simbolos.clicked.connect(self.mostrar_tabla_simbolos)

        # Conectar atajos de teclado
        self.home.shortcut_run_lexical.activated.connect(self.ev_lexico)
        self.home.shortcut_run_syntactic.activated.connect(self.ev_sintactico)
        self.home.shortcut_open.activated.connect(self.ev_archivo)
        self.home.shortcut_clear.activated.connect(self.ev_limpiar)

        # Mostrar información de la aplicación
        self.home.estado.showMessage("Analizador de código Java - Desarrollado con PyQt5 y PLY")

    def ev_lexico(self):
        """
        Manejo del análisis léxico
        """
        self.home.tb_lexico.setRowCount(0)
        codigo = self.home.tx_ingreso.toPlainText().strip()



        if not codigo:
            QMessageBox.warning(self, "Advertencia", "No hay código para analizar.")
            return

        # Realizar el análisis léxico
        try:
            from analizador_lexico import prueba, tabla_simbolos
            tabla_simbolos.limpiar()
            resultados = prueba(codigo)

            # Llenar la tabla con los resultados
            self.home.tb_lexico.setRowCount(len(resultados))

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

                if tipo == "ERROR":
                    color_fondo = QColor("#7E2D40")  # Fondo rojo para errores
                    color_texto = QColor("#FFFFFF")  # Texto blanco para errores

                # Crear items para la tabla
                item_linea = QTableWidgetItem(linea)
                item_tipo = QTableWidgetItem(tipo)
                item_lexema = QTableWidgetItem(lexema)
                item_patron = QTableWidgetItem(patron)

                # Aplicar colores
                item_linea.setBackground(color_fondo)
                item_tipo.setBackground(color_fondo)
                item_lexema.setBackground(color_fondo)
                item_patron.setBackground(color_fondo)

                item_linea.setForeground(color_texto)
                item_tipo.setForeground(color_texto)
                item_lexema.setForeground(color_texto)
                item_patron.setForeground(color_texto)

                # Agregar a la tabla
                self.home.tb_lexico.setItem(i, 0, item_linea)
                self.home.tb_lexico.setItem(i, 1, item_tipo)
                self.home.tb_lexico.setItem(i, 2, item_lexema)
                self.home.tb_lexico.setItem(i, 3, item_patron)

            # Desactivar el color alternante de filas nativo
            self.home.tb_lexico.setAlternatingRowColors(False)

            # Ajustar tamaño de las columnas
            self.home.tb_lexico.resizeColumnsToContents()

            # Mostrar mensaje en la barra de estado
            self.home.estado.showMessage(f"Análisis léxico completado: {len(resultados)} tokens encontrados")

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

        # Realizar el análisis sintáctico
        try:
            from analizador_sintactico import prueba_sintactica
            from analizador_lexico import tabla_simbolos
            tabla_simbolos.limpiar()
            resultados = prueba_sintactica(codigo)

            # Mostrar los resultados
            html_output = "<html><body style='color:#DCDCDC; font-family: Consolas, monospace;'>"

            for item in resultados:
                if "Error" in item:
                    html_output += f"<p style='color:#FF6B68;'>{item}</p>"
                elif "Advertencia" in item:
                    html_output += f"<p style='color:#FFA500;'>{item}</p>"
                else:
                    html_output += f"<p>{item}</p>"

            html_output += "</body></html>"
            self.home.tx_sintactico.setHtml(html_output)

            # Mostrar mensaje en la barra de estado
            if any("Error" in item for item in resultados):
                self.home.estado.showMessage("Análisis sintáctico completado con errores")
            else:
                self.home.estado.showMessage("Análisis sintáctico completado correctamente")

            # Cambiar a la pestaña de análisis sintáctico
            self.home.analysisTabs.setCurrentIndex(1)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error durante el análisis sintáctico: {str(e)}")
            self.home.estado.showMessage(f"Error: {str(e)}")

    def mostrar_tabla_simbolos(self):
        """
        Muestra la tabla de símbolos actual
        """
        # Limpiar la tabla
        self.home.tb_simbolos.setRowCount(0)

        # Desactivar colores alternantes
        self.home.tb_simbolos.setAlternatingRowColors(False)

        # Obtener la tabla de símbolos actual
        simbolos = tabla_simbolos.obtener_todos()

        if not simbolos:
            self.home.estado.showMessage("No hay símbolos definidos en la tabla de símbolos")
            return

        # Llenar la tabla con los símbolos
        self.home.tb_simbolos.setRowCount(len(simbolos))

        for i, (nombre, info) in enumerate(simbolos.items()):
            # Usar fondo blanco para todas las celdas
            color_fondo = QColor("#FFFFFF")  # Blanco para todas las celdas
            color_texto = QColor("#FFFFFF")  # Texto negro

            # Crear items para cada columna
            item_nombre = QTableWidgetItem(nombre)
            item_tipo = QTableWidgetItem(info.get("tipo", ""))
            item_valor = QTableWidgetItem(str(info.get("valor", "")))
            item_linea = QTableWidgetItem(str(info.get("linea", "")))
            item_alcance = QTableWidgetItem(info.get("alcance", "global"))

            # Aplicar colores y formato negrita
            item_nombre.setBackground(color_fondo)
            item_tipo.setBackground(color_fondo)
            item_valor.setBackground(color_fondo)
            item_linea.setBackground(color_fondo)
            item_alcance.setBackground(color_fondo)

            item_nombre.setForeground(color_texto)
            item_tipo.setForeground(color_texto)
            item_valor.setForeground(color_texto)
            item_linea.setForeground(color_texto)
            item_alcance.setForeground(color_texto)

            # Aplicar formato negrita
            font = item_nombre.font()
            font.setBold(True)
            item_nombre.setFont(font)
            item_tipo.setFont(font)
            item_valor.setFont(font)
            item_linea.setFont(font)
            item_alcance.setFont(font)

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
            "Archivos Java (*.java);;Todos los archivos (*)",
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
        tabla_simbolos.limpiar()  # Limpiar la tabla de símbolos
        self.home.estado.showMessage("Todos los campos han sido limpiados")


def iniciar():
    # Instanciar la aplicación
    app = QApplication(sys.argv)

    # Crear y mostrar la ventana principal
    ventana = Main()
    ventana.show()

    # Ejecutar el loop de eventos
    sys.exit(app.exec_())


if __name__ == '__main__':
    iniciar()