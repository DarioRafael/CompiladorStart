# -*- coding: utf-8 -*-
# Este archivo implementa la lógica para generar un árbol de derivación
# basado en los resultados del análisis sintáctico

class NodoArbol:
    """Representa un nodo en el árbol de derivación"""

    def __init__(self, tipo, valor=None, linea=None):
        self.tipo = tipo
        self.valor = valor
        self.linea = linea
        self.hijos = []

    def agregar_hijo(self, nodo):
        """Agrega un hijo al nodo actual"""
        self.hijos.append(nodo)
        return nodo


# Extensión del analizador sintáctico para construir el árbol
def construir_arbol_derivacion(codigo_fuente):
    """
    Construye un árbol de derivación a partir del análisis sintáctico del código
    """
    from analizador_sintactico import prueba_sintactica
    from analizador_lexico import tabla_simbolos

    # Limpiar tabla de símbolos antes de análisis
    tabla_simbolos.limpiar()

    # Realizar análisis sintáctico
    resultados = prueba_sintactica(codigo_fuente)

    # Verificar si hay errores en el análisis sintáctico
    errores = [r for r in resultados if "Error" in r]
    if errores:
        return None, errores

    # Construir el árbol
    raiz = NodoArbol("programa")

    # Crear nodo para la clase principal
    clase_encontrada = False
    for linea in codigo_fuente.split('\n'):
        linea = linea.strip()
        if "class" in linea and "{" in linea:
            clase_encontrada = True
            partes = linea.split("class")
            nombre_clase = partes[1].split("{")[0].strip()
            nodo_clase = NodoArbol("declaracion_clase", nombre_clase)
            raiz.agregar_hijo(nodo_clase)

            # Ahora buscar métodos
            agregar_metodos(codigo_fuente, nodo_clase)

            # Buscar atributos
            agregar_atributos(codigo_fuente, nodo_clase)

            break

    if not clase_encontrada:
        # Si no hay una clase explícita, crear un nodo genérico
        raiz.agregar_hijo(NodoArbol("código_fuente", "Código sin estructura de clase"))

    return raiz, resultados


def agregar_metodos(codigo_fuente, nodo_padre):
    """Agrega los nodos de métodos encontrados en el código"""
    import re

    # Patrón para detectar métodos
    patron_metodo = r'(public|private|protected)?\s+(static)?\s*(\w+)\s+(\w+)\s*\([^)]*\)\s*{'

    # Buscar todos los métodos
    for idx, linea in enumerate(codigo_fuente.split('\n'), 1):
        match = re.search(patron_metodo, linea)
        if match:
            tipo_retorno = match.group(3)
            nombre_metodo = match.group(4)

            # Ignorar si es la declaración de clase
            if nombre_metodo != "class":
                nodo_metodo = NodoArbol("metodo", nombre_metodo, idx)
                nodo_padre.agregar_hijo(nodo_metodo)

                # Buscar el cuerpo del método y agregar sentencias
                agregar_sentencias(codigo_fuente, idx, nodo_metodo)


def agregar_atributos(codigo_fuente, nodo_padre):
    """Agrega los nodos de atributos de clase"""
    import re

    # Patrón para detectar atributos
    patron_atributo = r'(public|private|protected)?\s+(static)?\s*(\w+)\s+(\w+)\s*;'

    # Buscar todos los atributos
    for idx, linea in enumerate(codigo_fuente.split('\n'), 1):
        linea = linea.strip()
        match = re.search(patron_atributo, linea)
        if match and "class" not in linea and "(" not in linea:
            tipo = match.group(3)
            nombre = match.group(4)
            nodo_atributo = NodoArbol("atributo", f"{tipo} {nombre}", idx)
            nodo_padre.agregar_hijo(nodo_atributo)


def agregar_sentencias(codigo_fuente, linea_inicio, nodo_padre):
    """Agrega sentencias dentro de un método"""
    import re

    lineas = codigo_fuente.split('\n')
    contador_llaves = 0
    dentro_metodo = False
    buffer_lineas = []

    # Buscar el cuerpo del método
    for idx, linea in enumerate(lineas[linea_inicio - 1:], linea_inicio):
        if '{' in linea and not dentro_metodo:
            dentro_metodo = True
            contador_llaves += linea.count('{')
        elif dentro_metodo:
            contador_llaves += linea.count('{')
            contador_llaves -= linea.count('}')
            buffer_lineas.append((idx, linea))

            if contador_llaves == 0:
                break

    # Analizar cada línea dentro del método
    for idx, linea in buffer_lineas:
        linea = linea.strip()
        if not linea or linea == "{" or linea == "}":
            continue

        # Detectar declaraciones
        if re.search(r'(\w+)\s+(\w+)\s*=', linea) or re.search(r'(\w+)\s+(\w+);', linea):
            nodo_sentencia = NodoArbol("declaracion", linea, idx)
            nodo_padre.agregar_hijo(nodo_sentencia)
        # Detectar asignaciones
        elif "=" in linea and "==" not in linea:
            nodo_sentencia = NodoArbol("asignacion", linea, idx)
            nodo_padre.agregar_hijo(nodo_sentencia)
        # Detectar if
        elif linea.startswith("if"):
            nodo_sentencia = NodoArbol("if", linea, idx)
            nodo_padre.agregar_hijo(nodo_sentencia)
        # Detectar for
        elif linea.startswith("for"):
            nodo_sentencia = NodoArbol("for", linea, idx)
            nodo_padre.agregar_hijo(nodo_sentencia)
        # Detectar while
        elif linea.startswith("while"):
            nodo_sentencia = NodoArbol("while", linea, idx)
            nodo_padre.agregar_hijo(nodo_sentencia)
        # Detectar llamadas a métodos
        elif "(" in linea and ")" in linea and ";" in linea:
            nodo_sentencia = NodoArbol("llamada", linea, idx)
            nodo_padre.agregar_hijo(nodo_sentencia)
        # Otras sentencias
        else:
            nodo_sentencia = NodoArbol("sentencia", linea, idx)
            nodo_padre.agregar_hijo(nodo_sentencia)


def generar_arbol_qt(nodo, parent_item=None, tree_widget=None):
    """
    Convierte un árbol de derivación en un QTreeWidgetItem para mostrar en QTreeWidget
    """
    from PyQt5.QtWidgets import QTreeWidgetItem
    from PyQt5.QtGui import QColor, QBrush, QFont

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

    # Formatos específicos por tipo de nodo
    if nodo.tipo == "programa":
        item.setFont(0, QFont("Consolas", 12, QFont.Bold))
        item.setForeground(0, QBrush(QColor('#F89406')))  # Naranja
    elif nodo.tipo == "declaracion_clase":
        item.setFont(0, QFont("Consolas", 12, QFont.Bold))
        item.setForeground(0, QBrush(QColor('#569CD6')))  # Azul
    elif nodo.tipo == "metodo":
        item.setFont(0, QFont("Consolas", 11, QFont.Bold))
        item.setForeground(0, QBrush(QColor('#4EC9B0')))  # Verde agua
    elif nodo.tipo == "atributo":
        item.setForeground(0, QBrush(QColor('#9CDCFE')))  # Azul claro
    elif nodo.tipo == "declaracion":
        item.setForeground(0, QBrush(QColor('#DCDCAA')))  # Amarillo
    elif nodo.tipo == "if" or nodo.tipo == "for" or nodo.tipo == "while":
        item.setForeground(0, QBrush(QColor('#C586C0')))  # Morado
    elif nodo.tipo == "llamada":
        item.setForeground(0, QBrush(QColor('#57A64A')))  # Verde

    # Agregar hijos recursivamente
    for hijo in nodo.hijos:
        generar_arbol_qt(hijo, item, tree_widget)

    return item