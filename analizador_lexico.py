import ply.lex as lex

# resultado del analisis
resultado_lexema = []


# Clase para gestionar la tabla de símbolos
class TablaSimbolos:
    def __init__(self):
        self.simbolos = {}
        self.alcance_actual = ['global']  # Pila de alcances (global, función, etc.)

    def agregar(self, nombre, tipo, linea, valor=None):
        """Agrega un símbolo a la tabla"""
        alcance = self.alcance_actual[-1]
        nombre_completo = f"{alcance}.{nombre}" if alcance != 'global' else nombre

        self.simbolos[nombre_completo] = {
            'tipo': tipo,
            'linea': linea,
            'valor': valor,
            'alcance': alcance,
            'usado': False  # Inicialmente no usado
        }

    def existe(self, nombre):
        """Verifica si un símbolo existe en la tabla"""
        # Primero buscar en el ámbito actual
        for alcance in reversed(self.alcance_actual):
            nombre_completo = f"{alcance}.{nombre}" if alcance != 'global' else nombre
            if nombre_completo in self.simbolos:
                return True
        return False

    def obtener(self, nombre):
        """Obtiene un símbolo de la tabla"""
        # Buscar en el ámbito actual y superiores
        for alcance in reversed(self.alcance_actual):
            nombre_completo = f"{alcance}.{nombre}" if alcance != 'global' else nombre
            if nombre_completo in self.simbolos:
                return self.simbolos[nombre_completo]
        return None

    def marcar_como_usado(self, nombre):
        """Marca un símbolo como usado"""
        # Buscar en el ámbito actual y superiores
        for alcance in reversed(self.alcance_actual):
            nombre_completo = f"{alcance}.{nombre}" if alcance != 'global' else nombre
            if nombre_completo in self.simbolos:
                self.simbolos[nombre_completo]['usado'] = True
                return True
        return False

    def abrir_alcance(self, nombre):
        """Abre un nuevo ámbito"""
        self.alcance_actual.append(nombre)

    def cerrar_alcance(self):
        """Cierra el ámbito actual"""
        if len(self.alcance_actual) > 1:
            self.alcance_actual.pop()

    def obtener_todos(self):
        """Obtiene todos los símbolos de la tabla"""
        return self.simbolos

    def limpiar(self):
        """Limpia la tabla de símbolos"""
        self.simbolos = {}
        self.alcance_actual = ['global']

    def verificar_uso(self):
        """Verifica si todos los símbolos han sido usados"""
        no_usados = []
        for nombre, info in self.simbolos.items():
            if not info['usado'] and info['tipo'] not in ('CLASS', 'METHOD'):
                no_usados.append((nombre, info))
        return no_usados


# Inicializar la tabla de símbolos
tabla_simbolos = TablaSimbolos()

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
    'main': 'MAIN',  # Añadido para detectar el método main
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
t_PUNTOCOMA = r';'  # Definición simple de PUNTOCOMA
t_DOSPUNTOS = r':'
t_INTERROGACION = r'\?'
t_ARROBA = r'@'

# Ignorar espacios y tabulaciones
t_ignore = ' \t'

# Estado para seguimiento del contexto
estados = {
    'ultimo_tipo': None,  # Último tipo visto (para declaraciones de variables)
    'modo_declaracion': False,  # Si estamos en modo de declaración de variable
    'clase_actual': None,  # Clase actual
    'metodo_actual': None,  # Método actual
}


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

    # Si es una palabra reservada que indica tipo, guardar para posible declaración
    if t.type in ('INT', 'FLOAT', 'DOUBLE', 'CHAR', 'BOOLEAN', 'STRING', 'BYTE', 'SHORT', 'LONG'):
        estados['ultimo_tipo'] = t.type
        estados['modo_declaracion'] = True
    # Si estamos en modo declaración y encontramos un identificador, es una declaración de variable
    elif estados['modo_declaracion'] and t.type == 'IDENTIFICADOR':
        tabla_simbolos.agregar(t.value, estados['ultimo_tipo'], t.lineno)
        estados['modo_declaracion'] = False
    # Si encontramos un identificador y no estamos en declaración, verificar si existe
    elif t.type == 'IDENTIFICADOR':
        # Verificar si el identificador ya está definido
        if tabla_simbolos.existe(t.value):
            tabla_simbolos.marcar_como_usado(t.value)

    # Seguimiento de clases y métodos
    if t.type == 'CLASS':
        estados['clase_actual'] = 'esperando_nombre'
    elif estados['clase_actual'] == 'esperando_nombre' and t.type == 'IDENTIFICADOR':
        estados['clase_actual'] = t.value
        tabla_simbolos.agregar(t.value, 'CLASS', t.lineno)
    elif t.type == 'MAIN':
        estados['metodo_actual'] = 'main'

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


# Actualización de estados al encontrar punto y coma
# Actualización de estados al encontrar punto y coma
# Actualización de estados al encontrar punto y coma
def t_punto_coma_handler(t):
    r';'  # Regular expression for semicolon
    estados['modo_declaracion'] = False
    t.type = 'PUNTOCOMA'  # Set the token type to PUNTOCOMA
    return t


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
    global estados
    analizador = lex.lex()
    analizador.lineno = 1

    analizador.input(data)

    # Reiniciar estados y resultados
    estados['ultimo_tipo'] = None
    estados['modo_declaracion'] = False
    estados['clase_actual'] = None
    estados['metodo_actual'] = None
    tabla_simbolos.limpiar()
    resultado_lexema.clear()

    # Analizar el código
    while True:
        tok = analizador.token()
        if not tok:
            break

        # Actualizar estado si es punto y coma
        if tok.type == 'PUNTOCOMA':
            estados['modo_declaracion'] = False

        estado = {
            "tipo": tok.type,
            "valor": tok.value,
            "linea": tok.lineno,
            "posicion": tok.lexpos
        }
        resultado_lexema.append(estado)

    # Verificar variables sin usar
    variables_sin_usar = tabla_simbolos.verificar_uso()
    for nombre, info in variables_sin_usar:
        resultado_lexema.append({
            "tipo": "ADVERTENCIA",
            "valor": f"Variable '{nombre}' declarada pero no usada",
            "linea": info['linea'],
            "posicion": 0
        })

    return resultado_lexema


# Inicializar el analizador léxico
def construir_lexer():
    return lex.lex()

if __name__ == '__main__':
    while True:
        data = input("Ingrese código Java: ")
        if not data:
            break
        resultados = prueba(data)
        for item in resultados:
            print(f"Línea {item['linea']} | Tipo {item['tipo']} | Valor {item['valor']} | Posición {item['posicion']}")