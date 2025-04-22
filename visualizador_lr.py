#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTreeWidget, QTreeWidgetItem,
                             QPushButton, QLabel, QSplitter, QWidget, QScrollArea, QFrame,
                             QGraphicsView, QGraphicsScene, QGraphicsRectItem, QGraphicsTextItem)
from PyQt5.QtGui import QColor, QBrush, QFont, QPen, QFontMetrics, QPainter  # Add QPainter here
from PyQt5.QtCore import Qt, QRectF, QPointF, QSizeF, pyqtSignal


class NodoLR:
    """Clase para representar un nodo en el árbol LR"""

    def __init__(self, etiqueta, tipo=None, valor=None, linea=None):
        self.etiqueta = etiqueta
        self.tipo = tipo
        self.valor = valor
        self.linea = linea
        self.hijos = []
        # Posición y tamaño para la representación gráfica
        self.x = 0
        self.y = 0
        self.width = 0
        self.height = 0
        # Colores y formato
        self.color_texto = "#FFFFFF"
        self.color_fondo = "#2D2D30"
        self.negrita = False
        self.italiano = False
        self.tamanio = 10

    def agregar_hijo(self, hijo):
        self.hijos.append(hijo)
        return hijo

    def texto_display(self):
        """Genera el texto a mostrar en el nodo"""
        texto = self.etiqueta
        if self.valor:
            texto += f": {self.valor}"
        if self.linea:
            texto += f" (línea {self.linea})"
        return texto

    def establecer_estilo(self, color_texto, color_fondo, negrita=False, italiano=False, tamanio=10):
        """Establece el estilo visual del nodo"""
        self.color_texto = color_texto
        self.color_fondo = color_fondo
        self.negrita = negrita
        self.italiano = italiano
        self.tamanio = tamanio


class ArbolLRScene(QGraphicsScene):
    """Escena para visualizar el árbol LR con dibujo personalizado"""

    def __init__(self, parent=None):
        super().__init__(parent)
        # Colores para el fondo y las líneas
        self.setBackgroundBrush(QBrush(QColor("#1E1E1E")))
        self.line_color = QColor("#4D4D4D")
        self.espaciado_horizontal = 40
        self.espaciado_vertical = 60
        self.padding_nodo = 10
        self.raiz = None

    def construir_arbol(self, raiz):
        """Construye la representación gráfica del árbol a partir de un nodo raíz"""
        self.raiz = raiz
        self.clear()

        # Calcular posiciones de todos los nodos
        self._calcular_posiciones(raiz, 0, 0)

        # Dibujar las conexiones entre nodos (de padre a hijos)
        self._dibujar_conexiones(raiz)

        # Dibujar los nodos
        self._dibujar_nodos(raiz)

    def _calcular_posiciones(self, nodo, nivel, offset_x):
        """Calcula la posición de cada nodo en la escena"""
        # Crear fuente para medir tamaño del texto
        font = QFont("Consolas", nodo.tamanio)
        if nodo.negrita:
            font.setBold(True)
        if nodo.italiano:
            font.setItalic(True)

        metrics = QFontMetrics(font)
        texto = nodo.texto_display()
        rect = metrics.boundingRect(texto)

        # Establecer tamaño del nodo basado en el texto
        nodo.width = rect.width() + self.padding_nodo * 2
        nodo.height = rect.height() + self.padding_nodo * 2

        # Calcular posiciones para los hijos recursivamente
        hijo_offset_x = offset_x
        for hijo in nodo.hijos:
            hijo_offset_x = self._calcular_posiciones(hijo, nivel + 1, hijo_offset_x)

        # Si no tiene hijos, establecer su posición directamente
        if not nodo.hijos:
            nodo.x = offset_x
            nodo.y = nivel * self.espaciado_vertical
            return offset_x + nodo.width + self.espaciado_horizontal

        # Si tiene hijos, centrar el nodo sobre sus hijos
        if nodo.hijos:
            primer_hijo = nodo.hijos[0]
            ultimo_hijo = nodo.hijos[-1]
            centro_hijos = (primer_hijo.x + ultimo_hijo.x + ultimo_hijo.width) / 2
            nodo.x = centro_hijos - nodo.width / 2
            nodo.y = nivel * self.espaciado_vertical

        return max(hijo_offset_x, nodo.x + nodo.width + self.espaciado_horizontal)

    def _dibujar_nodos(self, nodo):
        """Dibuja todos los nodos en la escena"""
        # Dibujar el nodo actual
        rect_item = QGraphicsRectItem(nodo.x, nodo.y, nodo.width, nodo.height)
        rect_item.setBrush(QBrush(QColor(nodo.color_fondo)))
        rect_item.setPen(QPen(QColor("#6D6D6D"), 1))
        self.addItem(rect_item)

        # Dibujar el texto del nodo
        text_item = QGraphicsTextItem(nodo.texto_display())
        font = QFont("Consolas", nodo.tamanio)
        if nodo.negrita:
            font.setBold(True)
        if nodo.italiano:
            font.setItalic(True)
        text_item.setFont(font)
        text_item.setDefaultTextColor(QColor(nodo.color_texto))

        # Posicionar el texto centrado en el nodo
        text_rect = text_item.boundingRect()
        text_x = nodo.x + (nodo.width - text_rect.width()) / 2
        text_y = nodo.y + (nodo.height - text_rect.height()) / 2
        text_item.setPos(text_x, text_y)

        self.addItem(text_item)

        # Dibujar los hijos recursivamente
        for hijo in nodo.hijos:
            self._dibujar_nodos(hijo)

    def _dibujar_conexiones(self, nodo):
        """Dibuja las conexiones entre un nodo y sus hijos"""
        for hijo in nodo.hijos:
            # Punto de inicio (centro inferior del nodo padre)
            inicio_x = nodo.x + nodo.width / 2
            inicio_y = nodo.y + nodo.height

            # Punto final (centro superior del nodo hijo)
            fin_x = hijo.x + hijo.width / 2
            fin_y = hijo.y

            # Dibujar la línea
            line = self.addLine(inicio_x, inicio_y, fin_x, fin_y, QPen(self.line_color, 1, Qt.SolidLine))

            # Dibujar conexiones para los hijos de este hijo
            self._dibujar_conexiones(hijo)


class ArbolLRView(QGraphicsView):
    """Vista personalizada para el árbol LR con soporte para zoom y panning"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setRenderHint(QPainter.Antialiasing)  # Changed from QPen to QPainter
        self.setRenderHint(QPainter.TextAntialiasing)  # Changed from QPen to QPainter
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.scale_factor = 1.15

    def wheelEvent(self, event):
        """Implementa el zoom con la rueda del ratón"""
        factor = self.scale_factor

        if event.angleDelta().y() < 0:
            # Zoom out
            factor = 1.0 / factor

        self.scale(factor, factor)


class VentanaArbolLR(QDialog):
    """Ventana para visualizar el árbol de derivación LR"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Árbol de Derivación LR Detallado")
        self.resize(1200, 800)

        # Crear elementos de la interfaz
        self.layout_principal = QVBoxLayout(self)

        # Barra superior con controles
        self.layout_controles = QHBoxLayout()

        self.lbl_info = QLabel(
            "Árbol de derivación en formato Left-to-Right (LR). Use la rueda del ratón para zoom y arrastre para moverse.")
        self.layout_controles.addWidget(self.lbl_info)

        self.btn_expandir = QPushButton("Expandir Todo")
        self.btn_expandir.clicked.connect(self.expandir_todo)
        self.layout_controles.addWidget(self.btn_expandir)

        self.btn_colapsar = QPushButton("Colapsar Todo")
        self.btn_colapsar.clicked.connect(self.colapsar_todo)
        self.layout_controles.addWidget(self.btn_colapsar)

        self.btn_cerrar = QPushButton("Cerrar")
        self.btn_cerrar.clicked.connect(self.close)
        self.layout_controles.addWidget(self.btn_cerrar)

        self.layout_principal.addLayout(self.layout_controles)

        # Crear vista para el árbol LR
        self.scene = ArbolLRScene()
        self.view = ArbolLRView(self.scene)
        self.layout_principal.addWidget(self.view)

        # Variables para almacenar el árbol
        self.arbol_raiz = None

    def establecer_arbol(self, raiz):
        """Establece y visualiza el árbol a partir de la raíz dada"""
        self.arbol_raiz = raiz
        self.scene.construir_arbol(raiz)

        # Ajustar la vista para mostrar todo el árbol
        self.view.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)
        self.view.centerOn(self.scene.sceneRect().center())

    def expandir_todo(self):
        """Expande todos los nodos del árbol"""
        # En esta implementación gráfica, todos los nodos están siempre expandidos
        # Esta función está aquí para mantener consistencia con la interfaz
        pass

    def colapsar_todo(self):
        """Colapsa todos los nodos del árbol excepto la raíz"""
        # En esta implementación gráfica, la colapsación no aplica directamente
        # Para implementarlo, necesitaríamos reconstruir la escena
        pass


def construir_arbol_lr_desde_codigo(codigo_fuente):
    """
    Construye un árbol LR a partir del código fuente
    Retorna la raíz del árbol y un booleano indicando éxito
    """
    from analizador_sintactico import prueba_sintactica
    from analizador_lexico import tabla_simbolos
    from arbol_derivacion import construir_arbol_derivacion

    try:
        # Primero realizamos el análisis sintáctico
        resultado = prueba_sintactica(codigo_fuente)

        # Verificar si hay errores
        tiene_errores = any("Error" in item for item in resultado)
        if tiene_errores:
            return None, False

        # Construir el árbol de derivación básico
        arbol_basico, _ = construir_arbol_derivacion(codigo_fuente)

        if arbol_basico is None:
            return None, False

        # Convertir el árbol básico a formato LR
        arbol_lr = _convertir_arbol_basico_a_lr(arbol_basico)

        return arbol_lr, True

    except Exception as e:
        print(f"Error al construir árbol LR: {str(e)}")
        return None, False


def _convertir_arbol_basico_a_lr(nodo_basico):
    """
    Convierte un nodo del árbol básico a formato LR con estilos visuales mejorados
    """
    # Crear el nodo LR equivalente
    nodo_lr = NodoLR(nodo_basico.tipo, nodo_basico.tipo, nodo_basico.valor, nodo_basico.linea)

    # Aplicar estilo según el tipo de nodo
    if nodo_basico.tipo == "programa":
        nodo_lr.establecer_estilo("#F89406", "#2D2D30", True, False, 14)  # Naranja
    elif nodo_basico.tipo == "declaracion_clase":
        nodo_lr.establecer_estilo("#569CD6", "#2D2D30", True, False, 13)  # Azul
    elif nodo_basico.tipo == "metodo":
        nodo_lr.establecer_estilo("#4EC9B0", "#2D2D30", True, False, 12)  # Verde agua
    elif nodo_basico.tipo == "atributo":
        nodo_lr.establecer_estilo("#9CDCFE", "#2D2D30", False, False, 11)  # Azul claro
    elif nodo_basico.tipo == "declaracion":
        nodo_lr.establecer_estilo("#DCDCAA", "#2D2D30", False, False, 11)  # Amarillo
    elif nodo_basico.tipo in ["if", "for", "while"]:
        nodo_lr.establecer_estilo("#C586C0", "#2D2D30", True, False, 11)  # Morado
    elif nodo_basico.tipo == "llamada":
        nodo_lr.establecer_estilo("#57A64A", "#2D2D30", False, False, 11)  # Verde
    elif nodo_basico.tipo == "expresion":
        nodo_lr.establecer_estilo("#CE9178", "#2D2D30", False, False, 10)  # Rojo claro
    elif nodo_basico.tipo == "operador":
        nodo_lr.establecer_estilo("#D4D4D4", "#2D2D30", True, False, 10)  # Gris claro
    else:
        # Estilo predeterminado para otros tipos de nodos
        nodo_lr.establecer_estilo("#FFFFFF", "#2D2D30", False, False, 10)

    # Procesar recursivamente todos los hijos
    for hijo in nodo_basico.hijos:
        nodo_hijo_lr = _convertir_arbol_basico_a_lr(hijo)
        nodo_lr.agregar_hijo(nodo_hijo_lr)

    return nodo_lr


def mostrar_arbol_lr(codigo_fuente, parent=None):
    """
    Función principal para mostrar el árbol LR en una ventana separada

    Args:
        codigo_fuente: Código fuente Java a analizar
        parent: Widget padre para la ventana

    Returns:
        bool: True si el árbol se mostró correctamente, False en caso contrario
    """
    # Construir el árbol LR
    arbol_lr, exito = construir_arbol_lr_desde_codigo(codigo_fuente)

    if not exito or arbol_lr is None:
        return False

    # Crear y mostrar la ventana
    ventana = VentanaArbolLR(parent)
    ventana.establecer_arbol(arbol_lr)
    ventana.show()

    return True