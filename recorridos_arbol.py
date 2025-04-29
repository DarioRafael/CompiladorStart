# -*- coding: utf-8 -*-
# Módulo para generar los recorridos de árboles
# Este módulo implementa la lógica para generar recorridos en pre-orden, in-orden y post-orden

from PyQt5.QtWidgets import QTreeWidgetItem
from PyQt5.QtGui import QColor, QBrush, QFont


class NodoRecorrido:
    """Clase para representar un nodo en el árbol de recorridos"""

    def __init__(self, tipo, valor=None, linea=None):
        self.tipo = tipo
        self.valor = valor
        self.linea = linea
        self.hijos = []
        self.recorrido_preorden = []
        self.recorrido_inorden = []
        self.recorrido_postorden = []

    def agregar_hijo(self, nodo):
        """Agrega un hijo al nodo actual"""
        self.hijos.append(nodo)
        return nodo


def construir_arbol_recorridos(codigo_fuente):
    """
    Construye un árbol y sus recorridos a partir del análisis del código

    Args:
        codigo_fuente: Código fuente Java a analizar

    Returns:
        NodoRecorrido: El nodo raíz del árbol con sus recorridos calculados
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
    return construir_arbol_desde_tokens(tokens), resultados


def construir_arbol_desde_tokens(tokens):
    """
    Construye un árbol estructurado a partir de los tokens del análisis léxico

    Args:
        tokens: Lista de tokens del análisis léxico

    Returns:
        NodoRecorrido: Raíz del árbol construido
    """
    raiz = NodoRecorrido("programa", "Código Java")

    # Agrupamos tokens por estructuras lógicas
    estructuras = agrupar_tokens_por_estructura(tokens)

    # Construir el árbol con los grupos de tokens
    for tipo, grupo in estructuras.items():
        nodo_estructura = NodoRecorrido(tipo, f"{tipo.capitalize()}")
        raiz.agregar_hijo(nodo_estructura)

        for token in grupo:
            # Solo incluimos tokens significativos
            if token.get("tipo") not in ["LLAIZQ", "LLADER", "PUNTOCOMA"]:
                valor = str(token.get("valor", ""))
                tipo = token.get("tipo", "")
                linea = token.get("linea", 0)

                nodo_token = NodoRecorrido(tipo.lower(), valor, linea)
                nodo_estructura.agregar_hijo(nodo_token)

    # Calcular los recorridos
    calcular_recorridos(raiz)

    return raiz


def agrupar_tokens_por_estructura(tokens):
    """
    Agrupa los tokens en estructuras lógicas del programa con mayor precisión

    Args:
        tokens: Lista de tokens del análisis léxico

    Returns:
        dict: Diccionario con tokens agrupados por estructura
    """
    estructuras = {
        "clases": [],
        "declaraciones": [],
        "metodos": [],
        "palabras_reservadas": [],
        "condicionales": [],
        "bucles": [],
        "asignaciones": [],
        "llamadas": [],
        "operadores": [],
        "simbolos": []
    }

    i = 0
    while i < len(tokens):
        token = tokens[i]
        tipo = token.get("tipo", "")

        # Palabras reservadas del lenguaje
        if tipo in ["PUBLIC", "PRIVATE", "PROTECTED", "STATIC", "VOID", "CLASS", "ABSTRACT", "FINAL"]:
            estructuras["palabras_reservadas"].append(token)
            i += 1
            continue

        # Símbolos de puntuación
        if tipo in ["LLAIZQ", "LLADER", "PUNTOCOMA", "CORIZQ", "CORDER", "PARIZQ", "PARDER", "PUNTO"]:
            estructuras["simbolos"].append(token)
            i += 1
            continue

        # Operadores
        if tipo in ["ASIGNAR", "SUMA", "RESTA", "MULT", "DIV", "INCREMENTO", "DECREMENTO",
                    "MENORQUE", "MAYORQUE", "MENORIGUAL", "MAYORIGUAL", "MULTASIGNAR"]:
            estructuras["operadores"].append(token)
            i += 1
            continue

        # Identificar declaración de clases
        if tipo == "CLASS":
            clase = [token]
            j = i + 1
            # Capturar nombre de la clase y llaves
            while j < len(tokens) and tokens[j].get("tipo") not in ["LLAIZQ", "LLADER"]:
                clase.append(tokens[j])
                j += 1
            if j < len(tokens):
                clase.append(tokens[j])

            estructuras["clases"].extend(clase)
            i = j + 1
            continue

        # Identificar métodos (como el método main)
        elif tipo in ["PUBLIC", "PRIVATE", "PROTECTED"] and i + 2 < len(tokens) and \
                tokens[i + 1].get("tipo") in ["STATIC", "VOID", "INT", "STRING"] and \
                tokens[i + 2].get("tipo") == "IDENTIFICADOR":
            metodo = [token]
            j = i + 1
            llaves_abiertas = 0

            # Capturar toda la firma del método y su contenido
            while j < len(tokens):
                metodo.append(tokens[j])

                if tokens[j].get("tipo") == "LLAIZQ":
                    llaves_abiertas += 1
                elif tokens[j].get("tipo") == "LLADER":
                    llaves_abiertas -= 1

                if llaves_abiertas == 0 and tokens[j].get("tipo") == "LLADER":
                    break

                j += 1

            estructuras["metodos"].extend(metodo)
            i = j + 1
            continue

        # Declaraciones de variables
        elif tipo in ["INT", "FLOAT", "DOUBLE", "BOOLEAN", "CHAR", "STRING"]:
            declaracion = [token]
            j = i + 1
            while j < len(tokens) and tokens[j].get("tipo") != "PUNTOCOMA":
                declaracion.append(tokens[j])
                j += 1
            if j < len(tokens):
                declaracion.append(tokens[j])

            estructuras["declaraciones"].extend(declaracion)
            i = j + 1
            continue

        # Condicionales (if, else, switch)
        elif tipo in ["IF", "ELSE", "SWITCH", "CASE"]:
            condicional = [token]
            j = i + 1
            llaves_abiertas = 0

            while j < len(tokens):
                condicional.append(tokens[j])

                if tokens[j].get("tipo") == "LLAIZQ":
                    llaves_abiertas += 1
                elif tokens[j].get("tipo") == "LLADER":
                    llaves_abiertas -= 1

                if llaves_abiertas == 0 and tokens[j].get("tipo") == "LLADER":
                    break

                j += 1

            estructuras["condicionales"].extend(condicional)
            i = j + 1
            continue

        # Bucles (for, while, do)
        elif tipo in ["FOR", "WHILE", "DO"]:
            bucle = [token]
            j = i + 1
            llaves_abiertas = 0

            while j < len(tokens):
                bucle.append(tokens[j])

                if tokens[j].get("tipo") == "LLAIZQ":
                    llaves_abiertas += 1
                elif tokens[j].get("tipo") == "LLADER":
                    llaves_abiertas -= 1

                if llaves_abiertas == 0 and tokens[j].get("tipo") == "LLADER":
                    break

                j += 1

            estructuras["bucles"].extend(bucle)
            i = j + 1
            continue

        # Asignaciones
        elif tipo == "IDENTIFICADOR" and i + 1 < len(tokens) and tokens[i + 1].get("tipo") == "ASIGNAR":
            asignacion = [token, tokens[i + 1]]
            j = i + 2

            while j < len(tokens) and tokens[j].get("tipo") != "PUNTOCOMA":
                asignacion.append(tokens[j])
                j += 1
            if j < len(tokens):
                asignacion.append(tokens[j])

            estructuras["asignaciones"].extend(asignacion)
            i = j + 1
            continue

        # Llamadas a funciones
        elif tipo == "IDENTIFICADOR" and i + 1 < len(tokens) and tokens[i + 1].get("tipo") == "PARIZQ":
            llamada = [token, tokens[i + 1]]
            j = i + 2
            llaves_abiertas = 1

            while j < len(tokens) and llaves_abiertas > 0:
                if tokens[j].get("tipo") == "PARIZQ":
                    llaves_abiertas += 1
                elif tokens[j].get("tipo") == "PARDER":
                    llaves_abiertas -= 1
                llamada.append(tokens[j])
                j += 1

            while j < len(tokens) and tokens[j].get("tipo") != "PUNTOCOMA":
                llamada.append(tokens[j])
                j += 1
            if j < len(tokens):
                llamada.append(tokens[j])

            estructuras["llamadas"].extend(llamada)
            i = j + 1
            continue

        # Cualquier token que no encaje en las categorías anteriores
        # Intentamos categorizarlo de la manera más precisa posible
        if tipo in ["IDENTIFICADOR", "ENTERO", "DECIMAL", "CADENA", "CARACTER"]:
            estructuras["declaraciones"].append(token)
        else:
            # Si realmente no sabemos qué es, lo ponemos en palabras reservadas
            estructuras["palabras_reservadas"].append(token)

        i += 1

    return estructuras

def calcular_recorridos(nodo):
    """
    Calcula y almacena los recorridos pre-orden, in-orden y post-orden para el árbol

    Args:
        nodo: Nodo raíz del árbol
    """

    # Pre-orden: Raíz, Izquierda, Derecha
    def preorden(nodo):
        if not nodo:
            return []

        resultado = [(nodo.tipo, nodo.valor)]
        for hijo in nodo.hijos:
            resultado.extend(preorden(hijo))
        return resultado

    # In-orden: Izquierda, Raíz, Derecha
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
    nodo.recorrido_preorden = preorden(nodo)
    nodo.recorrido_inorden = inorden(nodo)
    nodo.recorrido_postorden = postorden(nodo)

    return nodo


def mostrar_recorridos_en_arbol(arbol, tree_widget):
    """
    Muestra los recorridos del árbol en un QTreeWidget

    Args:
        arbol: Árbol con recorridos calculados
        tree_widget: Widget donde mostrar los recorridos
    """
    # Limpiar el árbol
    tree_widget.clear()

    # Configurar el encabezado
    tree_widget.setHeaderLabel("Recorridos del Árbol")
    header_font = QFont("Consolas", 12, QFont.Bold)
    tree_widget.headerItem().setFont(0, header_font)
    tree_widget.headerItem().setForeground(0, QBrush(QColor('#F89406')))

    # Crear los nodos para cada tipo de recorrido
    preorden_item = QTreeWidgetItem(tree_widget)
    preorden_item.setText(0, "Recorrido Pre-orden (Raíz → Izquierda → Derecha)")
    preorden_item.setFont(0, QFont("Consolas", 12, QFont.Bold))
    preorden_item.setForeground(0, QBrush(QColor('#569CD6')))  # Azul

    inorden_item = QTreeWidgetItem(tree_widget)
    inorden_item.setText(0, "Recorrido In-orden (Izquierda → Raíz → Derecha)")
    inorden_item.setFont(0, QFont("Consolas", 12, QFont.Bold))
    inorden_item.setForeground(0, QBrush(QColor('#4EC9B0')))  # Verde agua

    postorden_item = QTreeWidgetItem(tree_widget)
    postorden_item.setText(0, "Recorrido Post-orden (Izquierda → Derecha → Raíz)")
    postorden_item.setFont(0, QFont("Consolas", 12, QFont.Bold))
    postorden_item.setForeground(0, QBrush(QColor('#C586C0')))  # Morado

    # Añadir los elementos de cada recorrido
    for tipo, valor in arbol.recorrido_preorden:
        item = QTreeWidgetItem(preorden_item)
        texto = f"{tipo}"
        if valor:
            texto += f": {valor}"
        item.setText(0, texto)
        asignar_estilo_nodo(item, tipo)

    for tipo, valor in arbol.recorrido_inorden:
        item = QTreeWidgetItem(inorden_item)
        texto = f"{tipo}"
        if valor:
            texto += f": {valor}"
        item.setText(0, texto)
        asignar_estilo_nodo(item, tipo)

    for tipo, valor in arbol.recorrido_postorden:
        item = QTreeWidgetItem(postorden_item)
        texto = f"{tipo}"
        if valor:
            texto += f": {valor}"
        item.setText(0, texto)
        asignar_estilo_nodo(item, tipo)

    # Expandir todos los recorridos
    tree_widget.expandAll()


def asignar_estilo_nodo(item, tipo):
    """
    Asigna estilos visuales a un ítem del árbol según su tipo

    Args:
        item: QTreeWidgetItem al que aplicar el estilo
        tipo: Tipo de nodo que determina el estilo
    """
    item.setForeground(0, QBrush(QColor('#FFFFFF')))

    # Aplicar estilos según el tipo
    if tipo == "programa":
        item.setFont(0, QFont("Consolas", 10, QFont.Bold))
        item.setForeground(0, QBrush(QColor('#F89406')))  # Naranja
    elif tipo == "declaraciones":
        item.setFont(0, QFont("Consolas", 10, QFont.Bold))
        item.setForeground(0, QBrush(QColor('#9CDCFE')))  # Azul claro
    elif tipo == "condicionales":
        item.setFont(0, QFont("Consolas", 10, QFont.Bold))
        item.setForeground(0, QBrush(QColor('#C586C0')))  # Morado
    elif tipo == "bucles":
        item.setFont(0, QFont("Consolas", 10, QFont.Bold))
        item.setForeground(0, QBrush(QColor('#D7BA7D')))  # Amarillo ocre
    elif tipo == "asignaciones":
        item.setFont(0, QFont("Consolas", 10))
        item.setForeground(0, QBrush(QColor('#DCDCAA')))  # Amarillo
    elif tipo == "llamadas":
        item.setFont(0, QFont("Consolas", 10))
        item.setForeground(0, QBrush(QColor('#57A64A')))  # Verde
    elif tipo == "identificador":
        item.setForeground(0, QBrush(QColor('#9CDCFE')))  # Azul claro
    elif tipo in ["int", "float", "double", "boolean", "char", "string"]:
        item.setForeground(0, QBrush(QColor('#569CD6')))  # Azul
    elif tipo == "entero" or tipo == "decimal":
        item.setForeground(0, QBrush(QColor('#B5CEA8')))  # Verde claro
    elif tipo == "cadena":
        item.setForeground(0, QBrush(QColor('#CE9178')))  # Rojo claro


def visualizar_recorridos_arbol(codigo_fuente, tree_widget):
    """
    Función principal para generar y mostrar los recorridos del árbol

    Args:
        codigo_fuente: Código fuente Java a analizar
        tree_widget: QTreeWidget donde se mostrarán los recorridos

    Returns:
        bool: True si se generaron correctamente, False en caso contrario
    """
    try:
        # Construir el árbol con sus recorridos
        arbol, resultados = construir_arbol_recorridos(codigo_fuente)

        if arbol is None:
            return False

        # Mostrar los recorridos en el widget
        mostrar_recorridos_en_arbol(arbol, tree_widget)

        # Imprimir recorridos por consola
        print("\n--- Recorridos del Árbol ---")

        print("\nRecorrido Pre-orden:")
        for tipo, valor in arbol.recorrido_preorden:
            print(f"{tipo}: {valor}" if valor else f"{tipo}")

        print("\nRecorrido In-orden:")
        for tipo, valor in arbol.recorrido_inorden:
            print(f"{tipo}: {valor}" if valor else f"{tipo}")

        print("\nRecorrido Post-orden:")
        for tipo, valor in arbol.recorrido_postorden:
            print(f"{tipo}: {valor}" if valor else f"{tipo}")

        return True

    except Exception as e:
        print(f"Error al generar los recorridos del árbol: {str(e)}")
        return False