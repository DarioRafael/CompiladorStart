import ply.yacc as yacc
from analizador_lexico import tokens, analizador

# Resultado del análisis
resultado_gramatica = []

# Definir precedencia de operadores simplificada
precedence = (
    ('right', 'ASIGNAR'),
    ('left', 'OR'),
    ('left', 'AND'),
    ('left', 'IGUAL', 'DISTINTO'),
    ('left', 'MENORQUE', 'MAYORQUE', 'MENORIGUAL', 'MAYORIGUAL'),
    ('left', 'SUMA', 'RESTA'),
    ('left', 'MULT', 'DIV', 'MODULO'),
    ('right', 'NOT'),
    ('right', 'INCREMENTO', 'DECREMENTO'),
    ('left', 'PUNTO'),
)


def p_programa(p):
    'programa : codigo'
    p[0] = "Programa Java analizado correctamente"


def p_codigo(p):
    '''codigo : declaracion_clase
              | empty'''
    p[0] = "Código Java válido"


def p_declaracion_clase(p):
    '''declaracion_clase : PUBLIC CLASS IDENTIFICADOR LLAIZQ contenido_clase LLADER'''
    p[0] = "Declaración de clase válida"


def p_contenido_clase(p):
    '''contenido_clase : declaracion_metodo
                       | contenido_clase declaracion_metodo
                       | empty'''
    p[0] = "Contenido de clase válido"


def p_declaracion_metodo(p):
    '''declaracion_metodo : PUBLIC STATIC VOID IDENTIFICADOR PARIZQ argumentos PARDER LLAIZQ sentencias LLADER
                          | PUBLIC STATIC tipo IDENTIFICADOR PARIZQ argumentos PARDER LLAIZQ sentencias LLADER
                          | PUBLIC STATIC tipo IDENTIFICADOR PARIZQ PARDER LLAIZQ sentencias LLADER
                          | PUBLIC STATIC VOID IDENTIFICADOR PARIZQ PARDER LLAIZQ sentencias LLADER'''
    p[0] = "Declaración de método válida"


def p_argumentos(p):
    '''argumentos : tipo IDENTIFICADOR
                  | argumentos COMA tipo IDENTIFICADOR
                  | tipo IDENTIFICADOR CORIZQ CORDER
                  | STRING CORIZQ CORDER IDENTIFICADOR
                  | empty'''
    p[0] = "Argumentos válidos"


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
    p[0] = "Tipo válido"


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
                 | llamada_system PUNTOCOMA
                 | incremento_decremento PUNTOCOMA
                 | PUNTOCOMA
                 | LLAIZQ sentencias LLADER'''
    p[0] = "Sentencia válida"


def p_declaracion_variable(p):
    '''declaracion_variable : tipo IDENTIFICADOR
                            | tipo IDENTIFICADOR ASIGNAR expresion
                            | tipo IDENTIFICADOR CORIZQ CORDER
                            | tipo IDENTIFICADOR CORIZQ expresion CORDER'''
    p[0] = "Declaración de variable válida"


def p_asignacion(p):
    '''asignacion : IDENTIFICADOR ASIGNAR expresion
                  | IDENTIFICADOR CORIZQ expresion CORDER ASIGNAR expresion'''
    p[0] = "Asignación válida"


def p_incremento_decremento(p):
    '''incremento_decremento : IDENTIFICADOR INCREMENTO
                             | IDENTIFICADOR DECREMENTO
                             | INCREMENTO IDENTIFICADOR
                             | DECREMENTO IDENTIFICADOR'''
    p[0] = "Incremento/decremento válido"


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
                     | FOR PARIZQ declaracion_variable PUNTOCOMA expresion PUNTOCOMA incremento_decremento PARDER sentencia
                     | FOR PARIZQ declaracion_variable PUNTOCOMA expresion PUNTOCOMA incremento_decremento PARDER LLAIZQ sentencias LLADER'''
    p[0] = "Sentencia for válida"


def p_while_sentencia(p):
    '''while_sentencia : WHILE PARIZQ expresion PARDER sentencia
                       | WHILE PARIZQ expresion PARDER LLAIZQ sentencias LLADER'''
    p[0] = "Sentencia while válida"


def p_llamada_system(p):
    '''llamada_system : SYSTEM PUNTO OUT PUNTO PRINTLN PARIZQ expresion PARDER
                      | SYSTEM PUNTO OUT PUNTO PRINT PARIZQ expresion PARDER
                      | SYSTEM PUNTO OUT PUNTO PRINTLN PARIZQ PARDER
                      | SYSTEM PUNTO OUT PUNTO PRINT PARIZQ PARDER'''
    p[0] = "Llamada a System.out válida"


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
                 | NOT expresion
                 | RESTA expresion
                 | PARIZQ expresion PARDER
                 | PARIZQ tipo PARDER expresion
                 | IDENTIFICADOR CORIZQ expresion CORDER'''
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
                          | IDENTIFICADOR PARIZQ expresion PARDER
                          | IDENTIFICADOR PARIZQ PARDER
                          | IDENTIFICADOR PUNTO IDENTIFICADOR'''
    p[0] = "Expresión primaria válida"


def p_empty(p):
    'empty :'
    pass


# Manejo de errores mejorado para main
def p_error(p):
    global resultado_gramatica

    # Si no hay token, podría ser el final del archivo
    if not p:
        error = "Error de sintaxis al final del archivo"
        resultado_gramatica.append(error)
        return

    # Si estamos procesando la declaración de main, ignorar errores de corchetes
    linea_actual = p.lexer.lineno
    data = p.lexer.lexdata.split('\n')

    # Buscar si estamos en una línea que contiene "main" y "String[]"
    for i, line in enumerate(data):
        if i + 1 == linea_actual and "main" in line and ("String[]" in line or "String [ ]" in line):
            # Estamos en la declaración de main, ignorar errores de CORIZQ/CORDER
            if p.type in ('CORIZQ', 'CORDER'):
                parser.errok()
                return

    # Para otros errores, dar un mensaje descriptivo
    if p.type == 'IDENTIFICADOR' and not p.value.startswith('"') and not p.value.startswith("'"):
        error = f"Error de sintaxis en línea {p.lineno}: '{p.value}' podría necesitar comillas o no está declarado"
    elif p.type in ('CORDER', 'CORIZQ'):
        error = f"Error de sintaxis en línea {p.lineno}: Uso incorrecto de corchetes '[]'"
    elif p.type in ('PARDER', 'PARIZQ'):
        error = f"Error de sintaxis en línea {p.lineno}: Desbalance de paréntesis '()'"
    elif p.type in ('LLADER', 'LLAIZQ'):
        error = f"Error de sintaxis en línea {p.lineno}: Desbalance de llaves '{{}}'"
    else:
        error = f"Error de sintaxis en línea {p.lineno}: Token inesperado '{p.value}' de tipo {p.type}"

    resultado_gramatica.append(error)
    parser.errok()  # Intentar recuperarse para continuar el análisis


# Inicializar el analizador sintáctico
parser = yacc.yacc()


# Función para analizar un código fuente completo
def prueba_sintactica(data):
    global resultado_gramatica
    resultado_gramatica.clear()

    if not data.strip():
        resultado_gramatica.append("No hay código para analizar")
        return resultado_gramatica

    try:
        # Verificar caso especial: método main con argumentos String[]
        if "main" in data and "String[]" in data:
            # Tratar de manera especial - no hacer nada particular, solo verificar
            pass

        # Verificar que sea código Java válido
        if "class" not in data or "public" not in data:
            resultado_gramatica.append("Error: El código no parece ser un programa Java válido")
            return resultado_gramatica

        # Verificar balanceo de paréntesis, llaves, etc.
        contadores = {'(': 0, ')': 0, '{': 0, '}': 0, '"': 0, "'": 0}
        for char in data:
            if char in contadores:
                contadores[char] += 1

        # Verificar balanceo (excluyendo corchetes que son especiales)
        if contadores['('] != contadores[')']:
            resultado_gramatica.append(
                f"Error: Desbalance de paréntesis - {contadores['(']} abiertos y {contadores[')']} cerrados")
        if contadores['{'] != contadores['}']:
            resultado_gramatica.append(
                f"Error: Desbalance de llaves - {contadores['{']} abiertas y {contadores['}']} cerradas")
        if contadores['"'] % 2 != 0:
            resultado_gramatica.append(f"Error: Número impar de comillas dobles (\") - posible cadena no cerrada")
        if contadores["'"] % 2 != 0:
            resultado_gramatica.append(f"Error: Número impar de comillas simples (') - posible carácter no cerrado")

        # Verificar System.out.print sin comillas o punto y coma
        if "System.out.print" in data:
            for line in data.split('\n'):
                if "System.out.print" in line and not line.strip().endswith(";"):
                    resultado_gramatica.append(f"Error: Línea con System.out.print sin punto y coma: {line.strip()}")

                if "System.out.print" in line and not ('"' in line or "'" in line):
                    if "System.out.println()" not in line and "System.out.print()" not in line:
                        # Verificar si hay un identificador sin comillas después del print
                        if "print" in line and "(" in line and ")" in line:
                            content = line.split("(")[1].split(")")[0].strip()
                            if content and not (content.startswith('"') or content.startswith("'") or
                                                content.isdigit() or content in ["true", "false", "null"]):
                                resultado_gramatica.append(
                                    f"Error: Posible llamada a System.out.print sin cadena entre comillas: {line.strip()}")

        # Analizar el código
        result = parser.parse(data)
        if result:
            resultado_gramatica.append(result)

    except Exception as e:
        resultado_gramatica.append(f"Error durante el análisis: {str(e)}")

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