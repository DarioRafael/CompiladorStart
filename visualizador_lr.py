#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTreeWidget, QTreeWidgetItem,
                             QPushButton, QLabel, QSplitter, QWidget, QScrollArea, QFrame,
                             QGraphicsView, QGraphicsScene, QGraphicsRectItem, QGraphicsTextItem,
                             QGraphicsEllipseItem, QGraphicsPathItem, QGraphicsPolygonItem,
                             QGraphicsDropShadowEffect)
from PyQt5.QtGui import (QColor, QBrush, QFont, QPen, QFontMetrics, QPainter, QLinearGradient,
                         QRadialGradient, QPainterPath, QPolygonF)
from PyQt5.QtCore import Qt, QRectF, QPointF, QSizeF, pyqtSignal, QPoint

import math
import re


class NodoLR:
    """Enhanced class to represent a node in the LR tree with more visual options and grammar-specific attributes"""

    def __init__(self, etiqueta, tipo=None, valor=None, linea=None, categoria=None):
        self.etiqueta = etiqueta
        self.tipo = tipo
        self.valor = valor
        self.linea = linea
        self.categoria = categoria  # Grammar category (e.g., 'declaracion', 'expresion', 'sentencia')
        self.regla = None  # Grammar rule that produced this node
        self.token_original = None  # Original token text when applicable
        self.hijos = []

        # Position and size for graphical representation
        self.x = 0
        self.y = 0
        self.width = 0
        self.height = 0

        # Visual styling
        self.color_texto = "#FFFFFF"
        self.color_fondo = "#2D2D30"
        self.color_borde = "#6D6D6D"
        self.negrita = False
        self.italico = False
        self.tamanio = 10
        self.forma = "rect"  # Can be "rect", "ellipse", "diamond", "hexagon", "octagon"
        self.gradiente = False
        self.sombra = False
        self.radio_esquinas = 5

    def agregar_hijo(self, hijo):
        """Adds a child node and returns it for chaining"""
        self.hijos.append(hijo)
        return hijo

    def texto_display(self):
        """Generates the text to display in the node with more detailed information"""
        partes = []

        # Start with the primary label
        if self.regla:
            partes.append(f"{self.etiqueta} [{self.regla}]")
        else:
            partes.append(self.etiqueta)

        # Add value if present and different from etiqueta
        if self.valor and self.valor != self.etiqueta:
            # Handle special cases for better display
            if isinstance(self.valor, (int, float)):
                partes.append(f"Valor: {self.valor}")
            elif self.valor.startswith('"') and self.valor.endswith('"'):
                # For string literals
                partes.append(f"Literal: {self.valor}")
            else:
                partes.append(f"{self.valor}")

        # Add token or symbol detail if present
        if self.token_original and self.token_original != self.valor:
            partes.append(f"Token: {self.token_original}")

        # Add line number if present
        if self.linea:
            partes.append(f"línea {self.linea}")

        return " - ".join(partes)

    def establecer_estilo(self, color_texto=None, color_fondo=None, color_borde=None,
                          negrita=False, italico=False, tamanio=10, forma="rect",
                          gradiente=False, sombra=False, radio_esquinas=5):
        """Sets the visual style of the node"""
        if color_texto: self.color_texto = color_texto
        if color_fondo: self.color_fondo = color_fondo
        if color_borde: self.color_borde = color_borde
        self.negrita = negrita
        self.italico = italico
        self.tamanio = tamanio
        self.forma = forma
        self.gradiente = gradiente
        self.sombra = sombra
        self.radio_esquinas = radio_esquinas


class ArbolLRScene(QGraphicsScene):
    """Enhanced scene for visualizing the LR tree with improved grammar-aware drawing"""

    def __init__(self, parent=None):
        super().__init__(parent)
        # Colors for background and lines
        self.setBackgroundBrush(QBrush(QColor("#1E1E1E")))
        self.line_color = QColor("#4D4D4D")
        self.line_pen = QPen(self.line_color, 1.5, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)

        # Node spacing parameters - smaller for more compact trees
        self.espaciado_horizontal = 30
        self.espaciado_vertical = 60
        self.espaciado_hermanos = 15  # Space between sibling nodes
        self.padding_nodo = 12
        self.raiz = None
        self.margen = 20

        # For complex trees
        self.max_ancho_nivel = {}  # Track max width per level

    def construir_arbol(self, raiz):
        """Builds the graphical representation of the tree from a root node"""
        self.raiz = raiz
        self.clear()

        # Reset level tracking
        self.max_ancho_nivel = {}

        # First pass: Calculate node sizes
        self._calcular_tamanos_nodos(raiz)

        # Second pass: Calculate positions with improved algorithm for complex trees
        self._calcular_posiciones_mejorado(raiz, 0, self.margen)

        # Draw connections between nodes (parent to children)
        self._dibujar_conexiones(raiz)

        # Draw all nodes
        self._dibujar_nodos(raiz)

        # Set scene rectangle to include all items with margin
        self.setSceneRect(self.itemsBoundingRect().adjusted(-self.margen, -self.margen,
                                                            self.margen, self.margen))

    def _calcular_tamanos_nodos(self, nodo):
        """Pre-calculates the sizes of all nodes based on text content"""
        # Create font to measure text size
        font = QFont("Consolas", nodo.tamanio)
        font.setBold(nodo.negrita)
        font.setItalic(nodo.italico)

        metrics = QFontMetrics(font)
        texto = nodo.texto_display()
        rect = metrics.boundingRect(texto)

        # Set node size based on text - ensure integers to avoid float errors
        nodo.width = int(rect.width() + self.padding_nodo * 2)
        nodo.height = int(rect.height() + self.padding_nodo * 2)

        # Calculate sizes for all children recursively
        for hijo in nodo.hijos:
            self._calcular_tamanos_nodos(hijo)

    def _calcular_posiciones_mejorado(self, nodo, nivel, offset_x):
        """Improved position calculation algorithm that handles complex trees better"""
        # If this level hasn't been processed yet, initialize it
        if nivel not in self.max_ancho_nivel:
            self.max_ancho_nivel[nivel] = 0

        # Set vertical position based on level
        nodo.y = int(nivel * self.espaciado_vertical)

        # If no children, this is a leaf node - simple positioning
        if not nodo.hijos:
            nodo.x = int(offset_x)
            # Update max width for this level
            nuevo_ancho = offset_x + nodo.width
            self.max_ancho_nivel[nivel] = max(self.max_ancho_nivel[nivel], nuevo_ancho)
            return offset_x + nodo.width + self.espaciado_horizontal

        # Process all children first to determine their positions
        hijo_offset_x = offset_x
        for hijo in nodo.hijos:
            hijo_offset_x = self._calcular_posiciones_mejorado(hijo, nivel + 1, hijo_offset_x)
            # Add spacing between siblings
            if hijo != nodo.hijos[-1]:  # If not the last child
                hijo_offset_x += self.espaciado_hermanos

        # Position this node centered above its children
        primer_hijo = nodo.hijos[0]
        ultimo_hijo = nodo.hijos[-1]
        centro_x = (primer_hijo.x + ultimo_hijo.x + ultimo_hijo.width) / 2 - nodo.width / 2
        nodo.x = int(centro_x)

        # Ensure node doesn't overlap with adjacent nodes at the same level
        if nodo.x < offset_x:
            desplazamiento = offset_x - nodo.x
            # Shift this node and all its children
            self._desplazar_nodo_y_descendientes(nodo, desplazamiento, 0)

        # Update max width for this level
        nuevo_ancho = nodo.x + nodo.width
        self.max_ancho_nivel[nivel] = max(self.max_ancho_nivel[nivel], nuevo_ancho)

        # Return the rightmost edge of this subtree
        rightmost = max(offset_x + nodo.width, hijo_offset_x)
        return rightmost

    def _desplazar_nodo_y_descendientes(self, nodo, desplazamiento_x, desplazamiento_y):
        """Shifts a node and all its descendants by the specified amounts"""
        nodo.x += int(desplazamiento_x)
        nodo.y += int(desplazamiento_y)

        for hijo in nodo.hijos:
            self._desplazar_nodo_y_descendientes(hijo, desplazamiento_x, desplazamiento_y)

    def _dibujar_nodos(self, nodo):
        """Draws all nodes in the scene with enhanced grammar-aware visuals"""
        # Draw the node shape with specialized forms for grammar nodes
        x = int(nodo.x)
        y = int(nodo.y)
        width = int(nodo.width)
        height = int(nodo.height)

        if nodo.forma == "ellipse" or nodo.forma == "diamond" or nodo.forma == "hexagon" or nodo.forma == "octagon":
            # Simplificar a rectángulos para evitar problemas con formas especiales
            shape = QGraphicsRectItem(x, y, width, height, None)
        else:  # rect es el valor por defecto
            if nodo.radio_esquinas > 0:
                # Rectángulos con esquinas redondeadas
                path = QPainterPath()
                path.addRoundedRect(x, y, width, height, nodo.radio_esquinas, nodo.radio_esquinas)
                shape = QGraphicsPathItem(path)
            else:
                # Rectángulos normales
                shape = QGraphicsRectItem(x, y, width, height, None)

        # Apply fill style with grammar-specific gradients
        if nodo.gradiente:
            # Different gradient styles for different node types
            if nodo.categoria in ('sentencia', 'flujo'):
                # Vertical gradient
                gradient = QLinearGradient(nodo.x, nodo.y, nodo.x, nodo.y + nodo.height)
                gradient.setColorAt(0, QColor(nodo.color_fondo).lighter(120))
                gradient.setColorAt(1, QColor(nodo.color_fondo).darker(120))
            elif nodo.categoria in ('expresion', 'operador'):
                # Radial gradient for emphasis
                center_x = nodo.x + nodo.width / 2
                center_y = nodo.y + nodo.height / 2
                radius = max(nodo.width, nodo.height) / 2
                gradient = QRadialGradient(center_x, center_y, radius)
                gradient.setColorAt(0, QColor(nodo.color_fondo).lighter(130))
                gradient.setColorAt(1, QColor(nodo.color_fondo))
            else:
                # Diagonal gradient for other nodes
                gradient = QLinearGradient(nodo.x, nodo.y, nodo.x + nodo.width, nodo.y + nodo.height)
                gradient.setColorAt(0, QColor(nodo.color_fondo).lighter(110))
                gradient.setColorAt(1, QColor(nodo.color_fondo).darker(110))
            shape.setBrush(QBrush(gradient))
        else:
            shape.setBrush(QBrush(QColor(nodo.color_fondo)))

        # Apply border with thicker borders for important grammar elements
        border_width = 1.5
        if nodo.categoria in ('programa', 'clase', 'metodo'):
            border_width = 2.5
        shape.setPen(QPen(QColor(nodo.color_borde), border_width))

        # Add shadow effect for emphasis on important nodes
        if nodo.sombra:
            shadow = QGraphicsDropShadowEffect()
            shadow.setBlurRadius(10)
            shadow.setColor(QColor(0, 0, 0, 150))
            shadow.setOffset(3, 3)
            shape.setGraphicsEffect(shadow)

        self.addItem(shape)

        # Draw the node text
        text_item = QGraphicsTextItem(nodo.texto_display())
        font = QFont("Consolas", nodo.tamanio)
        font.setBold(nodo.negrita)
        font.setItalic(nodo.italico)
        text_item.setFont(font)
        text_item.setDefaultTextColor(QColor(nodo.color_texto))

        # Position text centered in the node
        text_rect = text_item.boundingRect()
        text_x = nodo.x + (nodo.width - text_rect.width()) / 2
        text_y = nodo.y + (nodo.height - text_rect.height()) / 2
        text_item.setPos(text_x, text_y)

        self.addItem(text_item)

        # Draw children recursively
        for hijo in nodo.hijos:
            self._dibujar_nodos(hijo)

    def _dibujar_conexiones(self, nodo):
        """Draws connections between a node and its children with improved grammar-aware visuals"""
        for hijo in nodo.hijos:
            # Start point (bottom center of parent node)
            inicio_x = int(nodo.x + nodo.width / 2)
            inicio_y = int(nodo.y + nodo.height)

            # End point (top center of child node)
            fin_x = int(hijo.x + hijo.width / 2)
            fin_y = int(hijo.y)

            # Use a curved path for more complex trees
            path = QPainterPath()
            path.moveTo(inicio_x, inicio_y)

            # Use curved path for a more elegant look
            control_y = int((inicio_y + fin_y) / 2)
            path.cubicTo(
                int(inicio_x), control_y,  # First control point
                int(fin_x), control_y,  # Second control point
                int(fin_x), int(fin_y)  # End point
            )

            # Customize line style based on grammar relationship
            line_pen = QPen(self.line_pen)

            # Specialized line styles based on grammar relationships
            if hijo.categoria == 'terminal':
                # Terminal symbols get dotted lines
                line_pen.setStyle(Qt.DotLine)
            elif hijo.categoria == 'no_terminal':
                # Non-terminal symbols get dashed lines
                line_pen.setStyle(Qt.DashLine)
            elif hijo.categoria in ('sentencia', 'flujo'):
                # Control flow uses thicker lines
                line_pen.setWidth(2)

            line = QGraphicsPathItem(path)
            line.setPen(line_pen)
            self.addItem(line)

            # Add arrow head - convert all coordinates to int
            arrow_size = 6
            angle = math.atan2(fin_y - control_y, fin_x - inicio_x)
            angle_degrees = math.degrees(angle)

            arrow_p1 = QPointF(fin_x, fin_y) - QPointF(
                int(arrow_size * math.cos(math.radians(angle_degrees + 150))),
                int(arrow_size * math.sin(math.radians(angle_degrees + 150))))

            arrow_p2 = QPointF(fin_x, fin_y) - QPointF(
                int(arrow_size * math.cos(math.radians(angle_degrees - 150))),
                int(arrow_size * math.sin(math.radians(angle_degrees - 150))))

            polygon = QPolygonF([QPointF(fin_x, fin_y), arrow_p1, arrow_p2])
            arrow_head = QGraphicsPolygonItem(polygon)
            arrow_head.setBrush(QBrush(self.line_color))
            arrow_head.setPen(QPen(Qt.NoPen))
            self.addItem(arrow_head)

            # Draw connections for this child's children
            self._dibujar_conexiones(hijo)


class ArbolLRView(QGraphicsView):
    """Enhanced view for the LR tree with zoom and panning support"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.TextAntialiasing)
        self.setRenderHint(QPainter.SmoothPixmapTransform)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.setOptimizationFlag(QGraphicsView.DontSavePainterState)
        self.scale_factor = 1.15
        self.min_scale = 0.1
        self.max_scale = 10.0

    def wheelEvent(self, event):
        """Implements zoom with mouse wheel"""
        factor = self.scale_factor

        if event.angleDelta().y() < 0:
            # Zoom out
            factor = 1.0 / factor

        # Apply scale with limits
        current_scale = self.transform().m11()
        new_scale = current_scale * factor

        if new_scale < self.min_scale:
            factor = self.min_scale / current_scale
        elif new_scale > self.max_scale:
            factor = self.max_scale / current_scale

        self.scale(factor, factor)


class VentanaArbolLR(QDialog):
    """Enhanced window for visualizing the LR derivation tree"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Árbol de Derivación LR Detallado")
        self.resize(1400, 900)
        self.setStyleSheet("""
            QDialog {
                background-color: #252526;
            }
            QLabel {
                color: #D4D4D4;
            }
            QPushButton {
                background-color: #3E3E42;
                color: #FFFFFF;
                border: 1px solid #5A5A5A;
                padding: 5px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #2D2D30;
                border: 1px solid #6A6A6A;
            }
        """)

        # Create UI elements
        self.layout_principal = QVBoxLayout(self)
        self.layout_principal.setContentsMargins(10, 10, 10, 10)

        # Top bar with controls
        self.layout_controles = QHBoxLayout()

        self.lbl_info = QLabel(
            "Árbol de derivación LR detallado. Use la rueda del ratón para zoom, arrastre para moverse y doble clic para centrar.")
        self.lbl_info.setStyleSheet("font-size: 11px;")
        self.layout_controles.addWidget(self.lbl_info, 1)

        self.btn_expandir = QPushButton("Expandir Todo")
        self.btn_expandir.clicked.connect(self.expandir_todo)
        self.layout_controles.addWidget(self.btn_expandir)

        self.btn_colapsar = QPushButton("Colapsar Todo")
        self.btn_colapsar.clicked.connect(self.colapsar_todo)
        self.layout_controles.addWidget(self.btn_colapsar)

        self.btn_zoom_ajustar = QPushButton("Ajustar Vista")
        self.btn_zoom_ajustar.clicked.connect(self.ajustar_vista)
        self.layout_controles.addWidget(self.btn_zoom_ajustar)

        self.btn_cerrar = QPushButton("Cerrar")
        self.btn_cerrar.clicked.connect(self.close)
        self.layout_controles.addWidget(self.btn_cerrar)

        self.layout_principal.addLayout(self.layout_controles)

        # Create view for the LR tree
        self.scene = ArbolLRScene()
        self.view = ArbolLRView(self.scene)
        self.view.setMouseTracking(True)
        self.view.viewport().setCursor(Qt.OpenHandCursor)
        self.layout_principal.addWidget(self.view)

        # Variables to store the tree
        self.arbol_raiz = None

    def establecer_arbol(self, raiz):
        """Sets and displays the tree from the given root"""
        self.arbol_raiz = raiz
        self.scene.construir_arbol(raiz)
        self.ajustar_vista()

    def ajustar_vista(self):
        """Adjusts the view to fit the entire tree"""
        self.view.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)
        self.view.centerOn(self.scene.sceneRect().center())

    def expandir_todo(self):
        """Expands all nodes in the tree"""
        # In this graphical implementation, all nodes are always expanded
        # Just readjust the view
        self.ajustar_vista()

    def colapsar_todo(self):
        """Collapses all nodes in the tree except the root"""
        # In this graphical implementation, collapsing doesn't apply directly
        # Just readjust the view
        self.ajustar_vista()

    def mouseDoubleClickEvent(self, event):
        """Centers the view on double click"""
        if event.button() == Qt.LeftButton:
            self.ajustar_vista()


def _analizar_expresion(expresion):
    """
    Analyzes an expression to break it down into more detailed grammar components
    Returns a tree of nodes representing the expression's grammar structure
    """
    # Basic lexical analysis to identify tokens
    if not expresion or expresion.strip() == '':
        return None

    # Handle literal values
    if expresion.isdigit():
        nodo = NodoLR("Literal Entero", "literal", expresion)
        nodo.categoria = "terminal"
        nodo.establecer_estilo(
            color_texto="#B5CEA8",  # Light green for numbers
            color_fondo="#1E1E1E",
            negrita=True,
            tamanio=10
        )
        return nodo

    if expresion.startswith('"') and expresion.endswith('"'):
        nodo = NodoLR("Literal Cadena", "literal", expresion)
        nodo.categoria = "terminal"
        nodo.establecer_estilo(
            color_texto="#CE9178",  # Light red for strings
            color_fondo="#1E1E1E",
            negrita=True,
            tamanio=10
        )
        return nodo

    # Check for operations with binary operators
    operators = ['+', '-', '*', '/', '%', '==', '!=', '<=', '>=', '<', '>', '&&', '||']
    for op in operators:
        if op in expresion:
            # Don't split within quotes
            parts = []
            in_quotes = False
            start = 0

            for i, char in enumerate(expresion):
                if char == '"':
                    in_quotes = not in_quotes
                elif char == op and not in_quotes and i > 0:
                    if (op == '+' or op == '-') and i > 0 and expresion[i - 1] in '+-*/=!<>':
                        # This is likely a unary operator, not binary
                        continue
                    parts = [expresion[:i].strip(), expresion[i + len(op):].strip()]
                    break

            if len(parts) == 2:
                # Create operator node
                nodo = NodoLR(f"Operación {op}", "operador", op)
                nodo.categoria = "expresion"
                nodo.establecer_estilo(
                    color_texto="#D4D4D4",  # Light gray
                    color_fondo="#2D2D30",
                    color_borde="#6D6D6D",
                    negrita=True,
                    tamanio=10,
                    forma="ellipse"
                )

                # Left operand
                izq = _analizar_expresion(parts[0])
                if izq:
                    nodo.agregar_hijo(izq)

                # Right operand
                der = _analizar_expresion(parts[1])
                if der:
                    nodo.agregar_hijo(der)

                return nodo

    # Check for method calls
    if '(' in expresion and ')' in expresion:
        nombre_metodo = expresion.split('(')[0].strip()
        args_str = expresion[len(nombre_metodo) + 1:].rsplit(')', 1)[0].strip()

        nodo = NodoLR("Llamada a Método", "llamada", nombre_metodo)
        nodo.categoria = "expresion"
        nodo.establecer_estilo(
            color_texto="#DCDCAA",  # Yellow for function calls
            color_fondo="#2D2D30",
            color_borde="#DCDCAA",
            negrita=True,
            tamanio=10,
            forma="rect",
            radio_esquinas=5
        )

        # Add method name as a child
        nombre_nodo = NodoLR("Nombre", "identificador", nombre_metodo)
        nombre_nodo.categoria = "terminal"
        nombre_nodo.establecer_estilo(
            color_texto="#DCDCAA",
            color_fondo="#1E1E1E",
            tamanio=9
        )
        nodo.agregar_hijo(nombre_nodo)

        # Add arguments if any
        if args_str:
            args = []
            current_arg = ""
            paren_depth = 0
            in_quotes = False

            for c in args_str:
                if c == '"':
                    in_quotes = not in_quotes
                elif c == '(' and not in_quotes:
                    paren_depth += 1
                elif c == ')' and not in_quotes:
                    paren_depth -= 1
                elif c == ',' and paren_depth == 0 and not in_quotes:
                    args.append(current_arg.strip())
                    current_arg = ""
                    continue
                current_arg += c

            if current_arg:
                args.append(current_arg.strip())

            for i, arg in enumerate(args):
                arg_nodo = NodoLR(f"Argumento {i + 1}", "argumento", arg)
                arg_nodo.categoria = "expresion"
                arg_nodo.establecer_estilo(
                    color_texto="#9CDCFE",
                    color_fondo="#1E1E1E",
                    tamanio=9
                )
                # Parse the argument recursively
                parsed_arg = _analizar_expresion(arg)
                if parsed_arg:
                    arg_nodo.agregar_hijo(parsed_arg)
                else:
                    # If parsing failed, just add as a literal
                    lit_nodo = NodoLR("Valor", "valor", arg)
                    lit_nodo.categoria = "terminal"
                    lit_nodo.establecer_estilo(
                        color_texto="#CE9178",
                        color_fondo="#1E1E1E",
                        tamanio=9
                    )
                    arg_nodo.agregar_hijo(lit_nodo)
                nodo.agregar_hijo(arg_nodo)

        return nodo

    # Identifier reference
    nodo = NodoLR("Identificador", "identificador", expresion)
    nodo.categoria = "terminal"
    nodo.establecer_estilo(
        color_texto="#9CDCFE",  # Light blue for variables
        color_fondo="#1E1E1E",
        tamanio=10
    )
    return nodo


def _analizar_tipo_dato(tipo):
    """Creates a detailed node for a data type with appropriate styling"""
    nodo = NodoLR("Tipo de Dato", "tipo", tipo)
    nodo.categoria = "no_terminal"

    # Color based on data type
    if tipo in ["int", "float", "double", "long", "byte", "short"]:
        color = "#569CD6"  # Blue for numeric types
    elif tipo in ["boolean"]:
        color = "#569CD6"  # Blue for boolean
    elif tipo in ["char", "String"]:
        color = "#569CD6"  # Blue for text types
    else:
        color = "#4EC9B0"  # Teal for object types

    nodo.establecer_estilo(
        color_texto=color,
        color_fondo="#1E1E1E",
        color_borde=color,
        negrita=True,
        tamanio=10,
        forma="rect"
    )
    return nodo


def _analizar_sentencia_for(expresion):
    """Analyzes a for statement to create a detailed grammar tree"""
    # Extract for components: for (init; condition; update) body
    header_match = re.search(r'for\s*\((.*?);(.*?);(.*?)\)', expresion)
    if not header_match:
        return None

    init_expr = header_match.group(1).strip()
    cond_expr = header_match.group(2).strip()
    update_expr = header_match.group(3).strip()

    # Find the body based on brackets matching
    body_start = expresion.find(')', header_match.end()) + 1

    # Find the matching closing bracket for the body
    if body_start < len(expresion) and '{' in expresion[body_start:]:
        # Body with braces
        body_start = expresion.find('{', body_start)
        open_braces = 1
        body_end = body_start + 1

        while open_braces > 0 and body_end < len(expresion):
            if expresion[body_end] == '{':
                open_braces += 1
            elif expresion[body_end] == '}':
                open_braces -= 1
            body_end += 1

        body = expresion[body_start:body_end].strip()
    else:
        # Body without braces (single statement)
        body = expresion[body_start:].strip()
        if ';' in body:
            body = body.split(';')[0] + ';'

    # Create the for statement node
    for_nodo = NodoLR("Sentencia for", "for")
    for_nodo.categoria = "sentencia"
    for_nodo.establecer_estilo(
        color_texto="#C586C0",  # Purple for control flow
        color_fondo="#2D2D30",
        color_borde="#C586C0",
        negrita=True,
        tamanio=11,
        forma="diamond",
        sombra=True
    )

    # Add initialization part
    init_nodo = NodoLR("Inicialización", "for_init", init_expr)
    init_nodo.categoria = "expresion"
    init_nodo.establecer_estilo(
        color_texto="#9CDCFE",
        color_fondo="#1E1E1E",
        tamanio=10
    )

    # Parse the initialization expression
    parsed_init = _analizar_expresion(init_expr)
    if parsed_init:
        init_nodo.agregar_hijo(parsed_init)
    else:
        # Check if this is a variable declaration
        parts = init_expr.split()
        if len(parts) >= 2:
            tipo = parts[0]
            resto = init_expr[len(tipo):].strip()

            tipo_nodo = _analizar_tipo_dato(tipo)
            init_nodo.agregar_hijo(tipo_nodo)

            # Add the variable and possible initialization
            var_nodo = NodoLR("Variable", "variable", resto)
            var_nodo.categoria = "expresion"
            var_nodo.establecer_estilo(
                color_texto="#9CDCFE",
                color_fondo="#1E1E1E",
                tamanio=10
            )

            # If there's an assignment, parse it
            if '=' in resto:
                var_name, value = resto.split('=', 1)
                name_nodo = NodoLR("Nombre", "identificador", var_name.strip())
                name_nodo.categoria = "terminal"
                name_nodo.establecer_estilo(
                    color_texto="#9CDCFE",
                    color_fondo="#1E1E1E",
                    tamanio=9
                )
                var_nodo.agregar_hijo(name_nodo)

                value_nodo = NodoLR("Valor", "valor", value.strip())
                value_nodo.categoria = "expresion"
                value_nodo.establecer_estilo(
                    color_texto="#CE9178",
                    color_fondo="#1E1E1E",
                    tamanio=9
                )

                # Parse the value recursively
                parsed_value = _analizar_expresion(value.strip())
                if parsed_value:
                    value_nodo.agregar_hijo(parsed_value)

                var_nodo.agregar_hijo(value_nodo)
            else:
                # Just a variable name
                name_nodo = NodoLR("Nombre", "identificador", resto)
                name_nodo.categoria = "terminal"
                name_nodo.establecer_estilo(
                    color_texto="#9CDCFE",
                    color_fondo="#1E1E1E",
                    tamanio=9
                )
                var_nodo.agregar_hijo(name_nodo)

            init_nodo.agregar_hijo(var_nodo)

    for_nodo.agregar_hijo(init_nodo)

    # Add condition part
    cond_nodo = NodoLR("Condición", "for_condition", cond_expr)
    cond_nodo.categoria = "expresion"
    cond_nodo.establecer_estilo(
        color_texto="#D4D4D4",
        color_fondo="#1E1E1E",
        tamanio=10
    )

    # Parse the condition expression
    parsed_cond = _analizar_expresion(cond_expr)
    if parsed_cond:
        cond_nodo.agregar_hijo(parsed_cond)

    for_nodo.agregar_hijo(cond_nodo)

    # Add update part
    update_nodo = NodoLR("Actualización", "for_update", update_expr)
    update_nodo.categoria = "expresion"
    update_nodo.establecer_estilo(
        color_texto="#D4D4D4",
        color_fondo="#1E1E1E",
        tamanio=10
    )

    # Parse the update expression
    parsed_update = _analizar_expresion(update_expr)
    if parsed_update:
        update_nodo.agregar_hijo(parsed_update)

    for_nodo.agregar_hijo(update_nodo)

    # Add body part
    body_nodo = NodoLR("Bloque for", "for_body", body)
    body_nodo.categoria = "bloque"
    body_nodo.establecer_estilo(
        color_texto="#D4D4D4",
        color_fondo="#1E1E1E",
        tamanio=10,
        forma="rect",
        radio_esquinas=5
    )

    # Parse body statements
    if body.startswith('{') and body.endswith('}'):
        # Remove braces and parse statements
        inner_body = body[1:-1].strip()
        # Split into statements
        statements = _split_statements(inner_body)

        for i, stmt in enumerate(statements):
            stmt_nodo = NodoLR(f"Sentencia {i + 1}", "sentencia", stmt)
            stmt_nodo.categoria = "sentencia"
            stmt_nodo.establecer_estilo(
                color_texto="#D4D4D4",
                color_fondo="#1E1E1E",
                tamanio=9
            )

            # Parse each statement
            parsed_stmt = _analizar_sentencia(stmt)
            if parsed_stmt:
                stmt_nodo.agregar_hijo(parsed_stmt)

            body_nodo.agregar_hijo(stmt_nodo)
    else:
        # Single statement
        stmt_nodo = NodoLR("Sentencia", "sentencia", body)
        stmt_nodo.categoria = "sentencia"
        stmt_nodo.establecer_estilo(
            color_texto="#D4D4D4",
            color_fondo="#1E1E1E",
            tamanio=9
        )

        parsed_stmt = _analizar_sentencia(body)
        if parsed_stmt:
            stmt_nodo.agregar_hijo(parsed_stmt)

        body_nodo.agregar_hijo(stmt_nodo)

    for_nodo.agregar_hijo(body_nodo)

    return for_nodo


def _split_statements(code):
    """
    Splits Java code into separate statements, respecting blocks and string literals
    """
    statements = []
    current = ""
    in_string = False
    in_comment = False
    brace_level = 0

    i = 0
    while i < len(code):
        # Check for string literals
        if code[i] == '"' and not in_comment:
            in_string = not in_string
            current += code[i]
            i += 1
            continue

        # Check for comments
        if i < len(code) - 1 and code[i:i + 2] == '//' and not in_string:
            in_comment = True
            current += code[i]
            i += 1
            continue

        if in_comment and code[i] == '\n':
            in_comment = False
            current += code[i]
            i += 1
            continue

        # Handle nested blocks
        if code[i] == '{' and not in_string and not in_comment:
            brace_level += 1
            current += code[i]
            i += 1
            continue

        if code[i] == '}' and not in_string and not in_comment:
            brace_level -= 1
            current += code[i]
            i += 1
            continue

        # Found statement end
        if code[i] == ';' and brace_level == 0 and not in_string and not in_comment:
            current += code[i]
            statements.append(current.strip())
            current = ""
            i += 1
            continue

        current += code[i]
        i += 1

    # Add the last statement if any
    if current.strip():
        statements.append(current.strip())

    return statements


def _analizar_sentencia(sentencia):
    """
    Analyzes a Java statement to create a detailed grammar tree
    """
    if not sentencia or sentencia.strip() == '':
        return None

    # Remove trailing semicolon for analysis
    if sentencia.endswith(';'):
        sentencia = sentencia[:-1].strip()

    # Check for various statement types

    # For statement
    if sentencia.startswith('for '):
        return _analizar_sentencia_for(sentencia)

    # System.out.println
    if 'System.out.println' in sentencia:
        match = re.search(r'System\.out\.println\((.*)\)', sentencia)
        if match:
            arg = match.group(1).strip()

            println_nodo = NodoLR("System.out.println", "llamada", "System.out.println")
            println_nodo.categoria = "expresion"
            println_nodo.establecer_estilo(
                color_texto="#DCDCAA",
                color_fondo="#2D2D30",
                color_borde="#DCDCAA",
                negrita=True,
                tamanio=10,
                forma="rect",
                radio_esquinas=5
            )

            # Add argument
            if arg:
                arg_nodo = NodoLR("Argumento", "argumento", arg)
                arg_nodo.categoria = "expresion"
                arg_nodo.establecer_estilo(
                    color_texto="#9CDCFE",
                    color_fondo="#1E1E1E",
                    tamanio=9
                )

                # Parse the argument recursively
                parsed_arg = _analizar_expresion(arg)
                if parsed_arg:
                    arg_nodo.agregar_hijo(parsed_arg)

                println_nodo.agregar_hijo(arg_nodo)

            return println_nodo

    # Variable declaration/assignment
    parts = sentencia.split()
    if len(parts) >= 2:
        # Check if it starts with a type
        potential_type = parts[0]
        if potential_type in ["int", "float", "double", "boolean", "char", "String", "long", "short", "byte"]:
            declaration = sentencia[len(potential_type):].strip()

            decl_nodo = NodoLR("Declaración de Variable", "declaracion")
            decl_nodo.categoria = "declaracion"
            decl_nodo.establecer_estilo(
                color_texto="#DCDCAA",
                color_fondo="#2D2D30",
                color_borde="#DCDCAA",
                negrita=False,
                tamanio=10,
                forma="rect",
                radio_esquinas=4
            )

            # Add type node
            tipo_nodo = _analizar_tipo_dato(potential_type)
            decl_nodo.agregar_hijo(tipo_nodo)

            # Add variable and possible initialization
            if '=' in declaration:
                var_name, value = declaration.split('=', 1)

                var_nodo = NodoLR("Variable", "variable", var_name.strip())
                var_nodo.categoria = "identificador"
                var_nodo.establecer_estilo(
                    color_texto="#9CDCFE",
                    color_fondo="#1E1E1E",
                    tamanio=10
                )
                decl_nodo.agregar_hijo(var_nodo)

                asignacion_nodo = NodoLR("Asignación", "operador", "=")
                asignacion_nodo.categoria = "operador"
                asignacion_nodo.establecer_estilo(
                    color_texto="#D4D4D4",
                    color_fondo="#1E1E1E",
                    tamanio=10,
                    forma="ellipse"
                )

                valor_nodo = _analizar_expresion(value.strip())
                if valor_nodo:
                    asignacion_nodo.agregar_hijo(valor_nodo)
                else:
                    simple_valor = NodoLR("Valor", "valor", value.strip())
                    simple_valor.categoria = "terminal"
                    simple_valor.establecer_estilo(
                        color_texto="#CE9178",
                        color_fondo="#1E1E1E",
                        tamanio=9
                    )
                    asignacion_nodo.agregar_hijo(simple_valor)

                decl_nodo.agregar_hijo(asignacion_nodo)
            else:
                # Just a variable declaration without initialization
                var_nodo = NodoLR("Variable", "variable", declaration.strip())
                var_nodo.categoria = "identificador"
                var_nodo.establecer_estilo(
                    color_texto="#9CDCFE",
                    color_fondo="#1E1E1E",
                    tamanio=10
                )
                decl_nodo.agregar_hijo(var_nodo)

            return decl_nodo

    # Assignment
    if '=' in sentencia and not '==' in sentencia and not '<=' in sentencia and not '>=' in sentencia:
        var_name, value = sentencia.split('=', 1)

        asignacion_nodo = NodoLR("Asignación", "asignacion")
        asignacion_nodo.categoria = "expresion"
        asignacion_nodo.establecer_estilo(
            color_texto="#D4D4D4",
            color_fondo="#2D2D30",
            color_borde="#D4D4D4",
            negrita=False,
            tamanio=10,
            forma="rect"
        )

        # Add identifier
        id_nodo = NodoLR("Identificador", "identificador", var_name.strip())
        id_nodo.categoria = "terminal"
        id_nodo.establecer_estilo(
            color_texto="#9CDCFE",
            color_fondo="#1E1E1E",
            tamanio=10
        )
        asignacion_nodo.agregar_hijo(id_nodo)

        # Add operator
        op_nodo = NodoLR("Operador", "operador", "=")
        op_nodo.categoria = "operador"
        op_nodo.establecer_estilo(
            color_texto="#D4D4D4",
            color_fondo="#1E1E1E",
            tamanio=10,
            forma="ellipse"
        )
        asignacion_nodo.agregar_hijo(op_nodo)

        # Add value
        valor_nodo = _analizar_expresion(value.strip())
        if valor_nodo:
            asignacion_nodo.agregar_hijo(valor_nodo)
        else:
            simple_valor = NodoLR("Valor", "valor", value.strip())
            simple_valor.categoria = "terminal"
            simple_valor.establecer_estilo(
                color_texto="#CE9178",
                color_fondo="#1E1E1E",
                tamanio=9
            )
            asignacion_nodo.agregar_hijo(simple_valor)

        return asignacion_nodo

    # Method call
    if '(' in sentencia and ')' in sentencia:
        return _analizar_expresion(sentencia)

    # Default case: expression statement
    return _analizar_expresion(sentencia)


def _analizar_metodo(codigo_metodo):
    """
    Analyzes a method declaration to create a detailed grammar tree
    """
    if not codigo_metodo:
        return None

    # Extract method components: modifiers, return type, name, parameters, body
    method_nodo = NodoLR("Declaración de Método", "metodo")
    method_nodo.categoria = "metodo"
    method_nodo.establecer_estilo(
        color_texto="#4EC9B0",
        color_fondo="#2D2D30",
        color_borde="#4EC9B0",
        negrita=True,
        tamanio=12,
        forma="rect",
        gradiente=True,
        radio_esquinas=6
    )

    # Find opening brace of method body
    open_brace = codigo_metodo.find('{')
    if open_brace == -1:
        return None

    # Extract header
    header = codigo_metodo[:open_brace].strip()

    # Find closing parenthesis of parameters
    close_paren = header.rfind(')')
    if close_paren == -1:
        return None

    # Extract parameters part
    params_start = header.rfind('(', 0, close_paren)
    if params_start == -1:
        return None

    params_text = header[params_start + 1:close_paren].strip()

    # Extract method name and everything before it
    before_params = header[:params_start].strip()
    parts = before_params.split()

    # The last part is the method name
    method_name = parts[-1]

    # Everything before the name might be modifiers and return type
    modifiers_and_type = parts[:-1]

    # Add modifiers
    modifiers = []
    return_type = None

    for part in modifiers_and_type:
        if part in ["public", "private", "protected", "static", "final", "abstract", "synchronized"]:
            modifiers.append(part)
        else:
            return_type = part

    if modifiers:
        mod_nodo = NodoLR("Modificadores", "modificador", " ".join(modifiers))
        mod_nodo.categoria = "no_terminal"
        mod_nodo.establecer_estilo(
            color_texto="#569CD6",
            color_fondo="#1E1E1E",
            tamanio=10
        )

        for mod in modifiers:
            mod_item = NodoLR(mod, "modificador", mod)
            mod_item.categoria = "terminal"
            mod_item.establecer_estilo(
                color_texto="#569CD6",
                color_fondo="#1E1E1E",
                tamanio=9
            )
            mod_nodo.agregar_hijo(mod_item)

        method_nodo.agregar_hijo(mod_nodo)

    # Add return type
    if return_type:
        tipo_nodo = _analizar_tipo_dato(return_type)
        tipo_nodo.etiqueta = "Tipo de Retorno"
        method_nodo.agregar_hijo(tipo_nodo)

    # Add method name
    name_nodo = NodoLR("Nombre del Método", "identificador", method_name)
    name_nodo.categoria = "terminal"
    name_nodo.establecer_estilo(
        color_texto="#DCDCAA",
        color_fondo="#1E1E1E",
        negrita=True,
        tamanio=10
    )
    method_nodo.agregar_hijo(name_nodo)

    # Add parameters
    param_nodo = NodoLR("Parámetros", "parametros", params_text)
    param_nodo.categoria = "no_terminal"
    param_nodo.establecer_estilo(
        color_texto="#9CDCFE",
        color_fondo="#1E1E1E",
        tamanio=10,
        forma="rect",
        radio_esquinas=4
    )

    if params_text:
        # Split parameters respecting complex types
        params = []
        current_param = ""
        bracket_level = 0

        for c in params_text:
            if c == '[':
                bracket_level += 1
            elif c == ']':
                bracket_level -= 1
            elif c == ',' and bracket_level == 0:
                params.append(current_param.strip())
                current_param = ""
                continue
            current_param += c

        if current_param:
            params.append(current_param.strip())

        for i, p in enumerate(params):
            p_parts = p.split()
            if len(p_parts) >= 2:
                p_type = p_parts[0]
                p_name = " ".join(p_parts[1:])

                p_nodo = NodoLR(f"Parámetro {i + 1}", "parametro", p)
                p_nodo.categoria = "no_terminal"
                p_nodo.establecer_estilo(
                    color_texto="#9CDCFE",
                    color_fondo="#1E1E1E",
                    tamanio=9
                )

                p_type_nodo = _analizar_tipo_dato(p_type)
                p_nodo.agregar_hijo(p_type_nodo)

                p_name_nodo = NodoLR("Nombre", "identificador", p_name)
                p_name_nodo.categoria = "terminal"
                p_name_nodo.establecer_estilo(
                    color_texto="#9CDCFE",
                    color_fondo="#1E1E1E",
                    tamanio=9
                )
                p_nodo.agregar_hijo(p_name_nodo)

                param_nodo.agregar_hijo(p_nodo)

    method_nodo.agregar_hijo(param_nodo)

    # Add method body
    open_braces = 1
    body_end = open_brace + 1

    while open_braces > 0 and body_end < len(codigo_metodo):
        if codigo_metodo[body_end] == '{':
            open_braces += 1
        elif codigo_metodo[body_end] == '}':
            open_braces -= 1
        body_end += 1

    body = codigo_metodo[open_brace:body_end].strip()

    body_nodo = NodoLR("Bloque de Método", "bloque", body)
    body_nodo.categoria = "bloque"
    body_nodo.establecer_estilo(
        color_texto="#D4D4D4",
        color_fondo="#2D2D30",
        color_borde="#6D6D6D",
        negrita=False,
        tamanio=10,
        forma="rect",
        radio_esquinas=5
    )

    # Parse statements in the body
    if body.startswith('{') and body.endswith('}'):
        # Remove braces and parse statements
        inner_body = body[1:-1].strip()

        if inner_body:
            # Split into statements
            statements = _split_statements(inner_body)

            for i, stmt in enumerate(statements):
                stmt_nodo = NodoLR(f"Sentencia {i + 1}", "sentencia", stmt)
                stmt_nodo.categoria = "sentencia"
                stmt_nodo.establecer_estilo(
                    color_texto="#D4D4D4",
                    color_fondo="#1E1E1E",
                    tamanio=9
                )

                # Parse each statement
                parsed_stmt = _analizar_sentencia(stmt)
                if parsed_stmt:
                    stmt_nodo.agregar_hijo(parsed_stmt)

                body_nodo.agregar_hijo(stmt_nodo)

    method_nodo.agregar_hijo(body_nodo)

    return method_nodo


def _analizar_clase(codigo_clase):
    """
    Analyzes a class declaration to create a detailed grammar tree
    """
    if not codigo_clase:
        return None

    # Find class keyword
    class_idx = codigo_clase.find("class ")
    if class_idx == -1:
        return None

    # Extract parts before and after class keyword
    before_class = codigo_clase[:class_idx].strip()
    after_class = codigo_clase[class_idx + 5:].strip()

    # Find class name (everything before first space or opening brace)
    name_end = min(after_class.find(' ') if after_class.find(' ') != -1 else len(after_class),
                   after_class.find('{') if after_class.find('{') != -1 else len(after_class))

    class_name = after_class[:name_end].strip()

    # Create the class node
    class_nodo = NodoLR("Declaración de Clase", "clase", class_name)
    class_nodo.categoria = "clase"
    class_nodo.establecer_estilo(
        color_texto="#569CD6",
        color_fondo="#2D2D30",
        color_borde="#569CD6",
        negrita=True,
        tamanio=13,
        forma="rect",
        gradiente=True,
        radio_esquinas=8
    )

    # Add modifiers
    if before_class:
        modifiers = before_class.split()
        mod_nodo = NodoLR("Modificador", "modificador", before_class)
        mod_nodo.categoria = "no_terminal"
        mod_nodo.establecer_estilo(
            color_texto="#569CD6",
            color_fondo="#1E1E1E",
            tamanio=10
        )

        for mod in modifiers:
            mod_item = NodoLR(mod, "modificador", mod)
            mod_item.categoria = "terminal"
            mod_item.establecer_estilo(
                color_texto="#569CD6",
                color_fondo="#1E1E1E",
                tamanio=9
            )
            mod_nodo.agregar_hijo(mod_item)

        class_nodo.agregar_hijo(mod_nodo)

    # Add class keyword
    class_keyword = NodoLR("class", "keyword", "class")
    class_keyword.categoria = "terminal"
    class_keyword.establecer_estilo(
        color_texto="#569CD6",
        color_fondo="#1E1E1E",
        negrita=True,
        tamanio=10
    )
    class_nodo.agregar_hijo(class_keyword)

    # Add class name
    name_nodo = NodoLR("Identificador", "identificador", class_name)
    name_nodo.categoria = "terminal"
    name_nodo.establecer_estilo(
        color_texto="#4EC9B0",
        color_fondo="#1E1E1E",
        negrita=True,
        tamanio=10
    )
    class_nodo.agregar_hijo(name_nodo)

    # Find class body
    body_start = after_class.find('{')
    if body_start == -1:
        return class_nodo

    # Extract class body with matching braces
    open_braces = 1
    body_end = body_start + 1

    while open_braces > 0 and body_end < len(after_class):
        if after_class[body_end] == '{':
            open_braces += 1
        elif after_class[body_end] == '}':
            open_braces -= 1
        body_end += 1

    body = after_class[body_start:body_end].strip()

    # Add class body
    body_nodo = NodoLR("Bloque de Clase", "bloque", body)
    body_nodo.categoria = "bloque"
    body_nodo.establecer_estilo(
        color_texto="#D4D4D4",
        color_fondo="#2D2D30",
        color_borde="#6D6D6D",
        negrita=False,
        tamanio=10,
        forma="rect",
        radio_esquinas=5
    )

    # Parse class elements (methods, fields, etc.)
    if body.startswith('{') and body.endswith('}'):
        inner_body = body[1:-1].strip()

        if inner_body:
            # Extract class members (methods, fields)
            members = _extract_class_members(inner_body)

            for member in members:
                member_text = member.strip()

                # Identify member type
                if '(' in member_text and ')' in member_text and '{' in member_text and '}' in member_text:
                    # This is likely a method
                    method_nodo = _analizar_metodo(member_text)
                    if method_nodo:
                        body_nodo.agregar_hijo(method_nodo)
                elif ';' in member_text:
                    # This is likely a field declaration
                    field_nodo = NodoLR("Atributo", "atributo", member_text.rstrip(';'))
                    field_nodo.categoria = "declaracion"
                    field_nodo.establecer_estilo(
                        color_texto="#9CDCFE",
                        color_fondo="#1E1E1E",
                        tamanio=10,
                        forma="ellipse"
                    )

                    # Parse field declaration
                    parts = member_text.rstrip(';').split()

                    modifiers = []
                    field_type = None
                    field_decl = None

                    for i, part in enumerate(parts):
                        if part in ["public", "private", "protected", "static", "final"]:
                            modifiers.append(part)
                        elif not field_type and part not in modifiers:
                            field_type = part
                            field_decl = " ".join(parts[i + 1:])
                            break

                    if modifiers:
                        mod_nodo = NodoLR("Modificadores", "modificador", " ".join(modifiers))
                        mod_nodo.categoria = "no_terminal"
                        mod_nodo.establecer_estilo(
                            color_texto="#569CD6",
                            color_fondo="#1E1E1E",
                            tamanio=9
                        )

                        for mod in modifiers:
                            mod_item = NodoLR(mod, "modificador", mod)
                            mod_item.categoria = "terminal"
                            mod_item.establecer_estilo(
                                color_texto="#569CD6",
                                color_fondo="#1E1E1E",
                                tamanio=8
                            )
                            mod_nodo.agregar_hijo(mod_item)

                        field_nodo.agregar_hijo(mod_nodo)

                    if field_type:
                        tipo_nodo = _analizar_tipo_dato(field_type)
                        field_nodo.agregar_hijo(tipo_nodo)

                    if field_decl:
                        decl_nodo = NodoLR("Declaración", "declaracion", field_decl)
                        decl_nodo.categoria = "expresion"
                        decl_nodo.establecer_estilo(
                            color_texto="#9CDCFE",
                            color_fondo="#1E1E1E",
                            tamanio=9
                        )

                        # If there's an assignment, parse it
                        if '=' in field_decl:
                            var_name, value = field_decl.split('=', 1)

                            name_nodo = NodoLR("Nombre", "identificador", var_name.strip())
                            name_nodo.categoria = "terminal"
                            name_nodo.establecer_estilo(
                                color_texto="#9CDCFE",
                                color_fondo="#1E1E1E",
                                tamanio=8
                            )
                            decl_nodo.agregar_hijo(name_nodo)

                            value_nodo = NodoLR("Valor", "valor", value.strip())
                            value_nodo.categoria = "expresion"
                            value_nodo.establecer_estilo(
                                color_texto="#CE9178",
                                color_fondo="#1E1E1E",
                                tamanio=8
                            )

                            # Parse the value
                            parsed_value = _analizar_expresion(value.strip())
                            if parsed_value:
                                value_nodo.agregar_hijo(parsed_value)

                            decl_nodo.agregar_hijo(value_nodo)
                        else:
                            # Just a variable name
                            name_nodo = NodoLR("Nombre", "identificador", field_decl)
                            name_nodo.categoria = "terminal"
                            name_nodo.establecer_estilo(
                                color_texto="#9CDCFE",
                                color_fondo="#1E1E1E",
                                tamanio=8
                            )
                            decl_nodo.agregar_hijo(name_nodo)

                        field_nodo.agregar_hijo(decl_nodo)

                    body_nodo.agregar_hijo(field_nodo)

    class_nodo.agregar_hijo(body_nodo)

    return class_nodo


def _extract_class_members(class_body):
    """
    Extracts class members (methods, fields) from the class body
    """
    members = []
    current = ""
    brace_level = 0
    in_string = False
    in_comment = False

    i = 0
    while i < len(class_body):
        # Check for string literals
        if class_body[i] == '"' and not in_comment:
            in_string = not in_string
            current += class_body[i]
            i += 1
            continue

        # Check for comments
        if i < len(class_body) - 1 and class_body[i:i + 2] == '//' and not in_string:
            in_comment = True
            current += class_body[i]
            i += 1
            continue

        if in_comment and class_body[i] == '\n':
            in_comment = False
            current += class_body[i]
            i += 1
            continue

        # Handle nested blocks
        if class_body[i] == '{' and not in_string and not in_comment:
            brace_level += 1
            current += class_body[i]
            i += 1
            continue

        if class_body[i] == '}' and not in_string and not in_comment:
            brace_level -= 1
            current += class_body[i]

            # End of method body
            if brace_level == 0:
                members.append(current.strip())
                current = ""

            i += 1
            continue

        # End of field declaration
        if class_body[i] == ';' and brace_level == 0 and not in_string and not in_comment:
            current += class_body[i]
            members.append(current.strip())
            current = ""
            i += 1
            continue

        current += class_body[i]
        i += 1

    # Add the last member if any
    if current.strip():
        members.append(current.strip())

    return members


def _analizar_programa(codigo_fuente):
    """
    Analyzes a complete Java program to create a detailed grammar tree
    """
    if not codigo_fuente or codigo_fuente.strip() == '':
        return None

    # Create the root node for the program
    programa_nodo = NodoLR("Programa", "programa")
    programa_nodo.categoria = "programa"
    programa_nodo.establecer_estilo(
        color_texto="#F89406",  # Orange
        color_fondo="#2D2D30",
        color_borde="#F89406",
        negrita=True,
        tamanio=14,
        forma="rect",
        gradiente=True,
        sombra=True,
        radio_esquinas=10
    )

    # Find class declarations
    class_keyword_positions = []
    i = 0
    while i < len(codigo_fuente):
        i = codigo_fuente.find("class ", i)
        if i == -1:
            break

        # Make sure it's actually a class keyword, not part of a word
        if i == 0 or codigo_fuente[i - 1].isspace() or codigo_fuente[i - 1] in "{}();":
            class_keyword_positions.append(i)
        i += 6  # Length of "class "

    # No classes found
    if not class_keyword_positions:
        return programa_nodo

    # Process each class
    for i, pos in enumerate(class_keyword_positions):
        # Determine where this class ends
        next_pos = class_keyword_positions[i + 1] if i + 1 < len(class_keyword_positions) else len(codigo_fuente)

        # Extract this class's code
        # Need to find the beginning of the class declaration
        start = pos
        while start > 0 and not codigo_fuente[start - 1] in "{};\n":
            start -= 1

        class_code = codigo_fuente[start:next_pos].strip()

        # Parse the class
        class_nodo = _analizar_clase(class_code)
        if class_nodo:
            programa_nodo.agregar_hijo(class_nodo)

    return programa_nodo


def construir_arbol_lr_desde_codigo(codigo_fuente):
    """
    Builds a detailed LR tree from source code with full grammar analysis
    Returns the root of the tree and a boolean indicating success
    """
    from analizador_sintactico import prueba_sintactica
    from analizador_lexico import tabla_simbolos
    from arbol_derivacion import construir_arbol_derivacion

    try:
        # First perform syntactic analysis
        resultado = prueba_sintactica(codigo_fuente)

        # Check for errors
        tiene_errores = any("Error" in item for item in resultado)
        if tiene_errores:
            return None, False

        # Build the grammar tree directly
        arbol_lr = _analizar_programa(codigo_fuente)

        if arbol_lr is None:
            return None, False

        return arbol_lr, True

    except Exception as e:
        print(f"Error al construir árbol LR: {str(e)}")
        return None, False


def mostrar_arbol_lr(codigo_fuente, parent=None):
    """
    Main function to display the LR tree in a separate window with improved grammar visualization

    Args:
        codigo_fuente: Java source code to analyze
        parent: Parent widget for the window

    Returns:
        bool: True if the tree was displayed correctly, False otherwise
    """
    # Build the LR tree with detailed grammar analysis
    arbol_lr, exito = construir_arbol_lr_desde_codigo(codigo_fuente)

    if not exito or arbol_lr is None:
        return False

    # Create and show the window
    ventana = VentanaArbolLR(parent)
    ventana.establecer_arbol(arbol_lr)
    ventana.exec_()

    return True