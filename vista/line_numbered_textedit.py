# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui, QtWidgets


class CodeEditor(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Layout principal
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Área de números de línea
        self.line_numbers = QtWidgets.QTextEdit()
        self.line_numbers.setReadOnly(True)
        self.line_numbers.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.line_numbers.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

        # Área de texto principal
        self.text_edit = QtWidgets.QTextEdit()

        # Estilos
        self.setStyleSheet("""
            QTextEdit { 
                background-color: #1E1E1E; 
                color: #DCDCDC; 
                border: 2px solid #3E3E3E;
                border-radius: 4px;
                padding: 10px;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 13px;
            }
        """)

        # Estilos específicos para números de línea
        self.line_numbers.setStyleSheet("""
            background-color: #252526; 
            color: #858585; 
            border: none;
            padding-right: 5px;
            text-align: right;
        """)

        # Sincronizar desplazamiento
        self.text_edit.verticalScrollBar().valueChanged.connect(
            self.line_numbers.verticalScrollBar().setValue
        )
        self.line_numbers.verticalScrollBar().valueChanged.connect(
            self.text_edit.verticalScrollBar().setValue
        )

        # Configuraciones iniciales
        self.text_edit.setLineWrapMode(QtWidgets.QTextEdit.NoWrap)
        self.line_numbers.setLineWrapMode(QtWidgets.QTextEdit.NoWrap)

        # Conectar señales para actualizar números de línea
        self.text_edit.textChanged.connect(self.update_line_numbers)

        # Añadir widgets al layout
        layout.addWidget(self.line_numbers)
        layout.addWidget(self.text_edit)

        # Establecer anchos de columna
        layout.setStretchFactor(self.line_numbers, 1)
        layout.setStretchFactor(self.text_edit, 10)

    def update_line_numbers(self):
        """Actualiza los números de línea"""
        # Obtener el número de líneas
        line_count = self.text_edit.document().blockCount()

        # Generar texto de números de línea
        line_numbers = '\n'.join(str(i + 1) for i in range(line_count))

        # Establecer texto de números de línea
        self.line_numbers.setPlainText(line_numbers)

    # Métodos delegados para mantener la misma interfaz que QTextEdit
    def toPlainText(self):
        return self.text_edit.toPlainText()

    def setText(self, text):
        self.text_edit.setText(text)

    def setPlaceholderText(self, text):
        self.text_edit.setPlaceholderText(text)

    def clear(self):
        self.text_edit.clear()
        self.line_numbers.clear()

    def setLineWrapMode(self, mode):
        self.text_edit.setLineWrapMode(mode)

    def setTabStopWidth(self, width):
        self.text_edit.setTabStopWidth(width)

    # Delegar más métodos según sea necesario
    def __getattr__(self, name):
        """Delegar cualquier otro método no definido explícitamente al text_edit"""
        return getattr(self.text_edit, name)

    # Eventos de teclado y foco
    def keyPressEvent(self, event):
        self.text_edit.setFocus()
        self.text_edit.keyPressEvent(event)