# -*- coding: utf-8 -*-
"""
arbol_visual.py - Visualizador de Árboles de Recorrido con PyQt5
Este módulo genera un árbol sintáctico y lo visualiza con los recorridos preorden, inorden y postorden.
"""

from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTabWidget, QGraphicsView, QGraphicsScene, QGraphicsRectItem, \
    QGraphicsTextItem, QGraphicsLineItem, QMessageBox, QToolBar, QAction, QLabel, QWidget
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QColor, QBrush, QPen, QFont, QPainter
import javalang
from copy import deepcopy


# Clase NodoArbol (sin cambios)
class NodoArbol:
    def __init__(self, tipo, valor=None, linea=None):
        self.tipo = tipo
        self.valor = valor if valor else tipo
        self.linea = linea
        self.hijos = []
        self.padre = None
        self.x = 0
        self.y = 0
        self.width = 100
        self.height = 40
        self.orden_preorden = 0
        self.orden_inorden = 0
        self.orden_postorden = 0

    def agregar_hijo(self, nodo):
        self.hijos.append(nodo)
        nodo.padre = self
        return nodo

    def __str__(self):
        return f"{self.tipo}: {self.valor}" if self.valor else self.tipo


# Clase Arbol (sin cambios)
class Arbol:
    def __init__(self):
        self.raiz = None
        self.contador_preorden = 1
        self.contador_inorden = 1
        self.contador_postorden = 1

    def construir_de_codigo(self, codigo):
        try:
            tree = javalang.parse.parse(codigo)
            self.raiz = NodoArbol("UnidadCompilación")
            self._construir_arbol(tree, self.raiz)
            self.calcular_orden_recorridos()
            return True
        except javalang.parser.JavaSyntaxError as e:
            print(f"Error de sintaxis en el código Java: {str(e)}")
            return False
        except Exception as e:
            print(f"Error al construir árbol: {str(e)}")
            return False

    def _construir_arbol(self, nodo, nodo_arbol):
        if not nodo:
            return
        tipo_nodo = nodo.__class__.__name__
        valor = None

        if tipo_nodo == "MemberReference":
            valor = getattr(nodo, "member", None)
            tipo_nodo = "Referencia"
            if valor and hasattr(nodo, "qualifier") and nodo.qualifier:
                valor = f"{nodo.qualifier}.{valor}"
            elif valor:
                tipo_nodo = "Miembro"
        elif tipo_nodo == "BlockStatement":
            tipo_nodo = "Bloque"
            valor = "{ ... }"
        elif tipo_nodo == "StatementExpression":
            tipo_nodo = "Expresión"
            if hasattr(nodo, "expression"):
                if hasattr(nodo.expression, "operator") and hasattr(nodo.expression, "left") and hasattr(
                        nodo.expression, "right"):
                    valor = f"{getattr(nodo.expression.left, 'name', nodo.expression.left)} {nodo.expression.operator} {getattr(nodo.expression.right, 'value', nodo.expression.right)}"
                elif hasattr(nodo.expression, "member"):
                    valor = str(nodo.expression.member)
        elif tipo_nodo == "VariableDeclarator":
            tipo_nodo = "Variable"
            valor = getattr(nodo, "name", None)
        elif tipo_nodo == "Assignment":
            tipo_nodo = "Asignación"
            if hasattr(nodo, "left") and hasattr(nodo, "right"):
                left = getattr(nodo.left, "name", str(nodo.left))
                right = getattr(nodo.right, "value", str(nodo.right))
                valor = f"{left} = {right}"
        elif tipo_nodo == "MethodInvocation":
            tipo_nodo = "LlamadaMétodo"
            valor = getattr(nodo, "member", None)
            if valor and hasattr(nodo, "qualifier") and nodo.qualifier:
                valor = f"{nodo.qualifier}.{valor}"
        elif tipo_nodo == "ClassDeclaration":
            tipo_nodo = "Clase"
            valor = getattr(nodo, "name", None)
        elif tipo_nodo == "MethodDeclaration":
            tipo_nodo = "Método"
            valor = getattr(nodo, "name", None)
        elif tipo_nodo == "BasicType":
            tipo_nodo = "TipoDato"
            valor = getattr(nodo, "name", None)
        else:
            if hasattr(nodo, "name"):
                valor = nodo.name
            elif hasattr(nodo, "value") and nodo.value is not None:
                valor = str(nodo.value)
            elif hasattr(nodo, "operator"):
                valor = nodo.operator
            elif hasattr(nodo, "type") and nodo.type:
                valor = str(nodo.type.name) if hasattr(nodo.type, "name") else str(nodo.type)

        nodo_actual = nodo_arbol.agregar_hijo(NodoArbol(tipo_nodo, valor))

        for attr_name, attr_value in nodo.__dict__.items():
            if isinstance(attr_value, (list, tuple)):
                for item in attr_value:
                    if isinstance(item, javalang.ast.Node):
                        self._construir_arbol(item, nodo_actual)
            elif isinstance(attr_value, javalang.ast.Node):
                self._construir_arbol(attr_value, nodo_actual)

    def calcular_orden_recorridos(self):
        if not self.raiz:
            return
        self.contador_preorden = 1
        self.contador_inorden = 1
        self.contador_postorden = 1
        self._recorrido_preorden(self.raiz)
        self._recorrido_inorden(self.raiz)
        self._recorrido_postorden(self.raiz)

    def _recorrido_preorden(self, nodo):
        if nodo is None:
            return []
        nodo.orden_preorden = self.contador_preorden
        self.contador_preorden += 1
        resultado = [nodo]
        for hijo in nodo.hijos:
            resultado.extend(self._recorrido_preorden(hijo))
        return resultado

    def _recorrido_inorden(self, nodo):
        if nodo is None:
            return []
        resultado = []
        mitad = len(nodo.hijos) // 2
        for i in range(mitad):
            resultado.extend(self._recorrido_inorden(nodo.hijos[i]))
        nodo.orden_inorden = self.contador_inorden
        self.contador_inorden += 1
        resultado.append(nodo)
        for i in range(mitad, len(nodo.hijos)):
            resultado.extend(self._recorrido_inorden(nodo.hijos[i]))
        return resultado

    def _recorrido_postorden(self, nodo):
        if nodo is None:
            return []
        resultado = []
        for hijo in nodo.hijos:
            resultado.extend(self._recorrido_postorden(hijo))
        nodo.orden_postorden = self.contador_postorden
        self.contador_postorden += 1
        resultado.append(nodo)
        return resultado


# Clase DibujanteArbol (modificada para usar copia del árbol)
class DibujanteArbol:
    def __init__(self, escena, modo_recorrido=None):
        self.escena = escena
        self.modo_recorrido = modo_recorrido
        self.colores_nodos = {}

    def _generar_color(self, tipo, nivel):
        if tipo not in self.colores_nodos:
            colores_base = [
                (205, 132, 143),  # Rosa más oscuro
                (123, 166, 180),  # Azul más oscuro
                (94, 188, 94),  # Verde más oscuro
                (205, 205, 174),  # Amarillo más oscuro
                (171, 110, 171),  # Lila más oscuro
                (205, 168, 135),  # Melocotón más oscuro
            ]
            idx = hash(tipo) % len(colores_base)
            r, g, b = colores_base[idx]
            r = min(255, r + nivel * 10)
            g = min(255, g + nivel * 10)
            b = min(255, b + nivel * 10)
            self.colores_nodos[tipo] = QColor(r, g, b).name()
        return self.colores_nodos[tipo]

    def dibujar_arbol(self, arbol):
        self.escena.clear()
        if not arbol.raiz:
            QMessageBox.warning(None, "Error", "El árbol no tiene una raíz válida.")
            return

        # Crear una copia profunda del árbol para no modificar el original
        arbol_copia = self._copiar_arbol(arbol.raiz)

        # Obtener todos los nodos en orden jerárquico (para estructura)
        nodos_jerarquicos = self._obtener_nodos_jerarquicos(arbol_copia)

        # Obtener nodos en el orden del recorrido
        nodos_ordenados = []
        if self.modo_recorrido == "preorden":
            nodos_ordenados = self._recorrido_preorden(arbol.raiz)
        elif self.modo_recorrido == "inorden":
            nodos_ordenados = self._recorrido_inorden(arbol.raiz)
        elif self.modo_recorrido == "postorden":
            nodos_ordenados = self._recorrido_postorden(arbol.raiz)

        # Reasignar datos de nodos en la copia según el recorrido
        if len(nodos_jerarquicos) == len(nodos_ordenados):
            for nodo_jerarquico, nodo_ordenado in zip(nodos_jerarquicos, nodos_ordenados):
                nodo_jerarquico.tipo = nodo_ordenado.tipo
                nodo_jerarquico.valor = nodo_ordenado.valor
                nodo_jerarquico.linea = nodo_ordenado.linea

        # Calcular posiciones con la estructura original usando la copia
        self._calcular_posiciones(arbol_copia)
        self._dibujar_nodos_y_conexiones(arbol_copia)

    def _copiar_arbol(self, nodo):
        """Crea una copia profunda del árbol."""
        if nodo is None:
            return None
        nuevo_nodo = NodoArbol(nodo.tipo, nodo.valor, nodo.linea)
        nuevo_nodo.x = nodo.x
        nuevo_nodo.y = nodo.y
        nuevo_nodo.width = nodo.width
        nuevo_nodo.height = nodo.height
        nuevo_nodo.orden_preorden = nodo.orden_preorden
        nuevo_nodo.orden_inorden = nodo.orden_inorden
        nuevo_nodo.orden_postorden = nodo.orden_postorden
        for hijo in nodo.hijos:
            nuevo_hijo = self._copiar_arbol(hijo)
            nuevo_nodo.agregar_hijo(nuevo_hijo)
        return nuevo_nodo

    def _obtener_nodos_jerarquicos(self, nodo):
        """Obtiene todos los nodos en orden jerárquico (como en el dibujo original)."""
        if nodo is None:
            return []
        resultado = [nodo]
        for hijo in nodo.hijos:
            resultado.extend(self._obtener_nodos_jerarquicos(hijo))
        return resultado

    def _recorrido_preorden(self, nodo):
        if nodo is None:
            return []
        resultado = [nodo]
        for hijo in nodo.hijos:
            resultado.extend(self._recorrido_preorden(hijo))
        return resultado

    def _recorrido_inorden(self, nodo):
        if nodo is None:
            return []
        resultado = []
        mitad = len(nodo.hijos) // 2
        for i in range(mitad):
            resultado.extend(self._recorrido_inorden(nodo.hijos[i]))
        resultado.append(nodo)
        for i in range(mitad, len(nodo.hijos)):
            resultado.extend(self._recorrido_inorden(nodo.hijos[i]))
        return resultado

    def _recorrido_postorden(self, nodo):
        if nodo is None:
            return []
        resultado = []
        for hijo in nodo.hijos:
            resultado.extend(self._recorrido_postorden(hijo))
        resultado.append(nodo)
        return resultado

    def _calcular_posiciones(self, nodo, nivel=0, x_base=0, ancho_base=2000):
        espacio_vertical = 120
        nodo.y = nivel * espacio_vertical

        texto = nodo.valor if nodo.valor else nodo.tipo
        texto_item = QGraphicsTextItem(texto)
        font = QFont("Arial", 12)
        texto_item.setFont(font)
        texto_width = texto_item.boundingRect().width()
        texto_height = texto_item.boundingRect().height()

        margen_horizontal = 20
        margen_vertical = 15
        nodo.width = texto_width + margen_horizontal
        nodo.height = texto_height + margen_vertical

        if not nodo.hijos:
            nodo.x = x_base + nodo.width / 2
            return nodo.width

        ancho_total = 0
        separacion = 40
        posiciones_hijos = []
        for hijo in nodo.hijos:
            ancho_hijo = self._calcular_posiciones(hijo, nivel + 1, x_base + ancho_total, ancho_base / len(nodo.hijos))
            posiciones_hijos.append(ancho_total + ancho_hijo / 2)
            ancho_total += ancho_hijo + separacion

        if posiciones_hijos:
            nodo.x = x_base + sum(posiciones_hijos) / len(posiciones_hijos)
        else:
            nodo.x = x_base + nodo.width / 2

        return ancho_total - separacion if nodo.hijos else nodo.width

    def _dibujar_nodos_y_conexiones(self, nodo, nivel=0):
        self._dibujar_nodo(nodo, nodo.x - nodo.width / 2, nodo.y, nivel)
        for hijo in nodo.hijos:
            color_linea = self._generar_color(nodo.tipo, nivel)
            linea = QGraphicsLineItem(
                nodo.x, nodo.y + nodo.height,
                hijo.x, hijo.y
            )
            linea.setPen(QPen(QColor(color_linea), 1.5))
            self.escena.addItem(linea)
            self._dibujar_nodos_y_conexiones(hijo, nivel + 1)

    def _dibujar_nodo(self, nodo, x, y, nivel):
        escala = 1.3 if nivel == 0 else 1.1 if nivel == 1 else 0.9
        width = nodo.width * escala
        height = nodo.height * escala

        rectangulo = QGraphicsRectItem(x, y, width, height)
        color = self._generar_color(nodo.tipo, nivel)
        rectangulo.setBrush(QBrush(QColor(color)))
        rectangulo.setPen(QPen(QColor("#000000"), 2))
        self.escena.addItem(rectangulo)

        texto_valor = nodo.valor if nodo.valor else nodo.tipo
        if len(texto_valor) > 30:
            texto_valor = texto_valor[:27] + "..."
        texto_item = QGraphicsTextItem(texto_valor)
        font_size = int(12 * escala)
        texto_item.setFont(QFont("Arial", font_size))
        texto_item.setDefaultTextColor(QColor("#000000"))
        texto_width = texto_item.boundingRect().width()
        texto_height = texto_item.boundingRect().height()
        texto_item.setPos(x + width / 2 - texto_width / 2, y + height / 2 - texto_height / 2)
        self.escena.addItem(texto_item)


# Clase VistaArbolGrafica (sin cambios)
class VistaArbolGrafica(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.escala = 1.0
        self.factor_zoom = 1.2
        self.escena = QGraphicsScene(self)
        self.setScene(self.escena)
        self.setRenderHint(QPainter.Antialiasing)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)

    def wheelEvent(self, event):
        factor = self.factor_zoom if event.angleDelta().y() > 0 else 1 / self.factor_zoom
        nueva_escala = self.escala * factor
        if 0.25 <= nueva_escala <= 4.0:
            self.scale(factor, factor)
            self.escala = nueva_escala
        super().wheelEvent(event)


# Clase VisualizadorArbol (sin cambios)
class VisualizadorArbol(QDialog):
    def __init__(self, arbol, parent=None):
        super().__init__(parent)
        self.arbol = arbol
        self.setWindowTitle("Visualizador de Árboles - Recorridos")
        self.setMinimumSize(1400, 800)
        self.setModal(True)
        self._configurar_ui()
        self._mostrar_arbol("preorden")

    def _configurar_ui(self):
        layout = QVBoxLayout(self)
        self.tab_widget = QTabWidget()
        self.vistas = {
            "preorden": VistaArbolGrafica(),
            "inorden": VistaArbolGrafica(),
            "postorden": VistaArbolGrafica()
        }
        self.dibujantes = {
            "preorden": DibujanteArbol(self.vistas["preorden"].escena, "preorden"),
            "inorden": DibujanteArbol(self.vistas["inorden"].escena, "inorden"),
            "postorden": DibujanteArbol(self.vistas["postorden"].escena, "postorden")
        }

        for nombre, vista in self.vistas.items():
            tab = QWidget()
            tab_layout = QVBoxLayout(tab)
            toolbar = QToolBar("Zoom")
            toolbar.addAction("Zoom +", lambda: self._zoom_in(vista))
            toolbar.addAction("Zoom -", lambda: self._zoom_out(vista))
            toolbar.addAction("Reset Zoom", lambda: self._reset_zoom(vista))
            tab_layout.addWidget(toolbar)
            tab_layout.addWidget(
                QLabel("Instrucciones: Usa el ratón para hacer zoom (rueda) y desplazarte (clic y arrastrar)"))
            tab_layout.addWidget(vista)
            self.tab_widget.addTab(tab, nombre.capitalize())

        self.tab_widget.currentChanged.connect(self._cambiar_pestana)
        layout.addWidget(self.tab_widget)

    def _zoom_in(self, vista):
        vista.scale(1.2, 1.2)
        vista.escala *= 1.2

    def _zoom_out(self, vista):
        vista.scale(1 / 1.2, 1 / 1.2)
        vista.escala /= 1.2

    def _reset_zoom(self, vista):
        vista.scale(1 / vista.escala, 1 / vista.escala)
        vista.escala = 1.0

    def _cambiar_pestana(self, indice):
        modos = ["preorden", "inorden", "postorden"]
        self._mostrar_arbol(modos[indice])

    def _mostrar_arbol(self, tipo):
        for nombre, dibujante in self.dibujantes.items():
            dibujante.dibujar_arbol(self.arbol)
        margen = 50
        for vista in self.vistas.values():
            rect = vista.scene().itemsBoundingRect()
            rect.adjust(-margen, -margen, margen, margen)
            vista.fitInView(rect, Qt.KeepAspectRatio)
        self.tab_widget.setCurrentIndex(["preorden", "inorden", "postorden"].index(tipo))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        margen = 50
        for vista in self.vistas.values():
            rect = vista.scene().itemsBoundingRect()
            rect.adjust(-margen, -margen, margen, margen)
            vista.fitInView(rect, Qt.KeepAspectRatio)


# Función principal (sin cambios)
def mostrar_arbol_recorridos(codigo, parent=None):
    try:
        arbol = Arbol()
        if not arbol.construir_de_codigo(codigo):
            QMessageBox.warning(parent, "Error", "No se pudieron generar los árboles debido a errores en el código.")
            return False
        visualizador = VisualizadorArbol(arbol, parent)
        visualizador.exec_()
        return True
    except Exception as e:
        import traceback
        print(f"Error al mostrar el árbol: {e}")
        traceback.print_exc()
        QMessageBox.critical(parent, "Error", f"Ocurrió un error al generar la visualización: {e}")
        return False
