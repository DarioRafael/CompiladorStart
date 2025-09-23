# -*- coding: utf-8 -*-
import ply.lex as lex

# resultado del analisis
resultado_lexema = []


# =========================
# Tabla de símbolos
# =========================
class TablaSimbolos:
    def __init__(self):
        self.simbolos = {}
        self.alcance_actual = ['global']  # Pila de alcances (global, función, etc.)
        self.nivel_llaves = 0  # Contador de niveles de llaves para detectar bloques
        self.en_metodo = False  # NUEVO: Flag para saber si estamos dentro de un método

    def agregar(self, nombre, tipo, linea, valor=None):
        """Agrega un símbolo a la tabla"""
        alcance = self.determinar_alcance()
        nombre_completo = f"{alcance}.{nombre}" if alcance != 'global' else nombre

        self.simbolos[nombre_completo] = {
            'tipo': tipo,
            'linea': linea,
            'valor': valor,
            'alcance': alcance,
            'usado': False  # Inicialmente no usado
        }

    def determinar_alcance(self):
        """Determina el alcance actual basado en el contexto"""
        # Si no estamos en un método, es alcance global (variables de clase)
        if not self.en_metodo:
            return 'global'

        # Si estamos en un método y hay más de 1 nivel de llaves = bloque local
        if self.en_metodo and self.nivel_llaves > 1:
            return 'local'

        # Si estamos en un método pero con 1 nivel de llaves o menos = alcance del método
        if self.en_metodo and len(self.alcance_actual) > 1:
            return self.alcance_actual[-1]

        return 'global'

    def existe(self, nombre):
        """Verifica si un símbolo existe en la tabla"""
        for alcance in reversed(self.alcance_actual):
            nombre_completo = f"{alcance}.{nombre}" if alcance != 'global' else nombre
            if nombre_completo in self.simbolos:
                return True
        # También intenta alcances comunes
        if f"local.{nombre}" in self.simbolos:
            return True
        if f"main.{nombre}" in self.simbolos:
            return True
        if nombre in self.simbolos:
            return True
        return False

    def _resolver_nombre_completo(self, nombre: str):
        """Devuelve el nombre completo (con alcance) más adecuado para 'nombre'."""
        for alcance in reversed(self.alcance_actual):
            nombre_completo = f"{alcance}.{nombre}" if alcance != 'global' else nombre
            if nombre_completo in self.simbolos:
                return nombre_completo
        if f"local.{nombre}" in self.simbolos:
            return f"local.{nombre}"
        if f"main.{nombre}" in self.simbolos:
            return f"main.{nombre}"
        if nombre in self.simbolos:
            return nombre
        return None

    def actualizar_valor(self, nombre: str, valor):
        """
        Actualiza el campo 'valor' del símbolo 'nombre'
        resolviendo alcance automáticamente. Devuelve True si actualizó.
        """
        nombre_completo = self._resolver_nombre_completo(nombre)
        if nombre_completo and nombre_completo in self.simbolos:
            self.simbolos[nombre_completo]['valor'] = valor
            return True
        return False

    def obtener_valor(self, nombre: str):
        """Obtiene el valor del símbolo si existe."""
        nombre_completo = self._resolver_nombre_completo(nombre)
        if nombre_completo and nombre_completo in self.simbolos:
            return self.simbolos[nombre_completo].get('valor', None)
        return None

    def obtener(self, nombre):
        """Obtiene un símbolo (dict) por nombre (resolviendo alcance)."""
        nombre_completo = self._resolver_nombre_completo(nombre)
        if nombre_completo and nombre_completo in self.simbolos:
            return self.simbolos[nombre_completo]
        return None

    def marcar_como_usado(self, nombre):
        """Marca un símbolo como usado."""
        nombre_completo = self._resolver_nombre_completo(nombre)
        if nombre_completo and nombre_completo in self.simbolos:
            self.simbolos[nombre_completo]['usado'] = True
            return True
        return False

    def abrir_alcance(self, nombre):
        """Abre un nuevo ámbito (por ejemplo, nombre del método)."""
        self.alcance_actual.append(nombre)
        if nombre == 'main':  # NUEVO: Marcar que entramos al método main
            self.en_metodo = True

    def cerrar_alcance(self):
        """Cierra el ámbito actual."""
        if len(self.alcance_actual) > 1:
            alcance_cerrado = self.alcance_actual.pop()
            if alcance_cerrado == 'main':  # NUEVO: Salimos del método main
                self.en_metodo = False

    def abrir_bloque(self):
        """Incrementa el contador de bloques { }."""
        self.nivel_llaves += 1

    def cerrar_bloque(self):
        """Decrementa el contador de bloques { }."""
        if self.nivel_llaves > 0:
            self.nivel_llaves -= 1
        # NUEVO: Si salimos del último bloque del método, salimos del método
        if self.nivel_llaves == 0 and self.en_metodo:
            self.cerrar_alcance()

    def obtener_todos(self):
        """Todos los símbolos."""
        return self.simbolos

    def limpiar(self):
        """Reset de la tabla."""
        self.simbolos = {}
        self.alcance_actual = ['global']
        self.nivel_llaves = 0
        self.en_metodo = False  # NUEVO: Reset del flag

    def verificar_uso(self):
        return [
            (nombre, info) for nombre, info in self.simbolos.items()
            if not info.get('usado', False) and
               info['tipo'] not in ['CLASS', 'METHOD'] and
               nombre != 'args'
        ]


# Global
tabla_simbolos = TablaSimbolos()

# =========================
# Palabras reservadas
# =========================
reservadas = {
    'abstract': 'ABSTRACT', 'assert': 'ASSERT', 'boolean': 'BOOLEAN', 'break': 'BREAK',
    'byte': 'BYTE', 'case': 'CASE', 'catch': 'CATCH', 'char': 'CHAR', 'class': 'CLASS',
    'const': 'CONST', 'continue': 'CONTINUE', 'default': 'DEFAULT', 'do': 'DO',
    'double': 'DOUBLE', 'else': 'ELSE', 'enum': 'ENUM', 'extends': 'EXTENDS',
    'final': 'FINAL', 'finally': 'FINALLY', 'float': 'FLOAT', 'for': 'FOR', 'if': 'IF',
    'implements': 'IMPLEMENTS', 'import': 'IMPORT', 'instanceof': 'INSTANCEOF',
    'int': 'INT', 'interface': 'INTERFACE', 'long': 'LONG', 'native': 'NATIVE',
    'new': 'NEW', 'package': 'PACKAGE', 'private': 'PRIVATE', 'protected': 'PROTECTED',
    'public': 'PUBLIC', 'return': 'RETURN', 'short': 'SHORT', 'static': 'STATIC',
    'strictfp': 'STRICTFP', 'super': 'SUPER', 'switch': 'SWITCH', 'synchronized': 'SYNCHRONIZED',
    'this': 'THIS', 'throw': 'THROW', 'throws': 'THROWS', 'transient': 'TRANSIENT',
    'try': 'TRY', 'void': 'VOID', 'volatile': 'VOLATILE', 'while': 'WHILE',
    'true': 'TRUE', 'false': 'FALSE', 'null': 'NULL',
    'String': 'STRING', 'System': 'SYSTEM', 'out': 'OUT', 'println': 'PRINTLN', 'print': 'PRINT',
    'main': 'MAIN',
}

# =========================
# Tokens
# =========================
tokens = [
             'IDENTIFICADOR', 'ENTERO', 'DECIMAL', 'CADENA', 'CARACTER',
             'SUMA', 'RESTA', 'MULT', 'DIV', 'MODULO', 'INCREMENTO', 'DECREMENTO',
             'ASIGNAR', 'SUMAASIGNAR', 'RESTAASIGNAR', 'MULTASIGNAR', 'DIVASIGNAR', 'MODULOASIGNAR',
             'MENORQUE', 'MAYORQUE', 'MENORIGUAL', 'MAYORIGUAL', 'IGUAL', 'DISTINTO',
             'AND', 'OR', 'NOT',
             'BITAND', 'BITOR', 'BITXOR', 'BITNOT', 'BITSHIFTIZQ', 'BITSHIFTDER', 'BITSHIFTDERU',
             'PARIZQ', 'PARDER', 'CORIZQ', 'CORDER', 'LLAIZQ', 'LLADER', 'PUNTO', 'COMA',
             'PUNTOCOMA', 'DOSPUNTOS', 'INTERROGACION', 'ARROBA',
         ] + list(reservadas.values())

# =========================
# Reglas simples
# =========================
t_SUMA = r'\+'
t_RESTA = r'-'
t_MULT = r'\*'
t_DIV = r'/'
t_MODULO = r'%'
t_INCREMENTO = r'\+\+'
t_DECREMENTO = r'--'

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
t_DOSPUNTOS = r':'
t_INTERROGACION = r'\?'
t_ARROBA = r'@'
t_PUNTO = r'\.'
t_COMA = r','

t_ignore = ' \t'

# =========================
# Estado para contexto - AMPLIADO PARA CAPTURAR ASIGNACIONES
# =========================
estados = {
    'ultimo_tipo': None,
    'modo_declaracion': False,
    'clase_actual': None,
    'metodo_actual': None,
    'en_for': False,
    'variable_reciente': None,  # NUEVO: Variable recién declarada
    'esperando_valor': False,  # NUEVO: Si estamos esperando un valor después de =
    'ultimo_identificador': None,  # NUEVO: Último identificador visto
}


# =========================
# Tokens con acción
# =========================
def t_LLAIZQ(t):
    r'{'
    tabla_simbolos.abrir_bloque()
    return t


def t_LLADER(t):
    r'}'
    tabla_simbolos.cerrar_bloque()
    return t


# NUEVO: Manejo especial del operador de asignación
def t_ASIGNAR(t):
    r'=(?!=)'  # '=' que NO está seguido de '='  -> no choca con '=='
    # Si acabamos de ver un identificador, preparamos para capturar su valor
    if estados.get('ultimo_identificador') and not estados.get('esperando_valor'):
        estados['esperando_valor'] = True
        estados['variable_reciente'] = estados['ultimo_identificador']
    return t


def t_DECIMAL(t):
    r'\d+\.\d+'
    t.value = float(t.value)

    # NUEVO: Si estamos esperando un valor, lo asignamos
    if estados.get('esperando_valor') and estados.get('variable_reciente'):
        if tabla_simbolos.actualizar_valor(estados['variable_reciente'], t.value):
            print(f"[DEBUG] Asignado valor {t.value} a variable {estados['variable_reciente']}")
        # Limpiar estado
        estados['esperando_valor'] = False
        estados['variable_reciente'] = None

    return t


def t_ENTERO(t):
    r'\d+'
    t.value = int(t.value)

    # NUEVO: Si estamos esperando un valor, lo asignamos
    if estados.get('esperando_valor') and estados.get('variable_reciente'):
        if tabla_simbolos.actualizar_valor(estados['variable_reciente'], t.value):
            print(f"[DEBUG] Asignado valor {t.value} a variable {estados['variable_reciente']}")
        # Limpiar estado
        estados['esperando_valor'] = False
        estados['variable_reciente'] = None

    return t


def t_IDENTIFICADOR(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reservadas.get(t.value, 'IDENTIFICADOR')

    # NUEVO: Manejo de valores literales booleanos y null
    if t.type in ('TRUE', 'FALSE', 'NULL'):
        if estados.get('esperando_valor') and estados.get('variable_reciente'):
            valor = None
            if t.type == 'TRUE':
                valor = True
            elif t.type == 'FALSE':
                valor = False
            else:  # NULL
                valor = None

            if tabla_simbolos.actualizar_valor(estados['variable_reciente'], valor):
                print(f"[DEBUG] Asignado valor {valor} a variable {estados['variable_reciente']}")
            # Limpiar estado
            estados['esperando_valor'] = False
            estados['variable_reciente'] = None

    if t.type == 'FOR':
        estados['en_for'] = True

    # Si es tipo → entra modo declaración
    if t.type in ('INT', 'FLOAT', 'DOUBLE', 'CHAR', 'BOOLEAN', 'STRING', 'BYTE', 'SHORT', 'LONG'):
        estados['ultimo_tipo'] = t.type
        estados['modo_declaracion'] = True
    elif estados['modo_declaracion'] and t.type == 'IDENTIFICADOR':
        # CORRECCIÓN: Usar el alcance determinado por la tabla de símbolos
        alcance_actual = tabla_simbolos.determinar_alcance()
        if estados['en_for']:
            alcance_actual = 'local'

        tabla_simbolos.agregar(t.value, estados['ultimo_tipo'], t.lineno)

        # CORRECCIÓN: Ajustar el alcance después de agregar
        nombre_completo = f"{alcance_actual}.{t.value}" if alcance_actual != 'global' else t.value
        if nombre_completo in tabla_simbolos.simbolos:
            tabla_simbolos.simbolos[nombre_completo]['alcance'] = alcance_actual

        print(
            f"[DEBUG] Variable '{t.value}' declarada en alcance '{alcance_actual}' (en_metodo: {tabla_simbolos.en_metodo}, nivel_llaves: {tabla_simbolos.nivel_llaves})")

        estados['modo_declaracion'] = False
        # NUEVO: Guardar como último identificador para posibles asignaciones
        estados['ultimo_identificador'] = t.value
    elif t.type == 'IDENTIFICADOR':
        # NUEVO: Siempre guardar el último identificador
        estados['ultimo_identificador'] = t.value
        if tabla_simbolos.existe(t.value):
            tabla_simbolos.marcar_como_usado(t.value)

    # Seguimiento clase/método
    if t.type == 'CLASS':
        estados['clase_actual'] = 'esperando_nombre'
    elif estados['clase_actual'] == 'esperando_nombre' and t.type == 'IDENTIFICADOR':
        estados['clase_actual'] = t.value
        tabla_simbolos.agregar(t.value, 'CLASS', t.lineno)
    elif t.type == 'MAIN':
        estados['metodo_actual'] = 'main'
        tabla_simbolos.abrir_alcance('main')
        tabla_simbolos.agregar('main', 'METHOD', t.lineno)
        print(f"[DEBUG] Entrando al método main (en_metodo: {tabla_simbolos.en_metodo})")

    return t


def t_CADENA(t):
    r'"[^"]*"'
    valor_original = t.value[1:-1]  # Sin comillas para el valor interno
    t.value = valor_original

    # NUEVO: Si estamos esperando un valor, lo asignamos
    if estados.get('esperando_valor') and estados.get('variable_reciente'):
        # Guardamos con comillas para mostrar que es una cadena
        valor_mostrar = f'"{valor_original}"'
        if tabla_simbolos.actualizar_valor(estados['variable_reciente'], valor_mostrar):
            print(f"[DEBUG] Asignado valor {valor_mostrar} a variable {estados['variable_reciente']}")
        # Limpiar estado
        estados['esperando_valor'] = False
        estados['variable_reciente'] = None

    return t


def t_CARACTER(t):
    r"'[^']'"
    valor_original = t.value[1:-1]  # Sin comillas para el valor interno
    t.value = valor_original

    # NUEVO: Si estamos esperando un valor, lo asignamos
    if estados.get('esperando_valor') and estados.get('variable_reciente'):
        # Guardamos con comillas simples para mostrar que es un carácter
        valor_mostrar = f"'{valor_original}'"
        if tabla_simbolos.actualizar_valor(estados['variable_reciente'], valor_mostrar):
            print(f"[DEBUG] Asignado valor {valor_mostrar} a variable {estados['variable_reciente']}")
        # Limpiar estado
        estados['esperando_valor'] = False
        estados['variable_reciente'] = None

    return t


def t_COMENTARIO_LINEA(t):
    r'//.*\n'
    t.lexer.lineno += 1


def t_COMENTARIO_BLOQUE(t):
    r'/\*[\s\S]*?\*/'
    t.lexer.lineno += t.value.count('\n')


def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)


def t_PUNTOCOMA(t):
    r';'
    estados['modo_declaracion'] = False
    estados['en_for'] = False
    # NUEVO: Limpiar estado de asignación al final de la declaración
    estados['esperando_valor'] = False
    estados['variable_reciente'] = None
    return t


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


# =========================
# API
# =========================
def prueba(data):
    global resultado_lexema, estados
    analizador = lex.lex()
    analizador.lineno = 1
    analizador.input(data)

    # Reset estados/tabla/resultado - AMPLIADO
    estados['ultimo_tipo'] = None
    estados['modo_declaracion'] = False
    estados['clase_actual'] = None
    estados['metodo_actual'] = None
    estados['en_for'] = False
    estados['variable_reciente'] = None
    estados['esperando_valor'] = False
    estados['ultimo_identificador'] = None
    tabla_simbolos.limpiar()
    resultado_lexema.clear()

    print(f"[DEBUG] Iniciando análisis del código...")
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

    print(f"[DEBUG] Análisis completado. Símbolos en tabla:")
    for nombre, info in tabla_simbolos.obtener_todos().items():
        print(f"  {nombre}: {info}")

    return resultado_lexema


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