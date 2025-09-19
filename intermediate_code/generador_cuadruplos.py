# -*- coding: utf-8 -*-
# intermediate_code/generador_cuadruplos.py

from dataclasses import dataclass
from typing import List, Optional, Union
from lexer.analizador_lexico import construir_lexer


@dataclass
class Cuadruplo:
    """Clase que representa un cuádruplo (índice, operador, arg1, arg2, resultado)"""
    indice: int
    operador: str
    arg1: str
    arg2: str
    resultado: str

    def __str__(self):
        return f"({self.indice}) {self.operador} {self.arg1} {self.arg2} {self.resultado}"

    def to_table_row(self):
        def fmt(v):
            if v is None:
                return "∅"
            v_str = str(v)
            if v_str == "":
                return "∅"
            return v_str

        return [str(self.indice), self.operador, fmt(self.arg1), fmt(self.arg2), fmt(self.resultado)]


class GeneradorCuadruplos:
    """Clase especializada para generar cuádruplos desde código Java"""

    def __init__(self):
        self.cuadruplos: List[Cuadruplo] = []
        self.contador_temp = 0
        self.contador_if = 0
        self.contador_for = 0
        self.contador_while = 0
        self.contador_etiqueta_general = 0
        self.tabla_simbolos = {}  # Para rastrear variables declaradas

    def limpiar(self):
        self.cuadruplos.clear()
        self.contador_temp = 0
        self.contador_if = 0
        self.contador_for = 0
        self.contador_while = 0
        self.contador_etiqueta_general = 0
        self.tabla_simbolos.clear()

    def nuevo_temporal(self) -> str:
        self.contador_temp += 1
        return f"t{self.contador_temp}"

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
        """Genera una nueva etiqueta general (mantener compatibilidad)"""
        self.contador_etiqueta_general += 1
        return f"etiqueta_{self.contador_etiqueta_general}"

    def agregar_cuadruplo(self, operador: str, arg1: str, arg2: str, resultado: str):
        indice = len(self.cuadruplos)
        arg1_norm = str(arg1) if arg1 is not None else ""
        arg2_norm = str(arg2) if arg2 is not None else ""
        resultado_norm = str(resultado) if resultado is not None else ""

        print(f"Agregando cuádruplo {indice}: {operador} | '{arg1_norm}' | '{arg2_norm}' | '{resultado_norm}'")

        cuadruplo = Cuadruplo(indice, operador, arg1_norm, arg2_norm, resultado_norm)
        self.cuadruplos.append(cuadruplo)

    def generar_desde_codigo(self, codigo: str) -> List[Cuadruplo]:
        self.limpiar()

        if not codigo.strip():
            return self.cuadruplos

        try:
            lexer = construir_lexer()
            lexer.input(codigo)
            tokens = []
            while True:
                tok = lexer.token()
                if not tok:
                    break
                tokens.append(tok)

            print(f"Total de tokens encontrados: {len(tokens)}")
            self._procesar_tokens_cuadruplos(tokens)

        except Exception as e:
            print(f"Error generando cuádruplos: {e}")
            import traceback
            traceback.print_exc()

        return self.cuadruplos

    def _procesar_tokens_cuadruplos(self, tokens):
        """Procesa todos los tokens de forma secuencial"""
        i = 0
        while i < len(tokens):
            try:
                # Saltar tokens de estructura de clase y método main
                if self._es_estructura_clase_o_metodo(tokens, i):
                    i = self._saltar_estructura_clase_o_metodo(tokens, i)
                    continue

                # Procesar declaraciones con inicialización
                elif self._es_declaracion_con_inicializacion(tokens, i):
                    i = self._procesar_declaracion_con_inicializacion(tokens, i)

                # Procesar asignaciones simples
                elif self._es_asignacion_simple(tokens, i):
                    i = self._procesar_asignacion_simple(tokens, i)

                # Procesar asignaciones compuestas (+=, *=, etc.)
                elif self._es_asignacion_compuesta(tokens, i):
                    i = self._procesar_asignacion_compuesta(tokens, i)

                # Procesar bucles FOR
                elif tokens[i].type == 'FOR':
                    i = self._procesar_for_completo(tokens, i)

                # Procesar estructuras IF
                elif tokens[i].type == 'IF':
                    i = self._procesar_if_completo(tokens, i)

                # Procesar WHILE
                elif tokens[i].type == 'WHILE':
                    i = self._procesar_while_completo(tokens, i)

                # Procesar System.out.println
                elif self._es_system_out_println(tokens, i):
                    i = self._procesar_system_out_println(tokens, i)

                # Procesar incremento/decremento
                elif self._es_incremento_decremento(tokens, i):
                    i = self._procesar_incremento_decremento(tokens, i)

                else:
                    i += 1

            except Exception as e:
                print(f"Error procesando token en posición {i}: {e}")
                i += 1

    def _es_estructura_clase_o_metodo(self, tokens, i):
        """Detecta estructuras de clase y método main"""
        if i >= len(tokens):
            return False

        # Detectar 'public class'
        if (i + 1 < len(tokens) and
                tokens[i].type == 'PUBLIC' and
                tokens[i + 1].type == 'CLASS'):
            return True

        # Detectar 'public static void main'
        if (i + 3 < len(tokens) and
                tokens[i].type == 'PUBLIC' and
                tokens[i + 1].type == 'STATIC' and
                tokens[i + 2].type == 'VOID' and
                tokens[i + 3].type == 'MAIN'):
            return True

        return False

    def _saltar_estructura_clase_o_metodo(self, tokens, i):
        """Salta la declaración de clase o método hasta encontrar la llave de apertura"""
        while i < len(tokens):
            if tokens[i].type == 'LLAIZQ':
                return i + 1  # Saltar la llave de apertura
            i += 1
        return i

    def _es_declaracion_con_inicializacion(self, tokens, i):
        """Detecta: tipo variable = expresión;"""
        return (i + 3 < len(tokens) and
                tokens[i].type in ['INT', 'DOUBLE', 'FLOAT', 'BOOLEAN', 'STRING'] and
                tokens[i + 1].type == 'IDENTIFICADOR' and
                tokens[i + 2].type == 'ASIGNAR')

    def _procesar_declaracion_con_inicializacion(self, tokens, i):
        """Procesa: int variable = expresión;"""
        tipo = tokens[i].value
        variable = tokens[i + 1].value
        self.tabla_simbolos[variable] = tipo

        print(f"Procesando declaración: {tipo} {variable} = ...")

        i += 3  # Saltar tipo, variable y '='

        # Recoger expresión hasta ';'
        expr_tokens = []
        nivel_parentesis = 0
        while i < len(tokens):
            if tokens[i].type == 'PARIZQ':
                nivel_parentesis += 1
            elif tokens[i].type == 'PARDER':
                nivel_parentesis -= 1
            elif tokens[i].type in ['PUNTOCOMA', 'PUNTOYCOMA'] and nivel_parentesis == 0:
                break
            expr_tokens.append(tokens[i])
            i += 1

        if expr_tokens:
            resultado_expr = self._procesar_expresion_completa(expr_tokens)
            self.agregar_cuadruplo("=", resultado_expr, "", variable)

        # Saltar ';'
        if i < len(tokens) and tokens[i].type in ['PUNTOCOMA', 'PUNTOYCOMA']:
            i += 1

        return i

    def _es_asignacion_simple(self, tokens, i):
        """Detecta: variable = expresión;"""
        return (i + 2 < len(tokens) and
                tokens[i].type == 'IDENTIFICADOR' and
                tokens[i + 1].type == 'ASIGNAR')

    def _procesar_asignacion_simple(self, tokens, i):
        """Procesa: variable = expresión;"""
        variable = tokens[i].value
        print(f"Procesando asignación simple: {variable} = ...")

        i += 2  # Saltar variable y '='

        # Recoger expresión hasta ';'
        expr_tokens = []
        nivel_parentesis = 0
        while i < len(tokens):
            if tokens[i].type == 'PARIZQ':
                nivel_parentesis += 1
            elif tokens[i].type == 'PARDER':
                nivel_parentesis -= 1
            elif tokens[i].type in ['PUNTOCOMA', 'PUNTOYCOMA'] and nivel_parentesis == 0:
                break
            expr_tokens.append(tokens[i])
            i += 1

        if expr_tokens:
            resultado_expr = self._procesar_expresion_completa(expr_tokens)
            self.agregar_cuadruplo("=", resultado_expr, "", variable)

        # Saltar ';'
        if i < len(tokens) and tokens[i].type in ['PUNTOCOMA', 'PUNTOYCOMA']:
            i += 1

        return i

    def _es_asignacion_compuesta(self, tokens, i):
        """Detecta: variable +=, *=, etc."""
        return (i + 2 < len(tokens) and
                tokens[i].type == 'IDENTIFICADOR' and
                tokens[i + 1].type in ['MULTASIGNAR', 'SUMAASIGNAR', 'RESTAASIGNAR', 'DIVASIGNAR'])

    def _procesar_asignacion_compuesta(self, tokens, i):
        """Procesa: variable *= expresión;"""
        variable = tokens[i].value
        operador_compound = tokens[i + 1].type

        print(f"Procesando asignación compuesta: {variable} {tokens[i + 1].value} ...")

        i += 2  # Saltar variable y operador

        # Recoger expresión
        expr_tokens = []
        nivel_parentesis = 0
        while i < len(tokens):
            if tokens[i].type == 'PARIZQ':
                nivel_parentesis += 1
            elif tokens[i].type == 'PARDER':
                nivel_parentesis -= 1
            elif tokens[i].type in ['PUNTOCOMA', 'PUNTOYCOMA'] and nivel_parentesis == 0:
                break
            expr_tokens.append(tokens[i])
            i += 1

        if expr_tokens:
            resultado_expr = self._procesar_expresion_completa(expr_tokens)

            # Mapear operador compuesto a operador básico
            op_map = {
                'MULTASIGNAR': '*', 'SUMAASIGNAR': '+',
                'RESTAASIGNAR': '-', 'DIVASIGNAR': '/'
            }
            op = op_map.get(operador_compound, '*')

            # Generar operación: temp = variable op expresión
            temp_resultado = self.nuevo_temporal()
            self.agregar_cuadruplo(op, variable, resultado_expr, temp_resultado)
            # Asignar resultado a variable: variable = temp
            self.agregar_cuadruplo("=", temp_resultado, "", variable)

        # Saltar ';'
        if i < len(tokens) and tokens[i].type in ['PUNTOCOMA', 'PUNTOYCOMA']:
            i += 1

        return i

    def _procesar_for_completo(self, tokens, i):
        """Procesa un bucle FOR completo: for(init; cond; incr) { cuerpo }"""
        print("Procesando bucle FOR completo...")

        i += 1  # Saltar 'for'

        # Saltar '('
        if i < len(tokens) and tokens[i].type == 'PARIZQ':
            i += 1

        # 1. Procesar inicialización
        init_tokens = []
        while i < len(tokens) and tokens[i].type not in ['PUNTOCOMA', 'PUNTOYCOMA']:
            init_tokens.append(tokens[i])
            i += 1

        if init_tokens:
            print(f"Procesando inicialización FOR: {[t.value for t in init_tokens]}")
            if (len(init_tokens) >= 4 and
                    init_tokens[0].type in ['INT', 'DOUBLE'] and
                    init_tokens[1].type == 'IDENTIFICADOR' and
                    init_tokens[2].type == 'ASIGNAR'):

                tipo = init_tokens[0].value
                variable = init_tokens[1].value
                self.tabla_simbolos[variable] = tipo
                expr_tokens = init_tokens[3:]

                if expr_tokens:
                    resultado_expr = self._procesar_expresion_completa(expr_tokens)
                    self.agregar_cuadruplo("=", resultado_expr, "", variable)

        # Saltar ';' de inicialización
        if i < len(tokens) and tokens[i].type in ['PUNTOCOMA', 'PUNTOYCOMA']:
            i += 1

        # 2. Etiqueta de inicio del bucle
        etiqueta_inicio = self.nueva_etiqueta_for_inicio()
        etiqueta_fin = self.nueva_etiqueta_for_fin()
        self.agregar_cuadruplo("LABEL", "", "", etiqueta_inicio)

        # 3. Procesar condición
        cond_tokens = []
        while i < len(tokens) and tokens[i].type not in ['PUNTOCOMA', 'PUNTOYCOMA']:
            cond_tokens.append(tokens[i])
            i += 1

        if cond_tokens:
            print(f"Procesando condición FOR: {[t.value for t in cond_tokens]}")
            resultado_cond = self._procesar_expresion_completa(cond_tokens)
            self.agregar_cuadruplo("IF_FALSE", resultado_cond, "", etiqueta_fin)

        # Saltar ';' de condición
        if i < len(tokens) and tokens[i].type in ['PUNTOCOMA', 'PUNTOYCOMA']:
            i += 1

        # 4. Recoger tokens de incremento (pero procesar después del cuerpo)
        incr_tokens = []
        nivel_paren = 0
        while i < len(tokens):
            if tokens[i].type == 'PARIZQ':
                nivel_paren += 1
            elif tokens[i].type == 'PARDER':
                if nivel_paren == 0:
                    break
                nivel_paren -= 1
            else:
                incr_tokens.append(tokens[i])
            i += 1

        # Saltar ')' del for
        if i < len(tokens) and tokens[i].type == 'PARDER':
            i += 1

        # 5. Procesar cuerpo del bucle
        if i < len(tokens) and tokens[i].type == 'LLAIZQ':
            i += 1  # Saltar '{'
            nivel_llaves = 1
            cuerpo_tokens = []

            while i < len(tokens) and nivel_llaves > 0:
                if tokens[i].type == 'LLAIZQ':
                    nivel_llaves += 1
                elif tokens[i].type == 'LLADER':
                    nivel_llaves -= 1

                if nivel_llaves > 0:  # Solo agregar si no es la llave de cierre final
                    cuerpo_tokens.append(tokens[i])
                i += 1

            if cuerpo_tokens:
                print(f"Procesando cuerpo FOR: {len(cuerpo_tokens)} tokens")
                self._procesar_tokens_cuadruplos(cuerpo_tokens)

        # 6. Procesar incremento
        if incr_tokens:
            print(f"Procesando incremento FOR: {[t.value for t in incr_tokens]}")
            if len(incr_tokens) == 2 and incr_tokens[1].type == 'INCREMENTO':
                variable_incr = incr_tokens[0].value
                temp_inc = self.nuevo_temporal()
                self.agregar_cuadruplo("+", variable_incr, "1", temp_inc)
                self.agregar_cuadruplo("=", temp_inc, "", variable_incr)
            elif len(incr_tokens) == 2 and incr_tokens[1].type == 'DECREMENTO':
                variable_incr = incr_tokens[0].value
                temp_dec = self.nuevo_temporal()
                self.agregar_cuadruplo("-", variable_incr, "1", temp_dec)
                self.agregar_cuadruplo("=", temp_dec, "", variable_incr)

        # 7. Salto al inicio y etiqueta de fin
        self.agregar_cuadruplo("GOTO", "", "", etiqueta_inicio)
        self.agregar_cuadruplo("LABEL", "", "", etiqueta_fin)

        return i

    def _procesar_if_completo(self, tokens, i):
        """Procesa una estructura IF completa"""
        print("Procesando estructura IF completa...")

        i += 1  # Saltar 'if'

        # Saltar '('
        if i < len(tokens) and tokens[i].type == 'PARIZQ':
            i += 1

        # Procesar condición
        cond_tokens = []
        nivel_paren = 1
        while i < len(tokens) and nivel_paren > 0:
            if tokens[i].type == 'PARIZQ':
                nivel_paren += 1
            elif tokens[i].type == 'PARDER':
                nivel_paren -= 1

            if nivel_paren > 0:
                cond_tokens.append(tokens[i])
            i += 1

        if cond_tokens:
            resultado_cond = self._procesar_expresion_completa(cond_tokens)
            etiqueta_else = self.nueva_etiqueta_if_else()
            etiqueta_fin = self.nueva_etiqueta_if_fin()

            # CORRECCIÓN: Usar los nombres de etiqueta, no convertir a string de otra manera
            self.agregar_cuadruplo("IF_FALSE", resultado_cond, "", etiqueta_else)

            # Procesar bloque if
            if i < len(tokens) and tokens[i].type == 'LLAIZQ':
                i += 1
                nivel_llaves = 1
                if_tokens = []

                while i < len(tokens) and nivel_llaves > 0:
                    if tokens[i].type == 'LLAIZQ':
                        nivel_llaves += 1
                    elif tokens[i].type == 'LLADER':
                        nivel_llaves -= 1

                    if nivel_llaves > 0:
                        if_tokens.append(tokens[i])
                    i += 1

                if if_tokens:
                    self._procesar_tokens_cuadruplos(if_tokens)

            self.agregar_cuadruplo("GOTO", "", "", etiqueta_fin)
            self.agregar_cuadruplo("LABEL", "", "", etiqueta_else)

            # Procesar else si existe
            if i < len(tokens) and tokens[i].type == 'ELSE':
                i += 1
                if i < len(tokens) and tokens[i].type == 'LLAIZQ':
                    i += 1
                    nivel_llaves = 1
                    else_tokens = []

                    while i < len(tokens) and nivel_llaves > 0:
                        if tokens[i].type == 'LLAIZQ':
                            nivel_llaves += 1
                        elif tokens[i].type == 'LLADER':
                            nivel_llaves -= 1

                        if nivel_llaves > 0:
                            else_tokens.append(tokens[i])
                        i += 1

                    if else_tokens:
                        self._procesar_tokens_cuadruplos(else_tokens)

            self.agregar_cuadruplo("LABEL", "", "", etiqueta_fin)

        return i

    def _procesar_while_completo(self, tokens, i):
        """Procesa un bucle WHILE completo"""
        print("Procesando bucle WHILE completo...")

        i += 1  # Saltar 'while'

        etiqueta_inicio = self.nueva_etiqueta_while_inicio()
        etiqueta_fin = self.nueva_etiqueta_while_fin()

        self.agregar_cuadruplo("LABEL", "", "", etiqueta_inicio)

        # Procesar condición
        if i < len(tokens) and tokens[i].type == 'PARIZQ':
            i += 1
            cond_tokens = []
            nivel_paren = 1

            while i < len(tokens) and nivel_paren > 0:
                if tokens[i].type == 'PARIZQ':
                    nivel_paren += 1
                elif tokens[i].type == 'PARDER':
                    nivel_paren -= 1

                if nivel_paren > 0:
                    cond_tokens.append(tokens[i])
                i += 1

            if cond_tokens:
                resultado_cond = self._procesar_expresion_completa(cond_tokens)
                # CORRECCIÓN: Usar el nombre de etiqueta directamente
                self.agregar_cuadruplo("IF_FALSE", resultado_cond, "", etiqueta_fin)

        # Procesar cuerpo
        if i < len(tokens) and tokens[i].type == 'LLAIZQ':
            i += 1
            nivel_llaves = 1
            cuerpo_tokens = []

            while i < len(tokens) and nivel_llaves > 0:
                if tokens[i].type == 'LLAIZQ':
                    nivel_llaves += 1
                elif tokens[i].type == 'LLADER':
                    nivel_llaves -= 1

                if nivel_llaves > 0:
                    cuerpo_tokens.append(tokens[i])
                i += 1

            if cuerpo_tokens:
                self._procesar_tokens_cuadruplos(cuerpo_tokens)

        # CORRECCIÓN: Usar los nombres de etiqueta directamente
        self.agregar_cuadruplo("GOTO", "", "", etiqueta_inicio)
        self.agregar_cuadruplo("LABEL", "", "", etiqueta_fin)

        return i

    def _es_system_out_println(self, tokens, i):
        """Detecta System.out.println"""
        return (i + 4 < len(tokens) and
                tokens[i].type in ['SYSTEM', 'IDENTIFICADOR'] and
                tokens[i].value == 'System' and
                tokens[i + 1].type == 'PUNTO' and
                tokens[i + 2].type in ['OUT', 'IDENTIFICADOR'] and
                tokens[i + 2].value == 'out' and
                tokens[i + 3].type == 'PUNTO' and
                tokens[i + 4].type in ['PRINTLN', 'IDENTIFICADOR'] and
                tokens[i + 4].value == 'println')

    def _procesar_system_out_println(self, tokens, i):
        """Procesa System.out.println(argumentos)"""
        print("Procesando System.out.println...")

        i += 5  # Saltar System.out.println

        if i < len(tokens) and tokens[i].type == 'PARIZQ':
            i += 1
            arg_tokens = []
            nivel_paren = 1

            while i < len(tokens) and nivel_paren > 0:
                if tokens[i].type == 'PARIZQ':
                    nivel_paren += 1
                elif tokens[i].type == 'PARDER':
                    nivel_paren -= 1

                if nivel_paren > 0:
                    arg_tokens.append(tokens[i])
                i += 1

            if arg_tokens:
                argumento = self._procesar_expresion_completa(arg_tokens)
                self.agregar_cuadruplo("PRINT", argumento, "", "")
            else:
                self.agregar_cuadruplo("PRINT", "", "", "")

        # Saltar ';'
        if i < len(tokens) and tokens[i].type in ['PUNTOCOMA', 'PUNTOYCOMA']:
            i += 1

        return i

    def _es_incremento_decremento(self, tokens, i):
        """Detecta i++, ++i, i--, --i"""
        if i + 1 < len(tokens):
            return ((tokens[i].type == 'IDENTIFICADOR' and
                     tokens[i + 1].type in ['INCREMENTO', 'DECREMENTO']) or
                    (tokens[i].type in ['INCREMENTO', 'DECREMENTO'] and
                     tokens[i + 1].type == 'IDENTIFICADOR'))
        return False

    def _procesar_incremento_decremento(self, tokens, i):
        """Procesa incremento/decremento"""
        if tokens[i].type == 'IDENTIFICADOR':
            # Post-incremento: i++
            variable = tokens[i].value
            operador = tokens[i + 1].type
            i += 2
        else:
            # Pre-incremento: ++i
            operador = tokens[i].type
            variable = tokens[i + 1].value
            i += 2

        if operador == 'INCREMENTO':
            temp = self.nuevo_temporal()
            self.agregar_cuadruplo("+", variable, "1", temp)
            self.agregar_cuadruplo("=", temp, "", variable)
        else:  # DECREMENTO
            temp = self.nuevo_temporal()
            self.agregar_cuadruplo("-", variable, "1", temp)
            self.agregar_cuadruplo("=", temp, "", variable)

        return i

    def _procesar_expresion_completa(self, tokens) -> str:
        """Procesa una expresión completa respetando precedencia de operadores"""
        if not tokens:
            return ""

        # Caso simple: un solo token
        if len(tokens) == 1:
            return str(tokens[0].value)

        # Precedencia de operadores (de menor a mayor)
        operadores_precedencia = [
            ['OR', '||'],
            ['AND', '&&'],
            ['IGUAL', 'DISTINTO', '==', '!='],
            ['MENORQUE', 'MAYORQUE', 'MENORIGUAL', 'MAYORIGUAL', '<', '>', '<=', '>='],
            ['SUMA', 'RESTA', '+', '-'],
            ['MULT', 'DIV', 'MODULO', '*', '/', '%']
        ]

        # Procesar por niveles de precedencia (menor a mayor)
        for grupo_ops in operadores_precedencia:
            pos_operador = self._encontrar_operador_principal(tokens, grupo_ops)

            if pos_operador != -1:
                # Dividir expresión
                izq_tokens = tokens[:pos_operador]
                der_tokens = tokens[pos_operador + 1:]

                # Procesar operandos recursivamente
                operando_izq = self._procesar_expresion_completa(izq_tokens) if izq_tokens else ""
                operando_der = self._procesar_expresion_completa(der_tokens) if der_tokens else ""

                # Obtener símbolo del operador
                operador = self._obtener_simbolo_operador(tokens[pos_operador])

                # Generar cuádruplo
                temp_resultado = self.nuevo_temporal()
                self.agregar_cuadruplo(operador, operando_izq, operando_der, temp_resultado)
                return temp_resultado

        # Manejar paréntesis
        if (len(tokens) >= 3 and
                tokens[0].type == 'PARIZQ' and
                tokens[-1].type == 'PARDER' and
                self._parentesis_balanceados(tokens)):
            # Remover paréntesis externos y procesar
            return self._procesar_expresion_completa(tokens[1:-1])

        # Manejar concatenación de strings
        if len(tokens) > 1:
            temp_actual = str(tokens[0].value)
            for i in range(1, len(tokens), 2):
                if i + 1 < len(tokens):
                    operador = tokens[i]
                    operando = tokens[i + 1]
                    if operador.type == 'SUMA' or operador.value == '+':
                        temp_resultado = self.nuevo_temporal()
                        self.agregar_cuadruplo("+", temp_actual, str(operando.value), temp_resultado)
                        temp_actual = temp_resultado
            return temp_actual

        # Caso por defecto: primer token
        return str(tokens[0].value) if tokens else ""

    def _encontrar_operador_principal(self, tokens, grupo_operadores):
        """Encuentra la posición del operador principal (más a la derecha fuera de paréntesis)"""
        nivel_parentesis = 0
        for i in range(len(tokens) - 1, -1, -1):
            token = tokens[i]

            if token.type == 'PARDER':
                nivel_parentesis += 1
            elif token.type == 'PARIZQ':
                nivel_parentesis -= 1
            elif nivel_parentesis == 0:  # Solo operadores fuera de paréntesis
                if token.type in grupo_operadores or (hasattr(token, 'value') and token.value in grupo_operadores):
                    return i

        return -1

    def _parentesis_balanceados(self, tokens):
        """Verifica si los paréntesis están balanceados"""
        contador = 0
        for token in tokens:
            if token.type == 'PARIZQ':
                contador += 1
            elif token.type == 'PARDER':
                contador -= 1
                if contador < 0:
                    return False
        return contador == 0

    def _obtener_simbolo_operador(self, token):
        """Obtiene el símbolo del operador"""
        if hasattr(token, 'value') and token.value:
            return token.value

        mapeo = {
            'SUMA': '+', 'RESTA': '-', 'MULT': '*', 'DIV': '/', 'MODULO': '%',
            'MENORQUE': '<', 'MAYORQUE': '>', 'MENORIGUAL': '<=', 'MAYORIGUAL': '>=',
            'IGUAL': '==', 'DISTINTO': '!=', 'AND': '&&', 'OR': '||'
        }
        return mapeo.get(token.type, token.type)

    def obtener_cuadruplos_para_tabla(self):
        """Retorna los cuádruplos formateados para mostrar en tabla"""
        return [cuadruplo.to_table_row() for cuadruplo in self.cuadruplos]

    def obtener_estadisticas(self):
        """Retorna estadísticas de la generación de cuádruplos"""
        total = len(self.cuadruplos)
        operadores = {}
        temporales = self.contador_temp
        etiquetas_if = self.contador_if
        etiquetas_for = self.contador_for
        etiquetas_while = self.contador_while
        etiquetas_generales = self.contador_etiqueta_general

        for cuadruplo in self.cuadruplos:
            op = cuadruplo.operador
            operadores[op] = operadores.get(op, 0) + 1

        return {
            'total_cuadruplos': total,
            'operadores_utilizados': operadores,
            'temporales_generados': temporales,
            'etiquetas_if_generadas': etiquetas_if,
            'etiquetas_for_generadas': etiquetas_for,
            'etiquetas_while_generadas': etiquetas_while,
            'etiquetas_generales_generadas': etiquetas_generales,
            'variables_declaradas': len(self.tabla_simbolos)
        }

    def generar_codigo_objeto(self):
        """Genera código objeto a partir de los cuádruplos"""
        codigo_objeto = []
        for cuad in self.cuadruplos:
            if cuad.operador == "=":
                codigo_objeto.append(f"LOAD {cuad.arg1}")
                codigo_objeto.append(f"STORE {cuad.resultado}")
            elif cuad.operador in ["+", "-", "*", "/", "%"]:
                codigo_objeto.append(f"LOAD {cuad.arg1}")
                codigo_objeto.append(f"LOAD {cuad.arg2}")
                codigo_objeto.append(f"{cuad.operador.upper()}")
                codigo_objeto.append(f"STORE {cuad.resultado}")
            elif cuad.operador in ["<", ">", "<=", ">=", "==", "!="]:
                codigo_objeto.append(f"LOAD {cuad.arg1}")
                codigo_objeto.append(f"LOAD {cuad.arg2}")
                codigo_objeto.append(f"CMP")
                if cuad.operador == "<":
                    codigo_objeto.append(f"JL {cuad.resultado}")
                elif cuad.operador == ">":
                    codigo_objeto.append(f"JG {cuad.resultado}")
                elif cuad.operador == "<=":
                    codigo_objeto.append(f"JLE {cuad.resultado}")
                elif cuad.operador == ">=":
                    codigo_objeto.append(f"JGE {cuad.resultado}")
                elif cuad.operador == "==":
                    codigo_objeto.append(f"JE {cuad.resultado}")
                elif cuad.operador == "!=":
                    codigo_objeto.append(f"JNE {cuad.resultado}")
            elif cuad.operador == "IF_FALSE":
                codigo_objeto.append(f"LOAD {cuad.arg1}")
                codigo_objeto.append(f"JZ {cuad.resultado}")
            elif cuad.operador == "GOTO":
                codigo_objeto.append(f"JMP {cuad.resultado}")
            elif cuad.operador == "LABEL":
                codigo_objeto.append(f"{cuad.resultado}:")
            elif cuad.operador == "PRINT":
                if cuad.arg1:
                    codigo_objeto.append(f"PRINT {cuad.arg1}")
                else:
                    codigo_objeto.append("PRINT")
            else:
                # Operador desconocido, agregar como comentario
                codigo_objeto.append(f"; {cuad.operador} {cuad.arg1} {cuad.arg2} {cuad.resultado}")
        return codigo_objeto

    def mostrar_cuadruplos(self):
        """Muestra todos los cuádruplos generados en formato legible"""
        print("\n=== CUÁDRUPLOS GENERADOS ===")
        if not self.cuadruplos:
            print("No se generaron cuádruplos.")
            return

        print(f"Total: {len(self.cuadruplos)} cuádruplos")
        print("-" * 50)
        for cuad in self.cuadruplos:
            print(cuad)
        print("-" * 50)

    def obtener_tabla_simbolos(self):
        """Retorna la tabla de símbolos"""
        return self.tabla_simbolos.copy()

    def validar_cuadruplos(self):
        """Valida la consistencia de los cuádruplos generados"""
        errores = []
        variables_definidas = set(self.tabla_simbolos.keys())

        for i, cuad in enumerate(self.cuadruplos):
            # Verificar que las variables usadas estén definidas
            if cuad.arg1 and cuad.arg1.startswith('t') == False and cuad.arg1.isalpha():
                if cuad.arg1 not in variables_definidas and not cuad.arg1.startswith('L'):
                    errores.append(f"Cuádruplo {i}: Variable '{cuad.arg1}' no definida")

            if cuad.arg2 and cuad.arg2.startswith('t') == False and cuad.arg2.isalpha():
                if cuad.arg2 not in variables_definidas and not cuad.arg2.startswith('L'):
                    errores.append(f"Cuádruplo {i}: Variable '{cuad.arg2}' no definida")

            # Si es una asignación, agregar la variable a las definidas
            if cuad.operador == "=" and cuad.resultado and cuad.resultado.startswith('t') == False:
                variables_definidas.add(cuad.resultado)

        return errores