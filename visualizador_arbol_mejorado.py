# -*- coding: utf-8 -*-
# Visualizador avanzado de árboles de derivación
# Este módulo mejora la presentación del árbol de derivación
# sin depender de recursos externos

from PyQt5.QtWidgets import QTreeWidgetItem
from PyQt5.QtGui import QColor, QBrush, QFont
import re


class NodoArbolDetallado:
    """Extiende la información de un nodo del árbol de derivación con detalles adicionales"""

    def __init__(self, tipo, valor=None, linea=None, detalles=None):
        self.tipo = tipo
        self.valor = valor
        self.linea = linea
        self.detalles = detalles or {}
        self.hijos = []

    def agregar_hijo(self, nodo):
        """Agrega un hijo al nodo actual"""
        self.hijos.append(nodo)
        return nodo

    def agregar_detalle(self, clave, valor):
        """Agrega información detallada al nodo"""
        self.detalles[clave] = valor
        return self


def generar_arbol_detallado(nodo_original):
    """
    Enriquece un árbol de derivación existente con información adicional
    para una mejor visualización.

    Args:
        nodo_original: El nodo raíz del árbol original

    Returns:
        NodoArbolDetallado: El nodo raíz del árbol enriquecido
    """

    def _procesar_nodo(nodo_orig):
        # Crear una versión detallada del nodo
        nodo_detallado = NodoArbolDetallado(
            nodo_orig.tipo,
            nodo_orig.valor,
            nodo_orig.linea
        )

        # Agregar metadatos según el tipo de nodo
        if nodo_orig.tipo == "if":
            # Para sentencias if, extraer la condición
            if nodo_orig.valor and "(" in nodo_orig.valor and ")" in nodo_orig.valor:
                condicion = nodo_orig.valor.split("(")[1].split(")")[0]

                # Crear nodos específicos para la estructura if
                nodo_condicion = NodoArbolDetallado("condicion", condicion, nodo_orig.linea)
                nodo_detallado.agregar_hijo(nodo_condicion)

                # Analizar condición para crear subnodos (operandos y operadores)
                if "==" in condicion:
                    partes = condicion.split("==")
                    izq = partes[0].strip()
                    der = partes[1].strip()

                    # Detectar si hay operaciones en los operandos (como el módulo %)
                    if "%" in izq:
                        subpartes = izq.split("%")
                        nodo_izq = NodoArbolDetallado("operando_izquierdo", izq, nodo_orig.linea)
                        nodo_condicion.agregar_hijo(nodo_izq)

                        nodo_izq.agregar_hijo(
                            NodoArbolDetallado("operando_izquierdo", subpartes[0].strip(), nodo_orig.linea))
                        nodo_izq.agregar_hijo(NodoArbolDetallado("operador", "%", nodo_orig.linea))
                        nodo_izq.agregar_hijo(
                            NodoArbolDetallado("operando_derecho", subpartes[1].strip(), nodo_orig.linea))
                    else:
                        nodo_condicion.agregar_hijo(NodoArbolDetallado("operando_izquierdo", izq, nodo_orig.linea))

                    # Agregar operador de igualdad
                    nodo_condicion.agregar_hijo(NodoArbolDetallado("operador", "==", nodo_orig.linea))

                    # Agregar operando derecho
                    nodo_condicion.agregar_hijo(NodoArbolDetallado("operando_derecho", der, nodo_orig.linea))

                # Buscar hijos originales del if para crear bloque if y else
                bloques_creados = False
                for hijo in nodo_orig.hijos:
                    if hijo.tipo == "declaracion" or hijo.tipo == "asignacion" or hijo.tipo == "llamada":
                        if not bloques_creados:
                            # Es el primer bloque (if)
                            bloque_if = NodoArbolDetallado("bloque_if", None, hijo.linea)
                            nodo_detallado.agregar_hijo(bloque_if)
                            bloque_if.agregar_hijo(_procesar_nodo(hijo))
                            bloques_creados = True
                        else:
                            # Es el segundo bloque (else)
                            bloque_else = NodoArbolDetallado("bloque_else", None, hijo.linea)
                            nodo_detallado.agregar_hijo(bloque_else)
                            bloque_else.agregar_hijo(_procesar_nodo(hijo))
                    else:
                        # Procesar otros hijos normalmente
                        nodo_hijo = _procesar_nodo(hijo)
                        nodo_detallado.agregar_hijo(nodo_hijo)

                return nodo_detallado

        elif nodo_orig.tipo == "llamada":
            # Para llamadas a métodos, extraer información detallada
            if "System.out.println" in nodo_orig.valor:
                partes = nodo_orig.valor.split("(")
                if len(partes) > 1:
                    objeto = NodoArbolDetallado("objeto", "System.out", nodo_orig.linea)
                    metodo = NodoArbolDetallado("metodo", "println", nodo_orig.linea)

                    # Extraer argumento entre paréntesis
                    arg_texto = partes[1].split(")")[0]
                    argumento = NodoArbolDetallado("argumento", arg_texto, nodo_orig.linea)

                    nodo_detallado.agregar_hijo(objeto)
                    nodo_detallado.agregar_hijo(metodo)
                    nodo_detallado.agregar_hijo(argumento)

                    return nodo_detallado

        elif nodo_orig.tipo == "declaracion":
            # Para declaraciones, extraer tipo y valor
            if "=" in nodo_orig.valor:
                partes = nodo_orig.valor.split("=")
                decl = partes[0].strip().split()
                if len(decl) >= 2:
                    tipo = decl[0]
                    nombre = decl[1]
                    valor = partes[1].strip()

                    nodo_detallado.valor = f"{tipo} {nombre} = {valor}"
                    nodo_detallado.agregar_detalle("tipo", tipo)
                    nodo_detallado.agregar_detalle("nombre", nombre)
                    nodo_detallado.agregar_detalle("valor_inicial", valor)

        # Proceso general para otros tipos de nodos
        for hijo in nodo_orig.hijos:
            nodo_hijo = _procesar_nodo(hijo)
            nodo_detallado.agregar_hijo(nodo_hijo)

        return nodo_detallado

    # Comenzar el procesamiento desde la raíz
    arbol_detallado = _procesar_nodo(nodo_original)
    return arbol_detallado


def generar_arbol_qt_mejorado(nodo, parent_item=None, tree_widget=None):
    """
    Genera una representación visual mejorada del árbol de derivación en un QTreeWidget

    Args:
        nodo: Nodo actual del árbol (puede ser NodoArbol original o NodoArbolDetallado)
        parent_item: Item padre en el widget de árbol
        tree_widget: Widget de árbol donde se mostrará

    Returns:
        QTreeWidgetItem: El item creado
    """
    # Crear el texto del nodo
    texto_nodo = f"{nodo.tipo}"
    if nodo.valor:
        texto_nodo += f": {nodo.valor}"
    if nodo.linea:
        texto_nodo += f" (línea {nodo.linea})"

    # Crear el item para el árbol
    if parent_item is None:
        # Primer nodo, raíz del árbol
        item = QTreeWidgetItem(tree_widget)
    else:
        # Nodo hijo
        item = QTreeWidgetItem(parent_item)

    item.setText(0, texto_nodo)

    # Aplicar formato según el tipo de nodo
    item.setForeground(0, QBrush(QColor('#FFFFFF')))

    # Formatos específicos por tipo de nodo con colores más intensos
    if nodo.tipo == "programa":
        item.setFont(0, QFont("Consolas", 12, QFont.Bold))
        item.setForeground(0, QBrush(QColor('#F89406')))  # Naranja
        item.setBackground(0, QBrush(QColor('#2D2D30')))  # Fondo ligeramente más oscuro
    elif nodo.tipo == "declaracion_clase":
        item.setFont(0, QFont("Consolas", 12, QFont.Bold))
        item.setForeground(0, QBrush(QColor('#569CD6')))  # Azul
        item.setBackground(0, QBrush(QColor('#2D2D30')))
    elif nodo.tipo == "metodo":
        item.setFont(0, QFont("Consolas", 11, QFont.Bold))
        item.setForeground(0, QBrush(QColor('#4EC9B0')))  # Verde agua
    elif nodo.tipo == "atributo":
        item.setForeground(0, QBrush(QColor('#9CDCFE')))  # Azul claro
    elif nodo.tipo == "declaracion":
        item.setForeground(0, QBrush(QColor('#DCDCAA')))  # Amarillo
    elif nodo.tipo == "if":
        item.setFont(0, QFont("Consolas", 10, QFont.Bold))
        item.setForeground(0, QBrush(QColor('#C586C0')))  # Morado
    elif nodo.tipo == "for" or nodo.tipo == "while":
        item.setForeground(0, QBrush(QColor('#C586C0')))  # Morado
    elif nodo.tipo == "llamada":
        item.setForeground(0, QBrush(QColor('#57A64A')))  # Verde
    elif nodo.tipo == "condicion":
        item.setForeground(0, QBrush(QColor('#FF8C00')))  # Naranja oscuro
        item.setFont(0, QFont("Consolas", 10, QFont.Bold))
    elif nodo.tipo == "operando_izquierdo" or nodo.tipo == "operando_derecho":
        item.setForeground(0, QBrush(QColor('#9CDCFE')))  # Azul claro
    elif nodo.tipo == "operador":
        item.setForeground(0, QBrush(QColor('#D4D4D4')))  # Gris claro
        item.setFont(0, QFont("Consolas", 10, QFont.Bold))
    elif nodo.tipo == "bloque_if":
        item.setForeground(0, QBrush(QColor('#57A64A')))  # Verde
        item.setText(0, "bloque_if (entonces)")
    elif nodo.tipo == "bloque_else":
        item.setForeground(0, QBrush(QColor('#FFA07A')))  # Salmón claro
        item.setText(0, "bloque_else (sino)")
    elif nodo.tipo == "objeto" or nodo.tipo == "metodo":
        item.setForeground(0, QBrush(QColor('#4FC1FF')))  # Azul brillante
    elif nodo.tipo == "argumento":
        item.setForeground(0, QBrush(QColor('#CE9178')))  # Rojo claro

    # Agregar tooltips con información adicional
    if hasattr(nodo, 'detalles') and nodo.detalles:
        tooltip = "<b>Información detallada:</b><br>"
        for clave, valor in nodo.detalles.items():
            tooltip += f"<b>{clave}:</b> {valor}<br>"
        item.setToolTip(0, tooltip)

    # Agregar hijos recursivamente
    for hijo in nodo.hijos:
        generar_arbol_qt_mejorado(hijo, item, tree_widget)

    return item


def visualizar_arbol_derivacion_mejorado(codigo_fuente, tree_widget):
    """
    Función principal para generar y mostrar un árbol de derivación mejorado

    Args:
        codigo_fuente: Código fuente Java a analizar
        tree_widget: QTreeWidget donde se mostrará el árbol

    Returns:
        bool: True si el árbol se generó correctamente, False en caso contrario
    """
    from arbol_derivacion import construir_arbol_derivacion

    # Limpiar el árbol
    tree_widget.clear()

    try:
        # Construir el árbol de derivación básico
        arbol_basico, resultados = construir_arbol_derivacion(codigo_fuente)

        if arbol_basico is None:
            return False

        # Enriquecer el árbol con información adicional
        arbol_detallado = generar_arbol_detallado(arbol_basico)

        # Generar la representación visual
        generar_arbol_qt_mejorado(arbol_detallado, None, tree_widget)

        # Expandir el árbol hasta cierto nivel para mejor visualización
        tree_widget.expandToDepth(2)

        return True

    except Exception as e:
        print(f"Error al generar el árbol de derivación mejorado: {str(e)}")
        return False