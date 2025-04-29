# -*- coding: utf-8 -*-
"""
arbol_visual.py - Visualizador de Árboles de Recorrido
Este módulo implementa una visualización de árbol vertical (de arriba hacia abajo)
con representaciones para pre-orden, in-orden y post-orden.
"""

import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from PyQt5.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QHBoxLayout, QToolBar,
    QPushButton, QLabel, QTabWidget, QGraphicsView, QGraphicsScene,
    QGraphicsRectItem, QGraphicsTextItem, QGraphicsLineItem, QGraphicsEllipseItem,
    QMessageBox, QWidget, QSlider, QAction
)
from PyQt5.QtCore import Qt, QRectF, QPointF
from PyQt5.QtGui import QColor, QBrush, QPen, QFont, QPainter, QIcon


# Clase que representa un nodo del árbol
class NodoArbol:
    def __init__(self, tipo, valor=None, linea=None):
        self.tipo = tipo
        self.valor = valor if valor else tipo
        self.linea = linea
        self.hijos = []
        self.padre = None
        self.x = 0  # Posición X para dibujar
        self.y = 0  # Posición Y para dibujar
        self.width = 100  # Ancho del nodo
        self.height = 40  # Alto del nodo
        self.orden_preorden = 0
        self.orden_inorden = 0
        self.orden_postorden = 0

    def agregar_hijo(self, nodo):
        """Agrega un hijo al nodo actual"""
        self.hijos.append(nodo)
        nodo.padre = self
        return nodo

    def __str__(self):
        """Representación en cadena del nodo"""
        return f"{self.tipo}: {self.valor}" if self.valor else self.tipo


# Clase para representar el árbol
class Arbol:
    def __init__(self):
        self.raiz = None
        self.contador_preorden = 1
        self.contador_inorden = 1
        self.contador_postorden = 1

    def crear_arbol_ejemplo(self):
        """Crea un árbol de ejemplo para pruebas"""
        self.raiz = NodoArbol("programa", "Programa")

        # Nivel 1
        nodo_declaraciones = NodoArbol("declaraciones", "Declaraciones")
        nodo_instrucciones = NodoArbol("instrucciones", "Instrucciones")
        self.raiz.agregar_hijo(nodo_declaraciones)
        self.raiz.agregar_hijo(nodo_instrucciones)

        # Nivel 2 - Declaraciones
        nodo_int = NodoArbol("int", "int")
        nodo_declaraciones.agregar_hijo(nodo_int)

        nodo_float = NodoArbol("float", "float")
        nodo_declaraciones.agregar_hijo(nodo_float)

        # Nivel 2 - Instrucciones
        nodo_if = NodoArbol("if", "if")
        nodo_instrucciones.agregar_hijo(nodo_if)

        nodo_while = NodoArbol("while", "while")
        nodo_instrucciones.agregar_hijo(nodo_while)

        # Nivel 3 - Identificadores
        nodo_id1 = NodoArbol("identificador", "contador")
        nodo_int.agregar_hijo(nodo_id1)

        nodo_id2 = NodoArbol("identificador", "precio")
        nodo_float.agregar_hijo(nodo_id2)

        # Calcular los recorridos
        self.calcular_orden_recorridos()
        return True

    def construir_de_codigo(self, codigo):
        """
        Construye un árbol a partir del código fuente usando recorridos_arbol
        """
        try:
            from recorridos_arbol import construir_arbol_recorridos

            # Usar la función de recorridos_arbol
            arbol, resultados = construir_arbol_recorridos(codigo)

            if arbol is None:
                print("Error al construir el árbol")
                return False

            # Convertir el árbol de recorridos_arbol a la estructura de Arbol
            self.raiz = self._convertir_nodo(arbol)

            # Calcular los recorridos
            self.calcular_orden_recorridos()

            return True
        except Exception as e:
            print(f"Error al construir árbol: {str(e)}")
            return False

    def _convertir_nodo(self, nodo_original):
        """
        Convierte un NodoRecorrido de recorridos_arbol a un NodoArbol
        """
        # Crear nuevo nodo con el mismo tipo y valor
        nuevo_nodo = NodoArbol(nodo_original.tipo, nodo_original.valor, nodo_original.linea)

        # Convertir recursivamente los hijos
        for hijo_original in nodo_original.hijos:
            nuevo_hijo = self._convertir_nodo(hijo_original)
            nuevo_nodo.agregar_hijo(nuevo_hijo)

        return nuevo_nodo

    def calcular_orden_recorridos(self):
        """Calcula los órdenes de recorrido para cada nodo"""
        if not self.raiz:
            return

        # Inicializar contadores
        self.contador_preorden = 1
        self.contador_inorden = 1
        self.contador_postorden = 1

        # Realizar recorridos
        self._recorrido_preorden(self.raiz)
        self._recorrido_inorden(self.raiz)
        self._recorrido_postorden(self.raiz)

    def _recorrido_preorden(self, nodo):
        """Pre-orden: Raíz → Izquierda → Derecha"""
        if nodo is None:
            return []

        # 1. Visita la raíz
        resultado = [nodo]

        # 2. Recorre subárbol izquierdo en pre-orden
        for hijo in nodo.hijos:
            resultado.extend(self._recorrido_preorden(hijo))

        return resultado

    def _recorrido_inorden(self, nodo):
        """In-orden: Izquierda → Raíz → Derecha (adaptado para múltiples hijos)"""
        if nodo is None:
            return []

        resultado = []
        mitad = len(nodo.hijos) // 2

        # 1. Recorre primera mitad de hijos (subárbol izquierdo)
        for i in range(mitad):
            resultado.extend(self._recorrido_inorden(nodo.hijos[i]))

        # 2. Visita la raíz
        resultado.append(nodo)

        # 3. Recorre segunda mitad de hijos (subárbol derecho)
        for i in range(mitad, len(nodo.hijos)):
            resultado.extend(self._recorrido_inorden(nodo.hijos[i]))

        return resultado

    def _recorrido_postorden(self, nodo):
        """Post-orden: Izquierda → Derecha → Raíz"""
        if nodo is None:
            return []

        resultado = []

        # 1. Recorre todos los subárboles
        for hijo in nodo.hijos:
            resultado.extend(self._recorrido_postorden(hijo))

        # 2. Visita la raíz
        resultado.append(nodo)

        return resultado


# Clase para la vista personalizada del árbol
class VistaArbolGrafica(QGraphicsView):
    def __init__(self, parent=None):
        super(VistaArbolGrafica, self).__init__(parent)

        # Configuración de la vista
        self.setRenderHint(QPainter.Antialiasing)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)

        # Factor de zoom
        self.escala = 1.0
        self.factor_zoom = 1.2

        # Escena
        self.escena = QGraphicsScene(self)
        self.setScene(self.escena)

    def wheelEvent(self, event):
        """Maneja el evento de la rueda del ratón para hacer zoom"""
        factor_zoom = self.factor_zoom

        if event.angleDelta().y() < 0:
            # Zoom out
            factor_zoom = 1.0 / factor_zoom
            self.escala /= self.factor_zoom
        else:
            # Zoom in
            self.escala *= self.factor_zoom

        # Limitar zoom
        if 0.25 <= self.escala <= 4.0:
            self.scale(factor_zoom, factor_zoom)
        else:
            # Restaurar escala
            self.escala = max(0.25, min(self.escala, 4.0))


# Clase para dibujar el árbol en la escena
class DibujanteArbol:
    def __init__(self, escena, modo_recorrido=None):
        self.escena = escena
        self.modo_recorrido = modo_recorrido

        # Colores para nodos según tipo
        self.colores_nodos = {
            "programa": "#B9DDFF",  # Azul claro
            "declaraciones": "#B9DDFF",  # Azul claro
            "instrucciones": "#B9DDFF",  # Azul claro
            "if": "#B9DDFF",  # Azul claro
            "while": "#B9DDFF",  # Azul claro
            "for": "#B9DDFF",  # Azul claro
            "int": "#B9DDFF",  # Azul claro
            "float": "#B9DDFF",  # Azul claro
            "double": "#B9DDFF",  # Azul claro
            "char": "#B9DDFF",  # Azul claro
            "boolean": "#B9DDFF",  # Azul claro
            "string": "#B9DDFF",  # Azul claro
            "identificador": "#B5F5B9",  # Verde claro
            "entero": "#FFFFA6",  # Amarillo claro
            "decimal": "#FFFFA6",  # Amarillo claro
            "condicionales": "#B9DDFF",  # Azul claro
            "bucles": "#B9DDFF",  # Azul claro
            "asignaciones": "#B9DDFF",  # Azul claro
            "llamadas": "#B9DDFF",  # Azul claro
            "default": "#B9DDFF"  # Azul claro por defecto
        }

    def dibujar_arbol(self, arbol):
        """Dibuja el árbol completo en la escena"""
        self.escena.clear()

        if not arbol.raiz:
            QMessageBox.warning(None, "Error", "El árbol no tiene una raíz válida.")
            return

        # Calcular posiciones para cada recorrido
        if self.modo_recorrido == "preorden":
            recorrido = arbol._recorrido_preorden(arbol.raiz)
        elif self.modo_recorrido == "inorden":
            recorrido = arbol._recorrido_inorden(arbol.raiz)
        else:  # postorden
            recorrido = arbol._recorrido_postorden(arbol.raiz)

        if not recorrido:
            QMessageBox.warning(None, "Error", "No se pudo calcular el recorrido del árbol.")
            return

        # Dibujar nodos en el orden del recorrido
        self._dibujar_recorrido(recorrido)

    def _dibujar_recorrido(self, recorrido):
        """Dibuja los nodos en el orden del recorrido"""
        # Configuración inicial
        x_inicial = 50
        y_inicial = 100
        espacio_horizontal = 150
        espacio_vertical = 100

        # Dibujar cada nodo en el recorrido
        for i, nodo in enumerate(recorrido):
            x = x_inicial + i * espacio_horizontal
            y = y_inicial

            # Dibujar nodo
            self._dibujar_nodo(nodo, x, y)

    def _dibujar_nodo(self, nodo, x, y):
        """Dibuja un nodo en la posición especificada"""
        # Crear el rectángulo
        rectangulo = QGraphicsRectItem(x, y, 100, 40)

        # Establecer color según tipo de nodo
        color = self.colores_nodos.get(nodo.tipo.lower(), self.colores_nodos["default"])
        rectangulo.setBrush(QBrush(QColor(color)))
        rectangulo.setPen(QPen(QColor("#000000"), 2))
        self.escena.addItem(rectangulo)

        # Texto del nodo
        texto_valor = nodo.valor if nodo.valor else nodo.tipo
        texto_item = QGraphicsTextItem(texto_valor)
        texto_item.setFont(QFont("Arial", 10))
        texto_item.setDefaultTextColor(QColor("#000000"))

        # Centrar texto en el nodo
        texto_width = texto_item.boundingRect().width()
        texto_height = texto_item.boundingRect().height()
        texto_item.setPos(x + 50 - texto_width / 2, y + 20 - texto_height / 2)
        self.escena.addItem(texto_item)


# Ventana principal para visualizar los árboles
class VisualizadorArbol(QDialog):
    def __init__(self, arbol, parent=None):
        super(VisualizadorArbol, self).__init__(parent)
        self.setWindowTitle("Visualizador de Árboles - Recorridos")
        self.setMinimumSize(1400, 800)
        self.setModal(True)

        # Guardar el árbol
        self.arbol = arbol

        # Configurar interfaz
        self._configurar_ui()

        # Mostrar el árbol inicial (pre-orden)
        self._mostrar_arbol("preorden")

    def _configurar_ui(self):
        """Configura la interfaz de usuario"""
        # Layout principal
        layout_principal = QVBoxLayout(self)

        # Crear pestañas
        self.tab_widget = QTabWidget()

        # Crear pestañas para cada recorrido
        self.tab_preorden = QWidget()
        self.tab_inorden = QWidget()
        self.tab_postorden = QWidget()

        # Crear vistas para cada recorrido
        self.vista_preorden = VistaArbolGrafica()
        self.vista_inorden = VistaArbolGrafica()
        self.vista_postorden = VistaArbolGrafica()

        # Dibujar los árboles
        # Los dibujantes se encargan de las escenas
        self.dibujante_preorden = DibujanteArbol(self.vista_preorden.escena, "preorden")
        self.dibujante_inorden = DibujanteArbol(self.vista_inorden.escena, "inorden")
        self.dibujante_postorden = DibujanteArbol(self.vista_postorden.escena, "postorden")

        # Layouts para cada pestaña
        layout_preorden = QVBoxLayout(self.tab_preorden)
        layout_inorden = QVBoxLayout(self.tab_inorden)
        layout_postorden = QVBoxLayout(self.tab_postorden)

        # Agregar controles de zoom a cada pestaña
        toolbar_preorden = QToolBar("Zoom")
        accion_zoom_in_preorden = QAction("Zoom +", self)
        accion_zoom_in_preorden.triggered.connect(lambda: self._zoom_in(self.vista_preorden))
        accion_zoom_out_preorden = QAction("Zoom -", self)
        accion_zoom_out_preorden.triggered.connect(lambda: self._zoom_out(self.vista_preorden))
        accion_reset_preorden = QAction("Reset Zoom", self)
        accion_reset_preorden.triggered.connect(lambda: self._reset_zoom(self.vista_preorden))
        toolbar_preorden.addAction(accion_zoom_in_preorden)
        toolbar_preorden.addAction(accion_zoom_out_preorden)
        toolbar_preorden.addAction(accion_reset_preorden)

        toolbar_inorden = QToolBar("Zoom")
        accion_zoom_in_inorden = QAction("Zoom +", self)
        accion_zoom_in_inorden.triggered.connect(lambda: self._zoom_in(self.vista_inorden))
        accion_zoom_out_inorden = QAction("Zoom -", self)
        accion_zoom_out_inorden.triggered.connect(lambda: self._zoom_out(self.vista_inorden))
        accion_reset_inorden = QAction("Reset Zoom", self)
        accion_reset_inorden.triggered.connect(lambda: self._reset_zoom(self.vista_inorden))
        toolbar_inorden.addAction(accion_zoom_in_inorden)
        toolbar_inorden.addAction(accion_zoom_out_inorden)
        toolbar_inorden.addAction(accion_reset_inorden)

        toolbar_postorden = QToolBar("Zoom")
        accion_zoom_in_postorden = QAction("Zoom +", self)
        accion_zoom_in_postorden.triggered.connect(lambda: self._zoom_in(self.vista_postorden))
        accion_zoom_out_postorden = QAction("Zoom -", self)
        accion_zoom_out_postorden.triggered.connect(lambda: self._zoom_out(self.vista_postorden))
        accion_reset_postorden = QAction("Reset Zoom", self)
        accion_reset_postorden.triggered.connect(lambda: self._reset_zoom(self.vista_postorden))
        toolbar_postorden.addAction(accion_zoom_in_postorden)
        toolbar_postorden.addAction(accion_zoom_out_postorden)
        toolbar_postorden.addAction(accion_reset_postorden)

        # Etiquetas informativas
        label_preorden = QLabel("Instrucciones: Usa el ratón para hacer zoom (rueda) y desplazarte (clic y arrastrar)")
        label_inorden = QLabel("Instrucciones: Usa el ratón para hacer zoom (rueda) y desplazarte (clic y arrastrar)")
        label_postorden = QLabel("Instrucciones: Usa el ratón para hacer zoom (rueda) y desplazarte (clic y arrastrar)")

        # Agregar vistas y controles a los layouts
        layout_preorden.addWidget(toolbar_preorden)
        layout_preorden.addWidget(label_preorden)
        layout_preorden.addWidget(self.vista_preorden)

        layout_inorden.addWidget(toolbar_inorden)
        layout_inorden.addWidget(label_inorden)
        layout_inorden.addWidget(self.vista_inorden)

        layout_postorden.addWidget(toolbar_postorden)
        layout_postorden.addWidget(label_postorden)
        layout_postorden.addWidget(self.vista_postorden)

        # Agregar pestañas al widget de pestañas
        self.tab_widget.addTab(self.tab_preorden, "Pre-orden")
        self.tab_widget.addTab(self.tab_inorden, "In-orden")
        self.tab_widget.addTab(self.tab_postorden, "Post-orden")

        # Conectar cambio de pestaña
        self.tab_widget.currentChanged.connect(self._cambiar_pestana)

        # Agregar pestañas al layout principal
        layout_principal.addWidget(self.tab_widget)

    def _zoom_in(self, vista):
        """Aumenta el zoom de la vista"""
        vista.scale(1.2, 1.2)
        vista.escala *= 1.2

    def _zoom_out(self, vista):
        """Reduce el zoom de la vista"""
        vista.scale(1 / 1.2, 1 / 1.2)
        vista.escala /= 1.2

    def _reset_zoom(self, vista):
        """Restaura el zoom original"""
        factor = 1.0 / vista.escala
        vista.scale(factor, factor)
        vista.escala = 1.0

    def _cambiar_pestana(self, indice):
        """Maneja el cambio de pestañas"""
        if indice == 0:
            self._mostrar_arbol("preorden")
        elif indice == 1:
            self._mostrar_arbol("inorden")
        else:
            self._mostrar_arbol("postorden")

    def _mostrar_arbol(self, tipo):
        """Muestra el árbol con el tipo de recorrido especificado"""
        # Dibujar árboles
        self.dibujante_preorden.dibujar_arbol(self.arbol)
        self.dibujante_inorden.dibujar_arbol(self.arbol)
        self.dibujante_postorden.dibujar_arbol(self.arbol)

        # Cambiar a la pestaña correspondiente
        if tipo == "preorden":
            self.tab_widget.setCurrentIndex(0)
        elif tipo == "inorden":
            self.tab_widget.setCurrentIndex(1)
        else:
            self.tab_widget.setCurrentIndex(2)

        # Ajustar vistas
        self.vista_preorden.fitInView(self.vista_preorden.scene().itemsBoundingRect(), Qt.KeepAspectRatio)
        self.vista_inorden.fitInView(self.vista_inorden.scene().itemsBoundingRect(), Qt.KeepAspectRatio)
        self.vista_postorden.fitInView(self.vista_postorden.scene().itemsBoundingRect(), Qt.KeepAspectRatio)

    def resizeEvent(self, event):
        """Ajusta la vista al cambiar el tamaño de la ventana"""
        super(VisualizadorArbol, self).resizeEvent(event)

        # Ajustar vistas
        self.vista_preorden.fitInView(self.vista_preorden.scene().itemsBoundingRect(), Qt.KeepAspectRatio)
        self.vista_inorden.fitInView(self.vista_inorden.scene().itemsBoundingRect(), Qt.KeepAspectRatio)
        self.vista_postorden.fitInView(self.vista_postorden.scene().itemsBoundingRect(), Qt.KeepAspectRatio)


# Función principal para mostrar el visualizador de árboles
def mostrar_arbol_recorridos(codigo, parent=None):
    """
    Función principal que crea y muestra el visualizador de recorridos de árboles
    """
    try:
        # Crear árbol
        arbol = Arbol()

        # Construir árbol desde el código
        resultado = arbol.construir_de_codigo(codigo)

        if not resultado:
            QMessageBox.warning(
                parent,
                "Error al generar árboles",
                "No se pudieron generar los árboles de recorridos debido a errores en el código. " +
                "Corrija los errores antes de intentar generar los árboles."
            )
            return False

        # Mostrar visualizador
        visualizador = VisualizadorArbol(arbol, parent)
        visualizador.exec_()

        return True

    except Exception as e:
        import traceback
        print(f"Error al mostrar el árbol: {str(e)}")
        traceback.print_exc()

        QMessageBox.critical(
            parent,
            "Error",
            f"Ocurrió un error al generar la visualización: {str(e)}"
        )

        return False


# Para pruebas independientes
if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Crear árbol de ejemplo
    arbol = Arbol()
    arbol.crear_arbol_ejemplo()

    # Mostrar visualizador
    visualizador = VisualizadorArbol(arbol)
    visualizador.show()

    sys.exit(app.exec_())