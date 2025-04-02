import ply.lex as lex

# resultado del analisis
resultado_lexema = []

# Palabras reservadas de Java
reservadas = {
    # Palabras clave fundamentales
    'abstract': 'ABSTRACT',
    'assert': 'ASSERT',
    'boolean': 'BOOLEAN',
    'break': 'BREAK',
    'byte': 'BYTE',
    'case': 'CASE',
    'catch': 'CATCH',
    'char': 'CHAR',
    'class': 'CLASS',
    'const': 'CONST',
    'continue': 'CONTINUE',
    'default': 'DEFAULT',
    'do': 'DO',
    'double': 'DOUBLE',
    'else': 'ELSE',
    'enum': 'ENUM',
    'extends': 'EXTENDS',
    'final': 'FINAL',
    'finally': 'FINALLY',
    'float': 'FLOAT',
    'for': 'FOR',
    'if': 'IF',
    'implements': 'IMPLEMENTS',
    'import': 'IMPORT',
    'instanceof': 'INSTANCEOF',
    'int': 'INT',
    'interface': 'INTERFACE',
    'long': 'LONG',
    'native': 'NATIVE',
    'new': 'NEW',
    'package': 'PACKAGE',
    'private': 'PRIVATE',
    'protected': 'PROTECTED',
    'public': 'PUBLIC',
    'return': 'RETURN',
    'short': 'SHORT',
    'static': 'STATIC',
    'strictfp': 'STRICTFP',
    'super': 'SUPER',
    'switch': 'SWITCH',
    'synchronized': 'SYNCHRONIZED',
    'this': 'THIS',
    'throw': 'THROW',
    'throws': 'THROWS',
    'transient': 'TRANSIENT',
    'try': 'TRY',
    'void': 'VOID',
    'volatile': 'VOLATILE',
    'while': 'WHILE',
    # Valores literales
    'true': 'TRUE',
    'false': 'FALSE',
    'null': 'NULL',
    'String': 'STRING',
    'System': 'SYSTEM',
    'out': 'OUT',
    'println': 'PRINTLN',
    'print': 'PRINT',
}

# Lista de tokens
tokens = [
             'IDENTIFICADOR',
             'ENTERO',
             'DECIMAL',
             'CADENA',
             'CARACTER',

             # Operadores aritméticos
             'SUMA',
             'RESTA',
             'MULT',
             'DIV',
             'MODULO',
             'INCREMENTO',
             'DECREMENTO',

             # Operadores de asignación
             'ASIGNAR',
             'SUMAASIGNAR',
             'RESTAASIGNAR',
             'MULTASIGNAR',
             'DIVASIGNAR',
             'MODULOASIGNAR',

             # Operadores relacionales
             'MENORQUE',
             'MAYORQUE',
             'MENORIGUAL',
             'MAYORIGUAL',
             'IGUAL',
             'DISTINTO',

             # Operadores lógicos
             'AND',
             'OR',
             'NOT',

             # Operadores bit a bit
             'BITAND',
             'BITOR',
             'BITXOR',
             'BITNOT',
             'BITSHIFTIZQ',
             'BITSHIFTDER',
             'BITSHIFTDERU',

             # Delimitadores
             'PARIZQ',
             'PARDER',
             'CORIZQ',
             'CORDER',
             'LLAIZQ',
             'LLADER',
             'PUNTO',
             'COMA',
             'PUNTOCOMA',
             'DOSPUNTOS',
             'INTERROGACION',
             'ARROBA',
         ] + list(reservadas.values())

# Reglas de expresiones regulares para tokens simples
t_SUMA = r'\+'
t_RESTA = r'-'
t_MULT = r'\*'
t_DIV = r'/'
t_MODULO = r'%'
t_INCREMENTO = r'\+\+'
t_DECREMENTO = r'--'

t_ASIGNAR = r'='
t_SUMAASIGNAR = r'\+='
t_RESTAASIGNAR = r'-='
t_MULTASIGNAR = r'\*='
t_DIVASIGNAR = r'/='
t_MODULOASIGNAR = r'%='

t_MENORQUE = r'<'
t_MAYORQUE = r'>'
t_MENORIGUAL = r'<='
t_MAYORIGUAL = r'>='
t_IGUAL = r'=='
t_DISTINTO = r'!='

t_AND = r'&&'
t_OR = r'\|\|'
t_NOT = r'!'

t_BITAND = r'&'
t_BITOR = r'\|'
t_BITXOR = r'\^'
t_BITNOT = r'~'
t_BITSHIFTIZQ = r'<<'
t_BITSHIFTDER = r'>>'
t_BITSHIFTDERU = r'>>>'

t_PARIZQ = r'\('
t_PARDER = r'\)'
t_CORIZQ = r'\['
t_CORDER = r'\]'
t_LLAIZQ = r'{'
t_LLADER = r'}'
t_PUNTO = r'\.'
t_COMA = r','
t_PUNTOCOMA = r';'
t_DOSPUNTOS = r':'
t_INTERROGACION = r'\?'
t_ARROBA = r'@'

# Ignorar espacios y tabulaciones
t_ignore = ' \t'


# Números decimales
def t_DECIMAL(t):
    r'\d+\.\d+'
    t.value = float(t.value)
    return t


# Números enteros
def t_ENTERO(t):
    r'\d+'
    t.value = int(t.value)
    return t


# Identificadores y palabras reservadas
def t_IDENTIFICADOR(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reservadas.get(t.value, 'IDENTIFICADOR')
    return t


# Cadenas de texto
def t_CADENA(t):
    r'"[^"]*"'
    t.value = t.value[1:-1]  # Eliminar las comillas
    return t


# Caracteres
def t_CARACTER(t):
    r"'[^']'"
    t.value = t.value[1:-1]  # Eliminar las comillas
    return t


# Comentarios de línea
def t_COMENTARIO_LINEA(t):
    r'//.*\n'
    t.lexer.lineno += 1
    pass  # No devolver token para comentarios


# Comentarios de bloque
def t_COMENTARIO_BLOQUE(t):
    r'/\*[\s\S]*?\*/'
    t.lexer.lineno += t.value.count('\n')
    pass  # No devolver token para comentarios


# Contar saltos de línea
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)


# Manejo de errores
def t_error(t):
    global resultado_lexema
    estado = {
        "tipo": "ERROR",
        "valor": t.value[0],
        "linea": t.lineno,
        "posicion": t.lexpos
    }
    resultado_lexema.append(estado)
    t.lexer.skip(1)


# Función para analizar una cadena de entrada
def prueba(data):
    global resultado_lexema

    # Reiniciar el analizador léxico
    analizador = lex.lex()
    analizador.input(data)

    resultado_lexema.clear()

    while True:
        tok = analizador.token()
        if not tok:
            break

        estado = {
            "tipo": tok.type,
            "valor": tok.value,
            "linea": tok.lineno,
            "posicion": tok.lexpos
        }
        resultado_lexema.append(estado)

    return resultado_lexema


# Inicializar el analizador léxico
analizador = lex.lex()

if __name__ == '__main__':
    while True:
        data = input("Ingrese código Java: ")
        if not data:
            break
        resultados = prueba(data)
        for item in resultados:
            print(f"Línea {item['linea']} | Tipo {item['tipo']} | Valor {item['valor']} | Posición {item['posicion']}")