# -*- coding: utf-8 -*-
# intermediate_code/generador_triplos.py

from dataclasses import dataclass
from typing import List, Optional, Dict
from lexer.analizador_lexico import construir_lexer


@dataclass
class Triplo:
    """Clase que representa un triplo (índice, operador, arg1, arg2)"""
    indice: int
    operador: str
    arg1: str
    arg2: str

    def __str__(self):
        return f"({self.indice}) {self.operador} {self.arg1} {self.arg2}"

    def to_table_row(self):
        """Convierte el triplo a una fila para la tabla de la GUI"""

        def format_arg(arg):
            if arg is None:
                return "∅"
            arg_str = str(arg)
            if arg_str == "":
                return "∅"
            return arg_str

        arg1_display = format_arg(self.arg1)
        arg2_display = format_arg(self.arg2)
        return [str(self.indice), self.operador, arg1_display, arg2_display]


class GeneradorTriplos:
    """Clase especializada para generar triplos optimizados desde código Java"""

    def __init__(self):
        self.triplos: List[Triplo] = []
        self.variables: Dict[str, int] = {}  # Mapeo variable -> índice del último triplo que la define
        self.contador_if = 0
        self.contador_for = 0
        self.contador_while = 0
        self.contador_etiqueta_general = 0

    def limpiar(self):
        """Limpia todos los triplos generados"""
        self.triplos.clear()
        self.variables.clear()
        self.contador_if = 0
        self.contador_for = 0
        self.contador_while = 0
        self.contador_etiqueta_general = 0

    def nueva_etiqueta_if_else(self) -> str:
        """Genera etiqueta para la parte else de un if"""
        self.contador_if += 1
        return f"if_else_{self.contador_if}"

    def nueva_etiqueta_if_fin(self) -> str:
        """Genera etiqueta para el fin de una estructura if"""
        return f"if_fin_{self.contador_if}"

    def nueva_etiqueta_for_inicio(self) -> str:
        """Genera etiqueta para el inicio de un bucle for"""
        self.contador_for += 1
        return f"for_inicio_{self.contador_for}"

    def nueva_etiqueta_for_fin(self) -> str:
        """Genera etiqueta para el fin de un bucle for"""
        return f"for_fin_{self.contador_for}"

    def nueva_etiqueta_while_inicio(self) -> str:
        """Genera etiqueta para el inicio de un bucle while"""
        self.contador_while += 1
        return f"while_inicio_{self.contador_while}"

    def nueva_etiqueta_while_fin(self) -> str:
        """Genera etiqueta para el fin de un bucle while"""
        return f"while_fin_{self.contador_while}"

    def nueva_etiqueta(self) -> str:
        """Genera una nueva etiqueta general"""
        self.contador_etiqueta_general += 1
        return f"etiqueta_{self.contador_etiqueta_general}"

    def agregar_triplo(self, operador: str, arg1: str, arg2: str) -> int:
        """Agrega un triplo y retorna su índice"""
        indice = len(self.triplos)
        arg1_norm = str(arg1) if arg1 is not None else ""
        arg2_norm = str(arg2) if arg2 is not None else ""

        triplo = Triplo(indice, operador, arg1_norm, arg2_norm)
        self.triplos.append(triplo)

        # Si es una asignación, actualizar el mapeo de variables
        if operador == "=" and arg2_norm and not arg2_norm.startswith("("):
            self.variables[arg2_norm] = indice

        return indice

    def obtener_referencia_variable(self, nombre_variable: str) -> str:
        """Obtiene la referencia correcta de una variable"""
        if nombre_variable in self.variables:
            return f"({self.variables[nombre_variable]})"
        return nombre_variable

    def generar_desde_codigo(self, codigo: str) -> List[Triplo]:
        """Genera triplos desde código Java"""
        self.limpiar()

        if not codigo.strip():
            return self.triplos

        try:
            lexer = construir_lexer()
            lexer.input(codigo)

            tokens = []
            while True:
                tok = lexer.token()
                if not tok:
                    break
                tokens.append(tok)

            self._procesar_tokens_optimizado(tokens)

        except Exception as e:
            print(f"Error generando triplos: {e}")

        return self.triplos

    def _procesar_tokens_optimizado(self, tokens):
        """Procesa tokens para generar triplos optimizados"""
        i = 0
        while i < len(tokens):
            tok = tokens[i]

            # Declaración con asignación: tipo variable = expresión;
            if (i + 4 < len(tokens) and
                    tok.type in ['INT', 'DOUBLE', 'STRING', 'BOOLEAN'] and
                    tokens[i + 1].type == 'IDENTIFICADOR' and
                    tokens[i + 2].type == 'ASIGNAR'):

                variable = tokens[i + 1].value
                i += 3  # Saltar tipo, variable, =

                expr_tokens = []
                while i < len(tokens) and tokens[i].type not in ['PUNTOCOMA', 'PUNTOYCOMA']:
                    expr_tokens.append(tokens[i])
                    i += 1

                if i < len(tokens):
                    i += 1  # Consumir punto y coma

                if expr_tokens:
                    if len(expr_tokens) == 1:
                        # Asignación simple
                        valor = self._procesar_valor(expr_tokens[0])
                        self.agregar_triplo("=", valor, variable)
                    else:
                        resultado_expr = self._procesar_expresion_optimizada(expr_tokens)
                        self.agregar_triplo("=", resultado_expr, variable)

            # Asignación simple: variable = expresión;
            elif (i + 3 < len(tokens) and
                  tok.type == 'IDENTIFICADOR' and
                  tokens[i + 1].type == 'ASIGNAR'):

                variable = tok.value
                i += 2  # Saltar variable, =

                expr_tokens = []
                while i < len(tokens) and tokens[i].type not in ['PUNTOCOMA', 'PUNTOYCOMA']:
                    expr_tokens.append(tokens[i])
                    i += 1

                if i < len(tokens):
                    i += 1  # Consumir punto y coma

                if expr_tokens:
                    if len(expr_tokens) == 1:
                        valor = self._procesar_valor(expr_tokens[0])
                        self.agregar_triplo("=", valor, variable)
                    else:
                        resultado_expr = self._procesar_expresion_optimizada(expr_tokens)
                        self.agregar_triplo("=", resultado_expr, variable)

            # Asignación compuesta: variable op= expresión;
            elif (i + 3 < len(tokens) and
                  tok.type == 'IDENTIFICADOR' and
                  tokens[i + 1].type in ['MULTASIGNAR', 'SUMAASIGNAR', 'RESTAASIGNAR', 'DIVASIGNAR']):

                variable = tok.value
                op_tipo = tokens[i + 1].type
                i += 2

                expr_tokens = []
                while i < len(tokens) and tokens[i].type not in ['PUNTOCOMA', 'PUNTOYCOMA']:
                    expr_tokens.append(tokens[i])
                    i += 1

                if i < len(tokens):
                    i += 1

                if expr_tokens:
                    op_map = {'MULTASIGNAR': '*', 'SUMAASIGNAR': '+', 'RESTAASIGNAR': '-', 'DIVASIGNAR': '/'}
                    op = op_map.get(op_tipo, '*')

                    variable_ref = self.obtener_referencia_variable(variable)

                    if len(expr_tokens) == 1:
                        valor = self._procesar_valor(expr_tokens[0])
                        indice_op = self.agregar_triplo(op, variable_ref, valor)
                        self.agregar_triplo("=", f"({indice_op})", variable)
                    else:
                        expr_resultado = self._procesar_expresion_optimizada(expr_tokens)
                        indice_op = self.agregar_triplo(op, variable_ref, expr_resultado)
                        self.agregar_triplo("=", f"({indice_op})", variable)

            # Bucles FOR
            elif tok.type == 'FOR':
                i = self._procesar_for_optimizado(tokens, i)
                continue

            # Estructuras IF
            elif tok.type == 'IF':
                i = self._procesar_if_optimizado(tokens, i)
                continue

            # System.out.println
            elif (i + 4 < len(tokens) and
                  tok.type == 'SYSTEM' and
                  tokens[i + 2].type == 'OUT' and
                  tokens[i + 4].type == 'PRINTLN'):

                i += 6  # Saltar System.out.println(

                arg_tokens = []
                paren_count = 1
                while i < len(tokens) and paren_count > 0:
                    if tokens[i].type == 'PARIZQ':
                        paren_count += 1
                    elif tokens[i].type == 'PARDER':
                        paren_count -= 1

                    if paren_count > 0:
                        arg_tokens.append(tokens[i])
                    i += 1

                if arg_tokens:
                    self._procesar_print_optimizado(arg_tokens)
                else:
                    self.agregar_triplo("PRINT", "∅", "∅")

            else:
                i += 1

    def _procesar_valor(self, token):
        """Procesa un valor individual (literal o variable)"""
        if token.type == 'IDENTIFICADOR':
            return self.obtener_referencia_variable(token.value)
        else:
            return str(token.value)

    def _procesar_for_optimizado(self, tokens, i):
        """Procesa un bucle FOR con triplos optimizados"""
        i += 1  # Saltar 'FOR'

        if i < len(tokens) and tokens[i].type == 'PARIZQ':
            i += 1

            # === INICIALIZACIÓN ===
            init_tokens = []
            while i < len(tokens) and tokens[i].type not in ['PUNTOCOMA', 'PUNTOYCOMA']:
                init_tokens.append(tokens[i])
                i += 1
            i += 1  # Saltar ';'

            # Procesar inicialización
            if len(init_tokens) >= 4:
                variable = init_tokens[1].value
                valor = init_tokens[3].value
                self.agregar_triplo("=", valor, variable)

            # === CONDICIÓN ===
            indice_inicio_condicion = len(self.triplos)  # Guardar índice donde empieza la condición

            cond_tokens = []
            while i < len(tokens) and tokens[i].type not in ['PUNTOCOMA', 'PUNTOYCOMA']:
                cond_tokens.append(tokens[i])
                i += 1
            i += 1  # Saltar ';'

            # === INCREMENTO (guardar para después) ===
            incr_tokens = []
            while i < len(tokens) and tokens[i].type != 'PARDER':
                incr_tokens.append(tokens[i])
                i += 1
            i += 1  # Saltar ')'

            # Procesar condición
            if len(cond_tokens) == 3:
                var1_nombre = cond_tokens[0].value
                operador = self._obtener_simbolo_operador(cond_tokens[1])
                var2_nombre = cond_tokens[2].value

                var1_ref = self.obtener_referencia_variable(var1_nombre)
                var2_ref = self.obtener_referencia_variable(var2_nombre)

                indice_cond = self.agregar_triplo(operador, var1_ref, var2_ref)

                # Calcular índice de fin (necesitamos contar cuerpo + incremento + goto)
                # Temporalmente ponemos un placeholder
                indice_iffalse = self.agregar_triplo("ifFalse", f"({indice_cond})", "PLACEHOLDER")

            # === CUERPO DEL BUCLE ===
            if i < len(tokens) and tokens[i].type == 'LLAVEIZQ':
                i += 1
                brace_count = 1
                cuerpo_tokens = []

                while i < len(tokens) and brace_count > 0:
                    if tokens[i].type == 'LLAVEIZQ':
                        brace_count += 1
                    elif tokens[i].type == 'LLAVEDER':
                        brace_count -= 1

                    if brace_count > 0:
                        cuerpo_tokens.append(tokens[i])
                    i += 1

                if cuerpo_tokens:
                    self._procesar_tokens_optimizado(cuerpo_tokens)

            # === PROCESAR INCREMENTO ===
            if incr_tokens and len(incr_tokens) >= 2:
                variable_incr = incr_tokens[0].value
                if incr_tokens[1].type == 'INCREMENTO':  # i++
                    var_ref = self.obtener_referencia_variable(variable_incr)
                    indice_suma = self.agregar_triplo("+", var_ref, "1")
                    self.agregar_triplo("=", f"({indice_suma})", variable_incr)

            # === SALTO AL INICIO ===
            self.agregar_triplo("goto", "∅", f"({indice_inicio_condicion})")

            # === ACTUALIZAR EL IFFALSE CON EL ÍNDICE CORRECTO ===
            indice_fin = len(self.triplos)
            if 'indice_iffalse' in locals():
                self.triplos[indice_iffalse].arg2 = f"({indice_fin})"

        return i

    def _procesar_if_optimizado(self, tokens, i):
        """Procesa una estructura IF optimizada"""
        i += 1  # Saltar 'IF'

        if i < len(tokens) and tokens[i].type == 'PARIZQ':
            i += 1

            # Recoger condición
            cond_tokens = []
            paren_count = 1
            while i < len(tokens) and paren_count > 0:
                if tokens[i].type == 'PARIZQ':
                    paren_count += 1
                elif tokens[i].type == 'PARDER':
                    paren_count -= 1

                if paren_count > 0:
                    cond_tokens.append(tokens[i])
                i += 1

            resultado_cond = self._procesar_expresion_optimizada(cond_tokens)
            etiqueta_else = self.nueva_etiqueta_if_else()
            etiqueta_fin = self.nueva_etiqueta_if_fin()

            self.agregar_triplo("IF_FALSE", resultado_cond, etiqueta_else)

            # Procesar bloque IF
            if i < len(tokens) and tokens[i].type == 'LLAVEIZQ':
                i += 1
                brace_count = 1
                if_tokens = []

                while i < len(tokens) and brace_count > 0:
                    if tokens[i].type == 'LLAVEIZQ':
                        brace_count += 1
                    elif tokens[i].type == 'LLAVEDER':
                        brace_count -= 1

                    if brace_count > 0:
                        if_tokens.append(tokens[i])
                    i += 1

                if if_tokens:
                    self._procesar_tokens_optimizado(if_tokens)

            self.agregar_triplo("GOTO", etiqueta_fin, "∅")
            self.agregar_triplo("LABEL", etiqueta_else, "∅")

            # Procesar ELSE si existe
            if i < len(tokens) and tokens[i].type == 'ELSE':
                i += 1
                if i < len(tokens) and tokens[i].type == 'LLAVEIZQ':
                    i += 1
                    brace_count = 1
                    else_tokens = []

                    while i < len(tokens) and brace_count > 0:
                        if tokens[i].type == 'LLAVEIZQ':
                            brace_count += 1
                        elif tokens[i].type == 'LLAVEDER':
                            brace_count -= 1

                        if brace_count > 0:
                            else_tokens.append(tokens[i])
                        i += 1

                    if else_tokens:
                        self._procesar_tokens_optimizado(else_tokens)

            self.agregar_triplo("LABEL", etiqueta_fin, "∅")

        return i

    def _procesar_print_optimizado(self, tokens):
        """Procesa System.out.println con referencias optimizadas"""
        expresion_completa = []

        i = 0
        while i < len(tokens):
            token = tokens[i]

            if token.type in ['SUMA', '+']:
                expresion_completa.append(" + ")
            elif token.type == 'IDENTIFICADOR':
                ref = self.obtener_referencia_variable(token.value)
                expresion_completa.append(ref)
            elif hasattr(token, 'value'):
                valor = str(token.value)
                if valor.startswith('"') and valor.endswith('"'):
                    expresion_completa.append(f'"{valor[1:-1]}"')
                else:
                    expresion_completa.append(valor)

            i += 1

        expresion_str = "".join(expresion_completa)
        self.agregar_triplo("PRINT", expresion_str, "∅")

    def _procesar_expresion_optimizada(self, tokens):
        """Procesa expresiones con referencias optimizadas"""
        if not tokens:
            return ""

        if len(tokens) == 1:
            return self._procesar_valor(tokens[0])

        # Manejar paréntesis externos
        while (len(tokens) >= 3 and
               tokens[0].type == 'PARIZQ' and
               tokens[-1].type == 'PARDER' and
               self._parentesis_balanceados(tokens)):
            tokens = tokens[1:-1]

        return self._procesar_expresion_con_precedencia_optimizada(tokens)

    def _procesar_expresion_con_precedencia_optimizada(self, tokens):
        """Procesa expresiones respetando precedencia con referencias optimizadas"""
        precedencia = {
            '||': 1, 'OR': 1,
            '&&': 2, 'AND': 2,
            '==': 3, '!=': 3, 'IGUAL': 3, 'DISTINTO': 3,
            '<': 4, '>': 4, '<=': 4, '>=': 4,
            'MENORQUE': 4, 'MAYORQUE': 4, 'MENORIGUAL': 4, 'MAYORIGUAL': 4,
            '+': 5, '-': 5, 'SUMA': 5, 'RESTA': 5,
            '*': 6, '/': 6, '%': 6, 'MULT': 6, 'DIV': 6, 'MODULO': 6
        }

        for nivel in range(1, 7):
            pos_op = self._encontrar_operador_fuera_parentesis_optimizado(tokens, precedencia, nivel)

            if pos_op != -1:
                izq = tokens[:pos_op]
                der = tokens[pos_op + 1:]

                izq_resultado = self._procesar_expresion_optimizada(izq) if izq else ""
                der_resultado = self._procesar_expresion_optimizada(der) if der else ""

                simbolo = self._obtener_simbolo_operador(tokens[pos_op])
                indice = self.agregar_triplo(simbolo, izq_resultado, der_resultado)
                return f"({indice})"

        return self._procesar_valor(tokens[0]) if tokens else ""

    def _encontrar_operador_fuera_parentesis_optimizado(self, tokens, precedencia, nivel_buscado):
        """Encuentra operador de precedencia específica fuera de paréntesis"""
        nivel_parentesis = 0

        for i in range(len(tokens) - 1, -1, -1):
            token = tokens[i]

            if token.type == 'PARDER':
                nivel_parentesis += 1
            elif token.type == 'PARIZQ':
                nivel_parentesis -= 1
            elif nivel_parentesis == 0:
                op_key = getattr(token, 'type', '') or str(getattr(token, 'value', ''))
                if precedencia.get(op_key, 0) == nivel_buscado:
                    return i

        return -1

    def _parentesis_balanceados(self, tokens):
        """Verifica si los paréntesis externos encierran toda la expresión"""
        if not tokens or len(tokens) < 3:
            return False

        if tokens[0].type != 'PARIZQ' or tokens[-1].type != 'PARDER':
            return False

        contador = 1
        for i in range(1, len(tokens) - 1):
            if tokens[i].type == 'PARIZQ':
                contador += 1
            elif tokens[i].type == 'PARDER':
                contador -= 1
                if contador == 0:
                    return False

        return contador == 1

    def _obtener_simbolo_operador(self, token):
        """Convierte el operador a su símbolo"""
        if hasattr(token, 'value') and token.value:
            return str(token.value)

        mapeo = {
            'SUMA': '+', 'RESTA': '-', 'MULT': '*', 'DIV': '/', 'MODULO': '%',
            'MENORQUE': '<', 'MAYORQUE': '>', 'MENORIGUAL': '<=', 'MAYORIGUAL': '>=',
            'IGUAL': '==', 'DISTINTO': '!=', 'AND': '&&', 'OR': '||'
        }
        return mapeo.get(token.type, token.type)

    def obtener_triplos_para_tabla(self):
        """Devuelve los triplos en formato para mostrar en la tabla de la GUI"""
        return [triplo.to_table_row() for triplo in self.triplos]

    def obtener_estadisticas(self):
        """Devuelve estadísticas sobre los triplos generados"""
        total = len(self.triplos)
        operadores = {}
        etiquetas_if = self.contador_if
        etiquetas_for = self.contador_for
        etiquetas_while = self.contador_while
        # suma total, incluyendo las etiquetas 'generales' si las usas en algún punto
        total_etiquetas = etiquetas_if + etiquetas_for + etiquetas_while + self.contador_etiqueta_general

        for triplo in self.triplos:
            op = triplo.operador
            operadores[op] = operadores.get(op, 0) + 1

        return {
            'total_triplos': total,
            'operadores_utilizados': operadores,
            'etiquetas_if_generadas': etiquetas_if,
            'etiquetas_for_generadas': etiquetas_for,
            'etiquetas_while_generadas': etiquetas_while,
            'etiquetas_generadas': total_etiquetas,  # <-- clave esperada por la UI
            'variables_registradas': len(self.variables)
        }

    # Mantener métodos originales para compatibilidad hacia atrás
    def _procesar_tokens_triplos(self, tokens):
        """Método de compatibilidad - redirige al nuevo método optimizado"""
        return self._procesar_tokens_optimizado(tokens)

    def _procesar_expresion_simple(self, tokens):
        """Método de compatibilidad - redirige al nuevo método optimizado"""
        return self._procesar_expresion_optimizada(tokens)

    def _procesar_for_loop(self, tokens, i):
        """Método de compatibilidad - redirige al nuevo método optimizado"""
        return self._procesar_for_optimizado(tokens, i)

    def _procesar_if_statement(self, tokens, i):
        """Método de compatibilidad - redirige al nuevo método optimizado"""
        return self._procesar_if_optimizado(tokens, i)

    def _procesar_println(self, tokens):
        """Método de compatibilidad - redirige al nuevo método optimizado"""
        return self._procesar_print_optimizado(tokens)

    def _buscar_referencia_variable(self, nombre_variable):
        """Método de compatibilidad - redirige al nuevo método optimizado"""
        return self.obtener_referencia_variable(nombre_variable)