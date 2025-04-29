# -*- coding: utf-8 -*-

# arbol_visual.py - versión mejorada
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from PyQt5.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTabWidget, QGraphicsView, QGraphicsScene,
    QGraphicsEllipseItem, QGraphicsTextItem, QGraphicsLineItem, QMessageBox, QWidget
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QBrush, QPen, QFont, QPainter


# Clase que representa un nodo del árbol
class NodoBinario:
    def __init__(self, tipo, valor=None, linea=None):
        self.tipo = tipo
        self.valor = valor
        self.linea = linea
        self.hijos = []
        self.izquierdo = None  # Para compatibilidad con la visualización binaria
        self.derecho = None  # Para compatibilidad con la visualización binaria
        self.x = 0
        self.y = 0
        self.orden_preorden = 0
        self.orden_inorden = 0
        self.orden_postorden = 0
        self.recorrido_preorden = []
        self.recorrido_inorden = []
        self.recorrido_postorden = []

    def agregar_hijo(self, nodo):
        """Agrega un hijo al nodo actual"""
        self.hijos.append(nodo)
        # Actualizar izquierdo/derecho para visualización binaria
        if len(self.hijos) == 1:
            self.izquierdo = nodo
        elif len(self.hijos) == 2:
            self.derecho = nodo
        return nodo


# Clase para representar el árbol
class ArbolBinario:
    def __init__(self):
        self.raiz = None
        self.contador_preorden = 1
        self.contador_inorden = 1
        self.contador_postorden = 1

    def crear_arbol_ejemplo(self):
        # Crear un árbol de ejemplo
        self.raiz = NodoBinario("programa", "Programa")
        self.raiz.agregar_hijo(NodoBinario("declaraciones", "Declaraciones"))
        self.raiz.agregar_hijo(NodoBinario("instrucciones", "Instrucciones"))

        # Añadir algunos nodos hijos
        self.raiz.hijos[0].agregar_hijo(NodoBinario("class", "Class"))
        self.raiz.hijos[0].agregar_hijo(NodoBinario("variables", "Variables"))
        self.raiz.hijos[1].agregar_hijo(NodoBinario("if", "If"))
        self.raiz.hijos[1].agregar_hijo(NodoBinario("for", "For"))

        # Calcular los recorridos
        self._calcular_recorridos()
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

            # Convertir el árbol de recorridos_arbol a la estructura de ArbolBinario
            self.raiz = self._convertir_nodo(arbol)

            # Calcular recorridos
            self._calcular_recorridos()
            self.calcular_orden_recorridos()

            return True
        except Exception as e:
            print(f"Error al construir árbol: {str(e)}")
            return False

    def _convertir_nodo(self, nodo_original):
        """
        Convierte un NodoRecorrido de recorridos_arbol a un NodoBinario de arbol_visual
        """
        # Crear nuevo nodo con el mismo tipo y valor
        nuevo_nodo = NodoBinario(nodo_original.tipo, nodo_original.valor, nodo_original.linea)

        # Convertir recursivamente los hijos
        for hijo_original in nodo_original.hijos:
            nuevo_hijo = self._convertir_nodo(hijo_original)
            nuevo_nodo.agregar_hijo(nuevo_hijo)

        return nuevo_nodo

    def _construir_arbol_recorridos(self, codigo_fuente):
        """
        Construye un árbol y sus recorridos a partir del análisis del código
        """
        from analizador_sintactico import prueba_sintactica
        from analizador_lexico import tabla_simbolos, prueba

        # Limpiar tabla de símbolos antes de análisis
        tabla_simbolos.limpiar()

        # Realizar análisis léxico primero
        tokens = prueba(codigo_fuente)

        # Realizar análisis sintáctico
        resultados = prueba_sintactica(codigo_fuente)

        # Verificar si hay errores en el análisis sintáctico
        errores = [r for r in resultados if "Error" in r]
        if errores:
            return None, errores

        # Construir el árbol a partir de los tokens
        return self._construir_arbol_desde_tokens(tokens), resultados

    def _construir_arbol_desde_tokens(self, tokens):
        """
        Construye un árbol estructurado a partir de los tokens
        """
        raiz = NodoBinario("programa", "Código Java")

        # Agrupamos tokens por estructuras lógicas
        estructuras = self._agrupar_tokens_por_estructura(tokens)

        # Construir el árbol con los grupos de tokens
        for tipo, grupo in estructuras.items():
            if grupo:  # Solo crear nodos para grupos no vacíos
                nodo_estructura = NodoBinario(tipo, f"{tipo.capitalize()}")
                raiz.agregar_hijo(nodo_estructura)

                for token in grupo:
                    # Solo incluimos tokens significativos
                    if token.get("tipo") not in ["LLAIZQ", "LLADER", "PUNTOCOMA"]:
                        valor = str(token.get("valor", ""))
                        tipo = token.get("tipo", "")
                        linea = token.get("linea", 0)

                        nodo_token = NodoBinario(tipo.lower(), valor, linea)
                        nodo_estructura.agregar_hijo(nodo_token)

        return raiz

    def _agrupar_tokens_por_estructura(self, tokens):
        """
        Agrupa los tokens en estructuras lógicas del programa
        """
        estructuras = {
            "declaraciones": [],
            "condicionales": [],
            "bucles": [],
            "asignaciones": [],
            "llamadas": [],
            "otros": []
        }

        i = 0
        while i < len(tokens):
            token = tokens[i]
            tipo = token.get("tipo", "")

            # Identificar declaraciones de variables
            if tipo in ["INT", "FLOAT", "DOUBLE", "BOOLEAN", "CHAR", "STRING"]:
                # Capturar toda la declaración hasta el punto y coma
                declaracion = [token]
                j = i + 1
                while j < len(tokens) and tokens[j].get("tipo") != "PUNTOCOMA":
                    declaracion.append(tokens[j])
                    j += 1
                if j < len(tokens):
                    declaracion.append(tokens[j])  # Incluir el punto y coma

                estructuras["declaraciones"].extend(declaracion)
                i = j + 1
                continue

            # Identificar condicionales (if, else, switch)
            elif tipo in ["IF", "ELSE", "SWITCH", "CASE"]:
                # Capturar la estructura condicional
                condicional = [token]
                j = i + 1
                llaves_abiertas = 0

                # Si hay un paréntesis abierto, capturar la condición
                if j < len(tokens) and tokens[j].get("tipo") == "PARIZQ":
                    llaves_abiertas += 1
                    condicional.append(tokens[j])
                    j += 1

                    while j < len(tokens) and llaves_abiertas > 0:
                        if tokens[j].get("tipo") == "PARIZQ":
                            llaves_abiertas += 1
                        elif tokens[j].get("tipo") == "PARDER":
                            llaves_abiertas -= 1
                        condicional.append(tokens[j])
                        j += 1

                estructuras["condicionales"].extend(condicional)
                i = j
                continue

            # Identificar bucles (for, while, do)
            elif tipo in ["FOR", "WHILE", "DO"]:
                bucle = [token]
                j = i + 1
                llaves_abiertas = 0

                # Si hay un paréntesis abierto, capturar la condición del bucle
                if j < len(tokens) and tokens[j].get("tipo") == "PARIZQ":
                    llaves_abiertas += 1
                    bucle.append(tokens[j])
                    j += 1

                    while j < len(tokens) and llaves_abiertas > 0:
                        if tokens[j].get("tipo") == "PARIZQ":
                            llaves_abiertas += 1
                        elif tokens[j].get("tipo") == "PARDER":
                            llaves_abiertas -= 1
                        bucle.append(tokens[j])
                        j += 1

                estructuras["bucles"].extend(bucle)
                i = j
                continue

            # Identificar asignaciones (=)
            elif tipo == "IDENTIFICADOR" and i + 1 < len(tokens) and tokens[i + 1].get("tipo") == "ASIGNAR":
                asignacion = [token, tokens[i + 1]]  # Identificador y =
                j = i + 2

                # Capturar el valor hasta el punto y coma
                while j < len(tokens) and tokens[j].get("tipo") != "PUNTOCOMA":
                    asignacion.append(tokens[j])
                    j += 1
                if j < len(tokens):
                    asignacion.append(tokens[j])  # Incluir el punto y coma

                estructuras["asignaciones"].extend(asignacion)
                i = j + 1
                continue

            # Identificar llamadas a funciones
            elif tipo == "IDENTIFICADOR" and i + 1 < len(tokens) and tokens[i + 1].get("tipo") == "PARIZQ":
                llamada = [token, tokens[i + 1]]  # Nombre de función y (
                j = i + 2
                llaves_abiertas = 1

                # Capturar los argumentos
                while j < len(tokens) and llaves_abiertas > 0:
                    if tokens[j].get("tipo") == "PARIZQ":
                        llaves_abiertas += 1
                    elif tokens[j].get("tipo") == "PARDER":
                        llaves_abiertas -= 1
                    llamada.append(tokens[j])
                    j += 1

                # Capturar hasta el punto y coma
                while j < len(tokens) and tokens[j].get("tipo") != "PUNTOCOMA":
                    llamada.append(tokens[j])
                    j += 1
                if j < len(tokens):
                    llamada.append(tokens[j])  # Incluir el punto y coma

                estructuras["llamadas"].extend(llamada)
                i = j + 1
                continue

            # Otros tokens
            else:
                estructuras["otros"].append(token)
                i += 1

        return estructuras

    def _calcular_recorridos(self):
        """Calcula los recorridos del árbol"""
        if not self.raiz:
            return

        # Pre-orden: Raíz, Izquierda, Derecha
        def preorden(nodo):
            if not nodo:
                return []

            resultado = [(nodo.tipo, nodo.valor)]
            for hijo in nodo.hijos:
                resultado.extend(preorden(hijo))
            return resultado

        # In-orden: Izquierda, Raíz, Derecha (adaptado para árbol n-ario)
        def inorden(nodo):
            if not nodo:
                return []

            resultado = []
            if nodo.hijos:
                # Mitad izquierda
                mitad = len(nodo.hijos) // 2
                for i in range(mitad):
                    resultado.extend(inorden(nodo.hijos[i]))

                # Raíz
                resultado.append((nodo.tipo, nodo.valor))

                # Mitad derecha
                for i in range(mitad, len(nodo.hijos)):
                    resultado.extend(inorden(nodo.hijos[i]))
            else:
                resultado.append((nodo.tipo, nodo.valor))

            return resultado

        # Post-orden: Izquierda, Derecha, Raíz
        def postorden(nodo):
            if not nodo:
                return []

            resultado = []
            for hijo in nodo.hijos:
                resultado.extend(postorden(hijo))
            resultado.append((nodo.tipo, nodo.valor))
            return resultado

        # Calcular y almacenar los recorridos
        self.raiz.recorrido_preorden = preorden(self.raiz)
        self.raiz.recorrido_inorden = inorden(self.raiz)
        self.raiz.recorrido_postorden = postorden(self.raiz)

    def calcular_orden_recorridos(self):
        """Numera los nodos en los diferentes recorridos"""
        if not self.raiz:
            return

        # Resetear contadores
        self.contador_preorden = 1
        self.contador_inorden = 1
        self.contador_postorden = 1

        self._calcular_orden_recorridos_recursivo(self.raiz)

    def _calcular_orden_recorridos_recursivo(self, nodo):
        if nodo is None:
            return

        # Pre-orden: Raíz -> Izquierda -> Derecha
        nodo.orden_preorden = self.contador_preorden
        self.contador_preorden += 1

        # Recorrer subárboles de izquierda a derecha (para la mitad izquierda)
        mitad = len(nodo.hijos) // 2
        for i in range(mitad):
            self._calcular_orden_recorridos_recursivo(nodo.hijos[i])

        # In-orden: Izquierda -> Raíz -> Derecha
        nodo.orden_inorden = self.contador_inorden
        self.contador_inorden += 1

        # Recorrer subárboles restantes (mitad derecha)
        for i in range(mitad, len(nodo.hijos)):
            self._calcular_orden_recorridos_recursivo(nodo.hijos[i])

        # Post-orden: Izquierda -> Derecha -> Raíz
        nodo.orden_postorden = self.contador_postorden
        self.contador_postorden += 1


# Clase para dibujar el árbol en la escena
class VistaArbol(QGraphicsScene):
    def __init__(self, parent=None):
        super(VistaArbol, self).__init__(parent)
        self.setBackgroundBrush(QBrush(QColor("#1E1E1E")))
        self.modo_recorrido = "preorden"
        self.colores_tipos = {
            "programa": "#F89406",  # Naranja
            "declaraciones": "#9CDCFE",  # Azul claro
            "instrucciones": "#DCDCAA",  # Amarillo
            "condicionales": "#C586C0",  # Morado
            "bucles": "#D7BA7D",  # Amarillo ocre
            "asignaciones": "#DCDCAA",  # Amarillo
            "llamadas": "#57A64A",  # Verde
            "identificador": "#9CDCFE",  # Azul claro
            "class": "#4EC9B0",  # Verde agua
            "variables": "#9CDCFE",  # Azul claro
            "if": "#C586C0",  # Morado
            "for": "#D7BA7D",  # Amarillo ocre
            "int": "#569CD6",  # Azul
            "float": "#569CD6",  # Azul
            "double": "#569CD6",  # Azul
            "boolean": "#569CD6",  # Azul
            "char": "#569CD6",  # Azul
            "string": "#569CD6",  # Azul
            "entero": "#B5CEA8",  # Verde claro
            "decimal": "#B5CEA8",  # Verde claro
            "cadena": "#CE9178",  # Rojo claro
            "otros": "#808080",  # Gris
        }

    def dibujar_arbol(self, arbol, tipo_recorrido):
        self.clear()
        self.modo_recorrido = tipo_recorrido

        if not arbol.raiz:
            return

        # Dibujar título
        titulo = "Recorrido "
        if tipo_recorrido == "preorden":
            titulo += "Pre-orden (Raíz → Izquierda → Derecha)"
            color_titulo = QColor("#569CD6")  # Azul
        elif tipo_recorrido == "inorden":
            titulo += "In-orden (Izquierda → Raíz → Derecha)"
            color_titulo = QColor("#4EC9B0")  # Verde
        else:  # postorden
            titulo += "Post-orden (Izquierda → Derecha → Raíz)"
            color_titulo = QColor("#C586C0")  # Morado

        texto_titulo = QGraphicsTextItem(titulo)
        texto_titulo.setFont(QFont("Arial", 18, QFont.Bold))
        texto_titulo.setDefaultTextColor(color_titulo)
        texto_titulo.setPos(50, 20)
        self.addItem(texto_titulo)

        # Calcular posiciones de los nodos - adaptamos para manejar múltiples hijos
        self._calcular_posiciones(arbol.raiz, 0, 0, 1000)

        # Dibujar las líneas y conexiones
        self._dibujar_conexiones(arbol.raiz)

        # Dibujar los nodos
        self._dibujar_nodos(arbol.raiz)

        # Opcional: Dibujar leyenda
        self._dibujar_leyenda()

    def _calcular_posiciones(self, nodo, nivel, min_x, max_x):
        """Calcula las posiciones X,Y para cada nodo en el árbol"""
        if nodo is None:
            return

        # Número total de nodos en este nivel
        num_hijos = len(nodo.hijos)

        # Posición Y basada en el nivel
        nodo.y = 100 + nivel * 100

        # Posición X centrada entre mínimo y máximo
        nodo.x = (min_x + max_x) / 2

        if num_hijos > 0:
            # Ancho de la sección para cada hijo
            ancho_seccion = (max_x - min_x) / num_hijos

            # Calcular posiciones para cada hijo
            for i, hijo in enumerate(nodo.hijos):
                x_min_hijo = min_x + i * ancho_seccion
                x_max_hijo = min_x + (i + 1) * ancho_seccion
                self._calcular_posiciones(hijo, nivel + 1, x_min_hijo, x_max_hijo)

    def _dibujar_conexiones(self, nodo):
        """Dibuja las líneas que conectan los nodos"""
        if nodo is None or not nodo.hijos:
            return

        # Tamaño del nodo
        radio = 40

        # Dibujar líneas a todos los hijos
        for hijo in nodo.hijos:
            linea = QGraphicsLineItem(nodo.x, nodo.y + radio - 5,
                                      hijo.x, hijo.y - radio + 5)
            linea.setPen(QPen(QColor("#AAAAAA"), 2))
            self.addItem(linea)

            # Dibujar conexiones recursivamente
            self._dibujar_conexiones(hijo)

    def _dibujar_nodos(self, nodo):
        """Dibuja los nodos del árbol con su orden de recorrido"""
        if nodo is None:
            return

        # Tamaño del nodo
        radio = 40

        # Crear círculo para el nodo
        circulo = QGraphicsEllipseItem(nodo.x - radio, nodo.y - radio, radio * 2, radio * 2)

        # Color según tipo de nodo
        color = self.colores_tipos.get(nodo.tipo.lower(), "#808080")
        circulo.setBrush(QBrush(QColor(color)))
        circulo.setPen(QPen(QColor("#FFFFFF"), 2))
        self.addItem(circulo)

        # Texto del nodo
        texto_valor = nodo.valor if nodo.valor else nodo.tipo
        texto = QGraphicsTextItem(texto_valor)
        texto.setFont(QFont("Arial", 10, QFont.Bold))
        texto.setDefaultTextColor(QColor("#FFFFFF"))

        # Centrar texto
        texto_x = nodo.x - texto.boundingRect().width() / 2
        texto_y = nodo.y - texto.boundingRect().height() / 2
        texto.setPos(texto_x, texto_y)
        self.addItem(texto)

        # Número de orden según el tipo de recorrido
        orden = 0
        if self.modo_recorrido == "preorden":
            orden = nodo.orden_preorden
        elif self.modo_recorrido == "inorden":
            orden = nodo.orden_inorden
        else:  # postorden
            orden = nodo.orden_postorden

        # Crear círculo para el orden
        circulo_orden = QGraphicsEllipseItem(nodo.x + radio - 10, nodo.y - radio - 20, 20, 20)

        # Color del círculo según tipo de recorrido
        if self.modo_recorrido == "preorden":
            circulo_orden.setBrush(QBrush(QColor("#569CD6")))  # Azul
        elif self.modo_recorrido == "inorden":
            circulo_orden.setBrush(QBrush(QColor("#4EC9B0")))  # Verde
        else:  # postorden
            circulo_orden.setBrush(QBrush(QColor("#C586C0")))  # Morado

        circulo_orden.setPen(QPen(QColor("#FFFFFF"), 1))
        self.addItem(circulo_orden)

        # Texto del orden
        texto_orden = QGraphicsTextItem(str(orden))
        texto_orden.setFont(QFont("Arial", 10, QFont.Bold))
        texto_orden.setDefaultTextColor(QColor("#FFFFFF"))

        # Centrar texto del orden
        texto_orden_x = nodo.x + radio - 5
        if orden >= 10:
            texto_orden_x -= 3
        texto_orden.setPos(texto_orden_x, nodo.y - radio - 18)
        self.addItem(texto_orden)

        # Dibujar nodos hijos
        for hijo in nodo.hijos:
            self._dibujar_nodos(hijo)

    def _dibujar_leyenda(self):
        """Dibuja una leyenda con los diferentes tipos de nodos"""
        y_pos = 60
        x_pos = 50

        # Título
        titulo = QGraphicsTextItem("Tipos de nodos:")
        titulo.setFont(QFont("Arial", 12, QFont.Bold))
        titulo.setDefaultTextColor(QColor("#FFFFFF"))
        titulo.setPos(x_pos, y_pos)
        self.addItem(titulo)

        y_pos += 30

        # Seleccionar algunos tipos importantes para la leyenda
        tipos_leyenda = [
            ("programa", "Programa"),
            ("declaraciones", "Declaraciones"),
            ("instrucciones", "Instrucciones"),
            ("condicionales", "Condicionales"),
            ("bucles", "Bucles")
        ]

        for tipo, nombre in tipos_leyenda:
            # Dibujar círculo pequeño
            color = self.colores_tipos.get(tipo, "#808080")
            circulo = QGraphicsEllipseItem(x_pos, y_pos, 15, 15)
            circulo.setBrush(QBrush(QColor(color)))
            circulo.setPen(QPen(QColor("#FFFFFF"), 1))
            self.addItem(circulo)

            # Texto
            texto = QGraphicsTextItem(nombre)
            texto.setFont(QFont("Arial", 10))
            texto.setDefaultTextColor(QColor("#FFFFFF"))
            texto.setPos(x_pos + 25, y_pos - 2)
            self.addItem(texto)

            y_pos += 20


# Ventana principal para mostrar los árboles
class VisualizadorArbol(QDialog):
    def __init__(self, arbol, parent=None):
        super(VisualizadorArbol, self).__init__(parent)
        self.setWindowTitle("Visualizador de Árboles y Recorridos")
        self.setMinimumSize(1000, 700)
        self.setModal(True)  # Modal para bloquear la ventana principal

        # Guardar el árbol
        self.arbol = arbol

        # Configurar interfaz
        self._configurar_ui()

        # Mostrar árbol inicial (pre-orden)
        self._mostrar_arbol("preorden")

    def _configurar_ui(self):
        # Layout principal
        layout_principal = QVBoxLayout(self)

        # Crear pestañas
        self.tab_widget = QTabWidget()

        # Crear pestañas para cada recorrido
        self.tab_preorden = QWidget()
        self.tab_inorden = QWidget()
        self.tab_postorden = QWidget()

        # Crear vistas para cada recorrido
        self.vista_preorden = QGraphicsView()
        self.vista_inorden = QGraphicsView()
        self.vista_postorden = QGraphicsView()

        # Crear escenas para cada recorrido
        self.escena_preorden = VistaArbol()
        self.escena_inorden = VistaArbol()
        self.escena_postorden = VistaArbol()

        # Establecer escenas en las vistas
        self.vista_preorden.setScene(self.escena_preorden)
        self.vista_inorden.setScene(self.escena_inorden)
        self.vista_postorden.setScene(self.escena_postorden)

        # Habilitar antialiasing para suavizar los gráficos
        self.vista_preorden.setRenderHint(QPainter.Antialiasing)
        self.vista_inorden.setRenderHint(QPainter.Antialiasing)
        self.vista_postorden.setRenderHint(QPainter.Antialiasing)

        # Layouts para cada pestaña
        self.layout_preorden = QVBoxLayout(self.tab_preorden)
        self.layout_inorden = QVBoxLayout(self.tab_inorden)
        self.layout_postorden = QVBoxLayout(self.tab_postorden)

        # Agregar vistas a los layouts de las pestañas
        self.layout_preorden.addWidget(self.vista_preorden)
        self.layout_inorden.addWidget(self.vista_inorden)
        self.layout_postorden.addWidget(self.vista_postorden)

        # Agregar pestañas con nombres Unicode
        self.tab_widget.addTab(self.tab_preorden, "Pre-orden")
        self.tab_widget.addTab(self.tab_inorden, "In-orden")
        self.tab_widget.addTab(self.tab_postorden, "Post-orden")

        # Conectar cambio de pestaña
        self.tab_widget.currentChanged.connect(self._cambiar_pestana)

        # Agregar elementos al layout principal
        layout_principal.addWidget(self.tab_widget)


    def _cambiar_pestana(self, indice):
        """Maneja el cambio de pestañas"""
        if indice == 0:
            self._mostrar_arbol("preorden")
        elif indice == 1:
            self._mostrar_arbol("inorden")
        else:
            self._mostrar_arbol("postorden")

    def _mostrar_arbol(self, tipo):
        """Muestra el árbol con el recorrido especificado"""
        # Dibujar árboles en cada pestaña
        self.escena_preorden.dibujar_arbol(self.arbol, "preorden")
        self.escena_inorden.dibujar_arbol(self.arbol, "inorden")
        self.escena_postorden.dibujar_arbol(self.arbol, "postorden")

        # Cambiar a la pestaña correspondiente
        if tipo == "preorden":
            self.tab_widget.setCurrentIndex(0)
        elif tipo == "inorden":
            self.tab_widget.setCurrentIndex(1)
        else:
            self.tab_widget.setCurrentIndex(2)

        # Ajustar vista
        self.vista_preorden.fitInView(self.escena_preorden.itemsBoundingRect(), Qt.KeepAspectRatio)
        self.vista_inorden.fitInView(self.escena_inorden.itemsBoundingRect(), Qt.KeepAspectRatio)
        self.vista_postorden.fitInView(self.escena_postorden.itemsBoundingRect(), Qt.KeepAspectRatio)

    def resizeEvent(self, event):
        """Asegura que el árbol se ajuste correctamente al cambiar el tamaño de la ventana"""
        super(VisualizadorArbol, self).resizeEvent(event)

        # Ajustar todas las vistas
        self.vista_preorden.fitInView(self.escena_preorden.itemsBoundingRect(), Qt.KeepAspectRatio)
        self.vista_inorden.fitInView(self.escena_inorden.itemsBoundingRect(), Qt.KeepAspectRatio)
        self.vista_postorden.fitInView(self.escena_postorden.itemsBoundingRect(), Qt.KeepAspectRatio)


# Función principal para mostrar el visualizador
def mostrar_arbol_recorridos(codigo, parent=None):
    """
    Función principal que crea y muestra el visualizador de recorridos de árboles
    """
    try:
        # Crear árbol
        arbol = ArbolBinario()

        # Construir árbol desde el código usando la nueva implementación
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

    # Crear árbol
    arbol = ArbolBinario()
    arbol.crear_arbol_ejemplo()

    # Mostrar visualizador
    visualizador = VisualizadorArbol(arbol)
    visualizador.show()

    sys.exit(app.exec_())