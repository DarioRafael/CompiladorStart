import ply.yacc as yacc
from analizador_lexico import tokens, tabla_simbolos
from analizador_lexico import construir_lexer

import ply.lex as lex  # Añade esta línea

# Resultado del análisis
resultado_gramatica = []


# Definir precedencia de operadores
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

# Variables para seguimiento del programa
alcance_actual = []  # Pila para seguimiento de alcances
variables_declaradas = {}  # Diccionario para seguimiento de variables


def p_programa(p):
    'programa : codigo'
    if len(resultado_gramatica) == 0:
        resultado_gramatica.append("Programa Java analizado correctamente")


def p_codigo(p):
    '''codigo : declaracion_clase
              | empty'''
    p[0] = "Código Java válido"


def p_declaracion_clase(p):
    '''declaracion_clase : PUBLIC CLASS IDENTIFICADOR LLAIZQ contenido_clase LLADER
                         | CLASS IDENTIFICADOR LLAIZQ contenido_clase LLADER'''
    # Registrar la clase en la tabla de símbolos
    if len(p) == 7:  # Con PUBLIC
        tabla_simbolos.agregar(p[3], 'CLASS', p.lineno(3))
    else:  # Sin PUBLIC
        tabla_simbolos.agregar(p[2], 'CLASS', p.lineno(2))

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
    # Registrar la variable en la tabla de símbolos
    nombre = p[3]
    tipo = p[2]
    linea = p.lineno(3)

    if len(p) == 7:  # Con asignación
        valor = p[5]
    else:  # Sin asignación
        valor = None

    tabla_simbolos.agregar(nombre, tipo, linea, valor)
    p[0] = f"Declaración de atributo válida: {tipo} {nombre}"


def p_modificador(p):
    '''modificador : PUBLIC
                   | PRIVATE
                   | PROTECTED
                   | PUBLIC STATIC
                   | PRIVATE STATIC
                   | PROTECTED STATIC
                   | STATIC
                   | empty'''
    if len(p) > 1:
        p[0] = p[1]
    else:
        p[0] = "default"


def p_declaracion_metodo(p):
    '''declaracion_metodo : modificador tipo IDENTIFICADOR PARIZQ parametros PARDER LLAIZQ sentencias LLADER
                          | modificador VOID IDENTIFICADOR PARIZQ parametros PARDER LLAIZQ sentencias LLADER
                          | modificador tipo IDENTIFICADOR PARIZQ PARDER LLAIZQ sentencias LLADER
                          | modificador VOID IDENTIFICADOR PARIZQ PARDER LLAIZQ sentencias LLADER
                          | modificador tipo MAIN PARIZQ STRING CORIZQ CORDER IDENTIFICADOR PARDER LLAIZQ sentencias LLADER
                          | modificador VOID MAIN PARIZQ STRING CORIZQ CORDER IDENTIFICADOR PARDER LLAIZQ sentencias LLADER'''
    # Detectar si es el método main
    if len(p) >= 7 and p[3] == 'main':
        tabla_simbolos.agregar('main', 'METHOD', p.lineno(3))
        p[0] = "Declaración de método main válida"
    else:
        # Registrar el método en la tabla de símbolos
        tipo_retorno = p[2]
        nombre = p[3]
        linea = p.lineno(3)
        tabla_simbolos.agregar(nombre, 'METHOD', linea)
        p[0] = f"Declaración de método válida: {tipo_retorno} {nombre}"


def p_parametros(p):
    '''parametros : tipo IDENTIFICADOR
                  | parametros COMA tipo IDENTIFICADOR
                  | STRING CORIZQ CORDER IDENTIFICADOR
                  | empty'''
    # Registrar los parámetros como variables
    if len(p) == 3:  # tipo IDENTIFICADOR
        tabla_simbolos.agregar(p[2], p[1], p.lineno(2))
    elif len(p) == 5 and p[1] != 'String':  # parametros COMA tipo IDENTIFICADOR
        tabla_simbolos.agregar(p[4], p[3], p.lineno(4))
    elif len(p) == 5:  # STRING CORIZQ CORDER IDENTIFICADOR
        tabla_simbolos.agregar(p[4], 'String[]', p.lineno(4))

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
    # Registrar la variable en la tabla de símbolos
    nombre = p[2]
    tipo = p[1]
    linea = p.lineno(2)

    if len(p) == 5 or len(p) > 5:  # Es un array
        tipo = f"{tipo}[]"

    if len(p) == 5 and p[3] == 'ASIGNAR':  # Con asignación simple
        valor = p[4]
    else:
        valor = None

    tabla_simbolos.agregar(nombre, tipo, linea, valor)
    p[0] = f"Declaración de variable válida: {tipo} {nombre}"


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
    # Verificar que la variable esté declarada
    nombre = p[1]
    if not tabla_simbolos.existe(nombre):
        resultado_gramatica.append(f"Error en línea {p.lineno(1)}: Variable '{nombre}' no declarada")
    else:
        tabla_simbolos.marcar_como_usado(nombre)

    p[0] = f"Asignación válida a {nombre}"


def p_incremento_decremento(p):
    '''incremento_decremento : IDENTIFICADOR INCREMENTO
                             | IDENTIFICADOR DECREMENTO
                             | INCREMENTO IDENTIFICADOR
                             | DECREMENTO IDENTIFICADOR'''
    # Verificar que la variable esté declarada
    if p[1] == '++' or p[1] == '--':
        nombre = p[2]
    else:
        nombre = p[1]

    if not tabla_simbolos.existe(nombre):
        resultado_gramatica.append(f"Error en línea {p.lineno(1)}: Variable '{nombre}' no declarada")
    else:
        tabla_simbolos.marcar_como_usado(nombre)

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
    # Verificar que el método esté declarado
    nombre = p[1]
    if not tabla_simbolos.existe(nombre):
        resultado_gramatica.append(f"Error en línea {p.lineno(1)}: Método '{nombre}' no declarado")
    else:
        tabla_simbolos.marcar_como_usado(nombre)

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
    # Aquí NO verificamos si una expresión es un identificador porque podría ser una cadena concatenada
    # Las verificaciones específicas las hacemos en expresión_primaria
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
    # Verificar solo si es un identificador simple, no una cadena o un literal
    if isinstance(p[1], str) and p[1] not in ['true', 'false', 'null'] and not isinstance(p[1], (int, float)):
        # Mejor comprobación para cadenas - verificar si el valor es una cadena ya tokenizada
        if p.slice[1].type == 'IDENTIFICADOR':
            nombre = p[1]
            if not tabla_simbolos.existe(nombre):
                # Solo reportar error si es realmente un identificador y no está declarado
                if nombre != '+' and p.slice[1].type == 'IDENTIFICADOR':
                    resultado_gramatica.append(f"Error en línea {p.lineno(1)}: Variable '{nombre}' no declarada")
            else:
                tabla_simbolos.marcar_como_usado(nombre)

    p[0] = p[1]


def p_empty(p):
    'empty :'
    pass


# Manejo de errores mejorado
def p_error(p):
    global resultado_gramatica

    # Si no hay token, podría ser el final del archivo
    if not p:
        error = "Error de sintaxis al final del archivo"
        resultado_gramatica.append(error)
        return

    # Si estamos procesando la declaración de main, manejar caso especial
    linea_actual = p.lineno if hasattr(p, 'lineno') else -1

    if hasattr(p, 'lexer') and hasattr(p.lexer, 'lexdata'):
        data = p.lexer.lexdata.split('\n')

        # Buscar si estamos en una línea que contiene "main" y "String[]"
        for i, line in enumerate(data):
            if i + 1 == linea_actual and "main" in line and ("String[]" in line or "String [ ]" in line):
                # Estamos en la declaración de main, ignorar errores de CORIZQ/CORDER
                if p.type in ('CORIZQ', 'CORDER'):
                    parser.errok()
                    return

    # Para otros errores, dar un mensaje descriptivo
    if p.type == 'IDENTIFICADOR':
        error = f"Error de sintaxis en línea {p.lineno}: '{p.value}' podría necesitar ser declarado primero"
    elif p.type in ('CORDER', 'CORIZQ'):
        error = f"Error de sintaxis en línea {p.lineno}: Uso incorrecto de corchetes '[]'"
    elif p.type in ('PARDER', 'PARIZQ'):
        error = f"Error de sintaxis en línea {p.lineno}: Desbalance de paréntesis '()'"
    elif p.type in ('LLADER', 'LLAIZQ'):
        error = f"Error de sintaxis en línea {p.lineno}: Desbalance de llaves '{{}}'"
    elif p.type == 'PUNTOCOMA':
        error = f"Error de sintaxis en línea {p.lineno}: Punto y coma ';' inesperado o faltante"
    else:
        error = f"Error de sintaxis en línea {p.lineno}: Token inesperado '{p.value}' de tipo {p.type}"

    resultado_gramatica.append(error)
    parser.errok()  # Intentar recuperarse para continuar el análisis


# Inicializar el analizador sintáctico
parser = yacc.yacc()


# Función para analizar un código fuente completo
def prueba_sintactica(data):
    global resultado_gramatica

    # Crear una nueva instancia del lexer
    lexer = construir_lexer()
    lexer.lineno = 1  # Reiniciar contador de líneas

    # Crear una nueva instancia del parser con el lexer
    parser = yacc.yacc()

    # Limpiar resultados anteriores
    resultado_gramatica.clear()
    tabla_simbolos.limpiar()

    if not data.strip():
        resultado_gramatica.append("No hay código para analizar")
        return resultado_gramatica

    try:
        # Verificar que sea código Java válido
        if "class" not in data and "Class" not in data:
            resultado_gramatica.append(
                "Error: El código no parece ser un programa Java válido. Debe contener una clase.")
            return resultado_gramatica

        # Verificar balanceo de paréntesis, llaves, etc.
        contadores = {'(': 0, ')': 0, '{': 0, '}': 0, '"': 0, "'": 0, '[': 0, ']': 0}

        # Variable para rastrear si estamos dentro de un comentario
        en_comentario_linea = False
        en_comentario_bloque = False
        i = 0

        while i < len(data):
            # Verificar comentarios
            if not en_comentario_bloque and i < len(data) - 1 and data[i:i + 2] == '//':
                en_comentario_linea = True
            elif not en_comentario_linea and i < len(data) - 1 and data[i:i + 2] == '/*':
                en_comentario_bloque = True
                i += 2
                continue
            elif en_comentario_bloque and i < len(data) - 1 and data[i:i + 2] == '*/':
                en_comentario_bloque = False
                i += 2
                continue
            elif en_comentario_linea and data[i] == '\n':
                en_comentario_linea = False

            # Omitir el conteo si estamos en un comentario
            if not en_comentario_linea and not en_comentario_bloque:
                if data[i] in contadores:
                    contadores[data[i]] += 1

            # Avanzar al siguiente carácter
            i += 1

        # Verificar balanceo
        if contadores['('] != contadores[')']:
            resultado_gramatica.append(
                f"Error: Desbalance de paréntesis - {contadores['(']} abiertos y {contadores[')']} cerrados")
        if contadores['{'] != contadores['}']:
            resultado_gramatica.append(
                f"Error: Desbalance de llaves - {contadores['{']} abiertas y {contadores['}']} cerradas")
        if contadores['['] != contadores[']']:
            resultado_gramatica.append(
                f"Error: Desbalance de corchetes - {contadores['[']} abiertos y {contadores[']']} cerrados")
        if contadores['"'] % 2 != 0:
            resultado_gramatica.append(f"Error: Número impar de comillas dobles (\") - posible cadena no cerrada")
        if contadores["'"] % 2 != 0:
            resultado_gramatica.append(f"Error: Número impar de comillas simples (') - posible carácter no cerrado")

        # Verificar System.out.print sin comillas o punto y coma
        if "System.out.print" in data:
            for i, line in enumerate(data.split('\n')):
                if "System.out.print" in line and not line.strip().endswith(";"):
                    resultado_gramatica.append(
                        f"Error en línea {i + 1}: Línea con System.out.print sin punto y coma: {line.strip()}")

                if "System.out.print" in line and '(' in line and ')' in line:
                    # Extraer lo que está dentro de los paréntesis
                    contenido = line.split("(")[1].split(")")[0].strip()
                    if contenido and not ('"' in contenido or "'" in contenido or
                                          any(var in contenido for var in tabla_simbolos.obtener_todos()) or
                                          contenido in ["true", "false", "null"] or
                                          contenido.isdigit()):
                        resultado_gramatica.append(
                            f"Advertencia en línea {i + 1}: Posible uso de variable no declarada en System.out.print: {contenido}")

        # Analizar el código
        result = parser.parse(data, lexer=lexer)  # Pasar el lexer explícitamente
        if result:
            resultado_gramatica.append(result)

        # Verificar variables declaradas pero no utilizadas
        variables_sin_usar = tabla_simbolos.verificar_uso()
        for nombre, info in variables_sin_usar:
            if info['tipo'] not in ['CLASS', 'METHOD']:  # No reportar clases o métodos no utilizados
                resultado_gramatica.append(
                    f"Advertencia: Variable '{nombre}' declarada en línea {info['linea']} pero no utilizada")

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