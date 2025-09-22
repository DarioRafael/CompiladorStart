# -*- coding: utf-8 -*-
import ply.yacc as yacc
from lexer.analizador_lexico import tokens
from lexer.analizador_lexico import tabla_simbolos
from lexer.analizador_lexico import construir_lexer

# Resultado del análisis
resultado_gramatica = []

# -----------------------------
# Precedencia de operadores
# -----------------------------
precedence = (
    ('right', 'ASIGNAR', 'SUMAASIGNAR', 'RESTAASIGNAR', 'MULTASIGNAR', 'DIVASIGNAR', 'MODULOASIGNAR'),
    ('left', 'OR'),
    ('left', 'AND'),
    ('left', 'BITOR'),
    ('left', 'BITXOR'),
    ('left', 'BITAND'),
    ('left', 'IGUAL', 'DISTINTO'),
    ('left', 'MENORQUE', 'MAYORQUE', 'MENORIGUAL', 'MAYORIGUAL'),
    ('left', 'BITSHIFTIZQ', 'BITSHIFTDER', 'BITSHIFTDERU'),
    ('left', 'SUMA', 'RESTA'),
    ('left', 'MULT', 'DIV', 'MODULO'),
    ('right', 'NOT', 'BITNOT'),
    ('right', 'INCREMENTO', 'DECREMENTO'),
    ('left', 'PUNTO'),
)

# (Opcional) Seguimiento de alcances si lo necesitas más adelante
alcance_actual = []
variables_declaradas = {}


# =========================
#  Auxiliares de símbolos
# =========================
def verificar_variable_existe(nombre):
    """Verifica si una variable existe en la tabla de símbolos considerando todos los alcances."""
    if f"local.{nombre}" in tabla_simbolos.simbolos:
        return True
    if f"main.{nombre}" in tabla_simbolos.simbolos:
        return True
    if nombre in tabla_simbolos.simbolos:
        return True
    return False


def marcar_variable_usada(nombre):
    """Marca una variable como usada buscando en todos los alcances."""
    if f"local.{nombre}" in tabla_simbolos.simbolos:
        tabla_simbolos.simbolos[f"local.{nombre}"]['usado'] = True
        return True
    if f"main.{nombre}" in tabla_simbolos.simbolos:
        tabla_simbolos.simbolos[f"main.{nombre}"]['usado'] = True
        return True
    if nombre in tabla_simbolos.simbolos:
        tabla_simbolos.simbolos[nombre]['usado'] = True
        return True
    return False


# =========================
#  Gramática
# =========================
def p_programa(p):
    'programa : codigo'
    if len(resultado_gramatica) == 0:
        resultado_gramatica.append(
            "<span style='font-size:20px; color:lime;'>✅ Análisis sintáctico finalizado sin errores</span>"
        )


def p_codigo(p):
    '''codigo : declaracion_clase
              | empty'''
    p[0] = "Código Java válido"


def p_declaracion_clase(p):
    '''declaracion_clase : PUBLIC CLASS IDENTIFICADOR LLAIZQ contenido_clase LLADER
                         | CLASS IDENTIFICADOR LLAIZQ contenido_clase LLADER'''
    p[0] = "Declaración de clase válida"


def p_contenido_clase(p):
    '''contenido_clase : declaracion_metodo
                       | declaracion_atributo
                       | contenido_clase declaracion_metodo
                       | contenido_clase declaracion_atributo
                       | empty'''
    p[0] = "Contenido de clase válido"


def p_declaracion_atributo(p):
    '''declaracion_atributo : modificador tipo IDENTIFICADOR PUNTOCOMA
                            | modificador tipo IDENTIFICADOR ASIGNAR expresion PUNTOCOMA'''
    p[0] = "Declaración de atributo válida"


def p_modificador(p):
    '''modificador : PUBLIC
                   | PRIVATE
                   | PROTECTED
                   | PUBLIC STATIC
                   | PRIVATE STATIC
                   | PROTECTED STATIC
                   | STATIC
                   | empty'''
    p[0] = p[1] if len(p) > 1 else "default"


def p_declaracion_metodo(p):
    '''declaracion_metodo : modificador tipo IDENTIFICADOR PARIZQ parametros PARDER LLAIZQ sentencias LLADER
                          | modificador VOID IDENTIFICADOR PARIZQ parametros PARDER LLAIZQ sentencias LLADER
                          | modificador tipo IDENTIFICADOR PARIZQ PARDER LLAIZQ sentencias LLADER
                          | modificador VOID IDENTIFICADOR PARIZQ PARDER LLAIZQ sentencias LLADER
                          | modificador tipo MAIN PARIZQ STRING CORIZQ CORDER IDENTIFICADOR PARDER LLAIZQ sentencias LLADER
                          | modificador VOID MAIN PARIZQ STRING CORIZQ CORDER IDENTIFICADOR PARDER LLAIZQ sentencias LLADER'''
    p[0] = "Declaración de método válida"


def p_parametros(p):
    '''parametros : tipo IDENTIFICADOR
                  | parametros COMA tipo IDENTIFICADOR
                  | STRING CORIZQ CORDER IDENTIFICADOR
                  | empty'''
    p[0] = "Parámetros válidos"


def p_tipo(p):
    '''tipo : INT
            | BOOLEAN
            | CHAR
            | BYTE
            | SHORT
            | LONG
            | FLOAT
            | DOUBLE
            | STRING
            | IDENTIFICADOR'''
    p[0] = p[1]


def p_sentencias(p):
    '''sentencias : sentencia
                  | sentencias sentencia
                  | empty'''
    p[0] = "Sentencias válidas"


def p_sentencia(p):
    '''sentencia : declaracion_variable PUNTOCOMA
                 | asignacion PUNTOCOMA
                 | if_sentencia
                 | for_sentencia
                 | while_sentencia
                 | do_while_sentencia PUNTOCOMA
                 | switch_sentencia
                 | llamada_metodo PUNTOCOMA
                 | llamada_system PUNTOCOMA
                 | incremento_decremento PUNTOCOMA
                 | return_sentencia PUNTOCOMA
                 | PUNTOCOMA
                 | LLAIZQ sentencias LLADER'''
    p[0] = "Sentencia válida"


def p_declaracion_variable(p):
    '''declaracion_variable : tipo IDENTIFICADOR
                            | tipo IDENTIFICADOR ASIGNAR expresion
                            | tipo IDENTIFICADOR CORIZQ CORDER
                            | tipo IDENTIFICADOR CORIZQ CORDER ASIGNAR NEW tipo CORIZQ expresion CORDER
                            | tipo IDENTIFICADOR CORIZQ CORDER ASIGNAR LLAIZQ lista_expresiones LLADER
                            | tipo IDENTIFICADOR CORIZQ expresion CORDER'''
    # Validación de tipo legible (los tokens de tipo traen el lexema en minúsculas)
    tipos_validos = ['int', 'boolean', 'char', 'byte', 'short', 'long', 'float', 'double', 'String']
    if p[1] not in tipos_validos:
        resultado_gramatica.append(
            f"<span style='color:red; font-size:20px; font-weight:bold;'>Error de sintaxis en línea {p.lineno(1)}: Tipo de variable no válido '{p[1]}'</span>"
        )
    p[0] = "Declaración de variable válida"


def p_lista_expresiones(p):
    '''lista_expresiones : expresion
                        | lista_expresiones COMA expresion
                        | empty'''
    p[0] = "Lista de expresiones válida"


def p_asignacion(p):
    '''asignacion : IDENTIFICADOR ASIGNAR expresion
                  | IDENTIFICADOR CORIZQ expresion CORDER ASIGNAR expresion
                  | IDENTIFICADOR SUMAASIGNAR expresion
                  | IDENTIFICADOR RESTAASIGNAR expresion
                  | IDENTIFICADOR MULTASIGNAR expresion
                  | IDENTIFICADOR DIVASIGNAR expresion
                  | IDENTIFICADOR MODULOASIGNAR expresion'''
    nombre = p[1]
    if not verificar_variable_existe(nombre):
        resultado_gramatica.append(f"<span style='font-size:20px; color:#FF6B68;'>Error en línea {p.lineno(1)}: Variable '{nombre}' no declarada</span>")
    else:
        marcar_variable_usada(nombre)
    p[0] = f"Asignación válida a {nombre}"


def p_incremento_decremento(p):
    '''incremento_decremento : IDENTIFICADOR INCREMENTO
                             | IDENTIFICADOR DECREMENTO
                             | INCREMENTO IDENTIFICADOR
                             | DECREMENTO IDENTIFICADOR'''
    nombre = p[2] if p[1] in ('++', '--') else p[1]
    if not verificar_variable_existe(nombre):
        resultado_gramatica.append(f"<span style='font-size:20px; color:#FF6B68;'>Error en línea {p.lineno(1)}: Variable '{nombre}' no declarada</span>")
    else:
        marcar_variable_usada(nombre)
    p[0] = f"Incremento/decremento válido de {nombre}"


def p_if_sentencia(p):
    '''if_sentencia : IF PARIZQ expresion PARDER sentencia
                    | IF PARIZQ expresion PARDER sentencia ELSE sentencia
                    | IF PARIZQ expresion PARDER LLAIZQ sentencias LLADER
                    | IF PARIZQ expresion PARDER LLAIZQ sentencias LLADER ELSE LLAIZQ sentencias LLADER
                    | IF PARIZQ expresion PARDER LLAIZQ sentencias LLADER ELSE sentencia'''
    p[0] = "Sentencia if válida"


def p_for_sentencia(p):
    '''for_sentencia : FOR PARIZQ declaracion_variable PUNTOCOMA expresion PUNTOCOMA expresion PARDER sentencia
                     | FOR PARIZQ declaracion_variable PUNTOCOMA expresion PUNTOCOMA expresion PARDER LLAIZQ sentencias LLADER
                     | FOR PARIZQ asignacion PUNTOCOMA expresion PUNTOCOMA expresion PARDER sentencia
                     | FOR PARIZQ asignacion PUNTOCOMA expresion PUNTOCOMA expresion PARDER LLAIZQ sentencias LLADER
                     | FOR PARIZQ declaracion_variable PUNTOCOMA expresion PUNTOCOMA incremento_decremento PARDER sentencia
                     | FOR PARIZQ declaracion_variable PUNTOCOMA expresion PUNTOCOMA incremento_decremento PARDER LLAIZQ sentencias LLADER
                     | FOR PARIZQ PUNTOCOMA expresion PUNTOCOMA expresion PARDER sentencia
                     | FOR PARIZQ PUNTOCOMA expresion PUNTOCOMA expresion PARDER LLAIZQ sentencias LLADER
                     | FOR PARIZQ PUNTOCOMA PUNTOCOMA PARDER sentencia
                     | FOR PARIZQ PUNTOCOMA PUNTOCOMA PARDER LLAIZQ sentencias LLADER'''
    p[0] = "Sentencia for válida"


def p_while_sentencia(p):
    '''while_sentencia : WHILE PARIZQ expresion PARDER sentencia
                       | WHILE PARIZQ expresion PARDER LLAIZQ sentencias LLADER'''
    p[0] = "Sentencia while válida"


def p_do_while_sentencia(p):
    '''do_while_sentencia : DO LLAIZQ sentencias LLADER WHILE PARIZQ expresion PARDER'''
    p[0] = "Sentencia do-while válida"


def p_switch_sentencia(p):
    '''switch_sentencia : SWITCH PARIZQ expresion PARDER LLAIZQ casos_switch LLADER'''
    p[0] = "Sentencia switch válida"


def p_casos_switch(p):
    '''casos_switch : caso_switch
                    | casos_switch caso_switch
                    | empty'''
    p[0] = "Casos switch válidos"


def p_caso_switch(p):
    '''caso_switch : CASE expresion DOSPUNTOS sentencias
                   | DEFAULT DOSPUNTOS sentencias'''
    p[0] = "Caso switch válido"


def p_llamada_metodo(p):
    '''llamada_metodo : IDENTIFICADOR PARIZQ argumentos PARDER
                      | IDENTIFICADOR PARIZQ PARDER'''
    nombre = p[1]
    if not verificar_variable_existe(nombre):
        resultado_gramatica.append(f"<span style='font-size:20px; color:#FF6B68;'>Error en línea {p.lineno(1)}: Método '{nombre}' no declarado</span>")
    else:
        marcar_variable_usada(nombre)
    p[0] = f"Llamada válida al método {nombre}"


def p_argumentos(p):
    '''argumentos : expresion
                  | argumentos COMA expresion
                  | empty'''
    p[0] = "Argumentos válidos"


def p_llamada_system(p):
    '''llamada_system : SYSTEM PUNTO OUT PUNTO PRINTLN PARIZQ expresion PARDER
                      | SYSTEM PUNTO OUT PUNTO PRINT PARIZQ expresion PARDER
                      | SYSTEM PUNTO OUT PUNTO PRINTLN PARIZQ PARDER
                      | SYSTEM PUNTO OUT PUNTO PRINT PARIZQ PARDER'''
    p[0] = "Llamada a System.out válida"


def p_return_sentencia(p):
    '''return_sentencia : RETURN
                        | RETURN expresion'''
    p[0] = "Sentencia return válida"


def p_expresion(p):
    '''expresion : expresion_primaria
                 | expresion SUMA expresion
                 | expresion RESTA expresion
                 | expresion MULT expresion
                 | expresion DIV expresion
                 | expresion MODULO expresion
                 | expresion MENORQUE expresion
                 | expresion MAYORQUE expresion
                 | expresion MENORIGUAL expresion
                 | expresion MAYORIGUAL expresion
                 | expresion IGUAL expresion
                 | expresion DISTINTO expresion
                 | expresion AND expresion
                 | expresion OR expresion
                 | expresion BITAND expresion
                 | expresion BITOR expresion
                 | expresion BITXOR expresion
                 | expresion BITSHIFTIZQ expresion
                 | expresion BITSHIFTDER expresion
                 | expresion BITSHIFTDERU expresion
                 | NOT expresion
                 | BITNOT expresion
                 | RESTA expresion %prec NOT
                 | PARIZQ expresion PARDER
                 | PARIZQ tipo PARDER expresion
                 | IDENTIFICADOR CORIZQ expresion CORDER
                 | NEW tipo PARIZQ argumentos PARDER
                 | NEW tipo PARIZQ PARDER
                 | NEW tipo CORIZQ expresion CORDER
                 | incremento_decremento'''
    p[0] = "Expresión válida"


def p_expresion_primaria(p):
    '''expresion_primaria : IDENTIFICADOR
                          | ENTERO
                          | DECIMAL
                          | CADENA
                          | CARACTER
                          | TRUE
                          | FALSE
                          | NULL
                          | llamada_metodo
                          | IDENTIFICADOR PUNTO IDENTIFICADOR'''
    if p.slice[1].type == 'IDENTIFICADOR':
        nombre = p[1]
        if nombre not in ['true', 'false', 'null']:
            if not verificar_variable_existe(nombre):
                resultado_gramatica.append(f"<span style='font-size:20px; color:#FF6B68;'>Error en línea {p.lineno(1)}: Variable '{nombre}' no declarada</span>")
            else:
                marcar_variable_usada(nombre)
    p[0] = p[1]


def p_empty(p):
    'empty :'
    pass


# =========================
# Manejo de errores (PANIC MODE)
# =========================
def p_error(p):
    """
    Recolecta múltiples errores:
    - Reporta el error actual
    - Entra en 'panic mode' y descarta tokens hasta un sincronizador ( ; ) } )
    - Llama a parser.errok() para poder continuar
    """
    if not p:
        resultado_gramatica.append(
            "<span style='font-size:20px; color:#FF6B68;'>Error de sintaxis: fin de archivo inesperado</span>"
        )
        return

    # Mensaje base
    if p.type == 'IDENTIFICADOR':
        msg = f"'{p.value}' podría necesitar ser declarado primero"
    elif p.type in ('CORDER', 'CORIZQ'):
        msg = "Uso incorrecto de corchetes '[]'"
    elif p.type in ('PARDER', 'PARIZQ'):
        msg = "Desbalance de paréntesis '()'"
    elif p.type in ('LLADER', 'LLAIZQ'):
        msg = "Desbalance de llaves '{}'"
    elif p.type == 'PUNTOCOMA':
        msg = "Punto y coma ';' inesperado o faltante"
    else:
        msg = f"Token inesperado '{p.value}' de tipo {p.type}"

    resultado_gramatica.append(
        f"<span style='font-size:20px; color:#FF6B68;'>Error de sintaxis en línea {p.lineno}: {msg}</span>"
    )

    # --- Panic mode: descartar hasta token seguro ---
    # Importante: esto permite seguir acumulando más errores
    parser.errok()  # limpia el estado de error
    # Consumir tokens hasta un sincronizador; si no hay más, salimos
    while True:
        tok = parser.token()
        if not tok:
            break
        if tok.type in ('PUNTOCOMA', 'PARDER', 'LLADER'):
            # Punto de sincronización encontrado: paramos aquí.
            break





# =========================
# Construcción del parser (UNA VEZ)
# =========================
# Usamos NullLogger para evitar spam en consola; write_tables=False para no crear archivos .py
parser = yacc.yacc(errorlog=yacc.NullLogger(), write_tables=False, debug=False)


# =========================
# API de análisis
# =========================
def prueba_sintactica(data):
    """
    Analiza el código y retorna la lista de mensajes (errores/advertencias/ok).
    NOTA: ya NO reconstruimos el parser aquí; reutilizamos el global.
    """
    global resultado_gramatica

    lexer = construir_lexer()
    lexer.lineno = 1

    resultado_gramatica.clear()
    tabla_simbolos.limpiar()

    if not data.strip():
        resultado_gramatica.append("No hay código para analizar")
        return resultado_gramatica

    try:
        # chequeo mínimo de "class"
        if "class" not in data and "Class" not in data:
            resultado_gramatica.append(
                "<span style='font-size:20px; color:#FF6B68;'>Error: El código no parece ser un programa Java válido. Debe contener una clase.</span>"
            )
            return resultado_gramatica

        # Ejecutar el parser (tracking para líneas/cols más precisas si amplías)
        result = parser.parse(data, lexer=lexer, tracking=True)
        if result:
            resultado_gramatica.append(result)

        # Advertencias: variables sin usar
        variables_sin_usar = []
        for nombre_completo, info in tabla_simbolos.simbolos.items():
            if (info['tipo'] not in ['CLASS', 'METHOD'] and
                not info.get('usado', False) and
                'args' not in nombre_completo):
                nombre_simple = nombre_completo.split('.')[-1] if '.' in nombre_completo else nombre_completo
                variables_sin_usar.append((nombre_simple, info))

        for nombre, info in variables_sin_usar:
            resultado_gramatica.append(
                f"<span style='font-size:20px; color:#FFA500;'>Advertencia: Variable '{nombre}' declarada en línea {info['linea']} pero no utilizada</span>"
            )

    except Exception as e:
        resultado_gramatica.append(
            f"<span style='font-size:20px; color:#FF6B68;'>Error durante el análisis: {str(e)}</span>"
        )

    return resultado_gramatica


if __name__ == '__main__':
    while True:
        try:
            s = input('Ingrese código Java >>> ')
            if not s.strip():
                continue
            resultados = prueba_sintactica(s)
            for r in resultados:
                print(r)
        except EOFError:
            break
