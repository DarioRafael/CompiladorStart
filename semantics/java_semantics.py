# -*- coding: utf-8 -*-
# semantics/java_semantics.py
from typing import List, Dict, Tuple, Optional
from lexer.analizador_lexico import construir_lexer

# Mapa de tokens de tipo -> nombre semántico
PrimitiveMap = {
    'INT': 'int',
    'BOOLEAN': 'boolean',
    'CHAR': 'char',
    'BYTE': 'byte',
    'SHORT': 'short',
    'LONG': 'long',
    'FLOAT': 'float',
    'DOUBLE': 'double',
    'STRING': 'String',
}

# Literales -> tipo
LITERALS_TYPE = {
    'ENTERO': 'numeric',
    'DECIMAL': 'numeric',
    'CADENA': 'String',
    'CARACTER': 'char',
    'TRUE': 'boolean',
    'FALSE': 'boolean',
    'NULL': 'null',
}

# Conjuntos de operadores
ARITH_OPS = {
    'SUMA', 'RESTA', 'MULT', 'DIV', 'MODULO',
    'BITAND', 'BITOR', 'BITXOR', 'BITSHIFTIZQ', 'BITSHIFTDER', 'BITSHIFTDERU'
}
BOOL_OPS = {
    'AND', 'OR', 'IGUAL', 'DISTINTO',
    'MENORQUE', 'MAYORQUE', 'MENORIGUAL', 'MAYORIGUAL',
    'NOT', 'BITNOT'
}
ASSIGN_OPS = {'ASIGNAR', 'SUMAASIGNAR', 'RESTAASIGNAR', 'MULTASIGNAR', 'DIVASIGNAR', 'MODULOASIGNAR'}

MODIFIERS = {
    'PUBLIC', 'PRIVATE', 'PROTECTED', 'STATIC', 'FINAL',
    'ABSTRACT', 'NATIVE', 'STRICTFP', 'SYNCHRONIZED', 'TRANSIENT', 'VOLATILE'
}

BUILTIN_CHAIN = {"System", "out", "print", "println"}


def _mk(start: int, length: int, line: int, col: int, message: str) -> Dict:
    return {"start": start, "length": length, "line": line, "col": col, "message": message}

def _tok_len(tok) -> int:
    try:
        return len(tok.value) if isinstance(tok.value, str) else 1
    except Exception:
        return 1

def _peek(buf, i, n=1):
    j = i + n
    return buf[j] if 0 <= j < len(buf) else None

def _col_of(code: str, tok) -> int:
    # columna 1-based
    idx = tok.lexpos
    prev_nl = code.rfind('\n', 0, idx)
    if prev_nl < 0:
        return idx + 1
    return idx - prev_nl

def _line_of(tok) -> int:
    return getattr(tok, 'lineno', 1)



def _is_modifier(tt: str) -> bool:
    return tt in MODIFIERS

def _is_type_token(tt: str) -> bool:
    # tipo primitivo/STRING o tipo usuario (IDENTIFICADOR)
    return tt in PrimitiveMap or tt in ('STRING', 'IDENTIFICADOR')

def _token_type_name(tok) -> str:
    if not tok:
        return 'unknown'
    if tok.type in PrimitiveMap:
        return PrimitiveMap[tok.type]
    if tok.type == 'STRING':
        return 'String'
    if tok.type == 'IDENTIFICADOR':
        # tipo usuario
        return tok.value
    return 'unknown'

def _is_member_access(tokens, i) -> bool:
    """IDENT . IDENT (o parte de cadena de miembros)."""
    prev = _peek(tokens, i, -1)
    next1 = _peek(tokens, i, 1)
    return (prev and prev.type == 'PUNTO') or (next1 and next1.type == 'PUNTO')

def _is_method_call(tokens, i) -> bool:
    """IDENT ( ... )"""
    next1 = _peek(tokens, i, 1)
    return next1 and next1.type == 'PARIZQ'


def _expr_type(tokens, i, resolve_name) -> Tuple[str, int]:
    """
    Deduce tipo semántico aproximado de una expresión desde tokens[i...] hasta ; o ) a nivel 0.
    Usa resolve_name(name) para identificar el tipo de identificadores.
    Devuelve (tipo, next_index_after_expr).
    """
    seen_string = False
    seen_numeric = False
    seen_boolean = False
    seen_char = False
    seen_new = False
    depth_paren = 0

    idx = i
    while idx < len(tokens):
        t = tokens[idx]
        tt = t.type

        if tt == 'PUNTOCOMA' and depth_paren == 0:
            break
        if tt == 'PARDER' and depth_paren == 0:
            break
        if tt == 'DOSPUNTOS' and depth_paren == 0:
            idx += 1
            continue

        if tt == 'PARIZQ':
            depth_paren += 1
        elif tt == 'PARDER':
            depth_paren = max(0, depth_paren - 1)

        if tt in LITERALS_TYPE:
            ty = LITERALS_TYPE[tt]
            if ty == 'String':
                seen_string = True
            elif ty == 'numeric':
                seen_numeric = True
            elif ty == 'boolean':
                seen_boolean = True
            elif ty == 'char':
                seen_char = True

        elif tt == 'IDENTIFICADOR':
            name = t.value
            if name in BUILTIN_CHAIN:
                pass
            elif _is_member_access(tokens, idx):
                pass
            elif _is_method_call(tokens, idx):
                pass
            else:
                decl_ty = resolve_name(name)
                # mapear a categorías
                if decl_ty:
                    if decl_ty == 'String':
                        seen_string = True
                    elif decl_ty == 'boolean':
                        seen_boolean = True
                    elif decl_ty == 'char':
                        seen_char = True
                    elif decl_ty.endswith('[]'):
                        pass
                    else:
                        if decl_ty in ('byte', 'short', 'int', 'long', 'float', 'double'):
                            seen_numeric = True

        elif tt == 'NEW':
            seen_new = True
            nxt = _peek(tokens, idx, 1)
            nxt2 = _peek(tokens, idx, 2)
            if nxt and nxt2 and nxt2.type == 'CORIZQ':
                return ("array", idx + 1)  # new T[...]
            if nxt and nxt.type == 'STRING':
                seen_string = True

        elif tt in ARITH_OPS:
            if tt == 'SUMA' and seen_string:
                seen_string = True
            else:
                seen_numeric = True

        elif tt in BOOL_OPS:
            seen_boolean = True

        idx += 1

    if seen_string:
        return ('String', idx)
    if seen_boolean:
        return ('boolean', idx)
    if seen_char:
        return ('char', idx)
    if seen_numeric:
        return ('numeric', idx)
    if seen_new:
        return ('object', idx)
    return ('unknown', idx)


def _parse_parameter_list(tokens, i) -> Tuple[List[Tuple[str, str, object]], int]:
    """
    Parsea parámetros desde tokens[i] donde tokens[i] == PARIZQ.
    Devuelve ([(name, type_name, name_tok), ...], next_index_after_closing_paren)
    """
    params = []
    if not (i < len(tokens) and tokens[i].type == 'PARIZQ'):
        return params, i

    idx = i + 1
    depth = 1
    while idx < len(tokens) and depth > 0:
        t = tokens[idx]
        tt = t.type

        if tt == 'PARIZQ':
            depth += 1
            idx += 1
            continue
        if tt == 'PARDER':
            depth -= 1
            idx += 1
            if depth == 0:
                break
            continue

        if tt == 'STRING':
            t1 = _peek(tokens, idx, 1)
            t2 = _peek(tokens, idx, 2)
            t3 = _peek(tokens, idx, 3)
            if t1 and t1.type == 'CORIZQ' and t2 and t2.type == 'CORDER' and t3 and t3.type == 'IDENTIFICADOR':
                params.append((t3.value, 'String[]', t3))
                idx += 4
                if _peek(tokens, idx) and _peek(tokens, idx).type == 'COMA':
                    idx += 1
                continue

        if _is_type_token(tt):
            name_tok = _peek(tokens, idx, 1)
            if name_tok and name_tok.type == 'IDENTIFICADOR':
                ty = _token_type_name(t)
                # sufijo array: T name [] (param estilo antiguo)
                b1 = _peek(tokens, idx, 2)
                b2 = _peek(tokens, idx, 3)
                if b1 and b1.type == 'CORIZQ' and b2 and b2.type == 'CORDER':
                    ty = ty + '[]'
                    idx += 2  # consumimos [] después del nombre (manteniendo patrón simple)
                params.append((name_tok.value, ty, name_tok))
                idx += 2
                if _peek(tokens, idx) and _peek(tokens, idx).type == 'COMA':
                    idx += 1
                continue

        idx += 1

    return params, idx


def _check_assign_compat(errors, code, op_tok, target_ty: str, expr_ty: str):
    """Valida compatibilidad en asignación (incluye compuestas)."""
    def is_numeric(ty): return ty == 'numeric' or ty in (
        'byte', 'short', 'int', 'long', 'float', 'double'
    )

    line = _line_of(op_tok)
    col = _col_of(code, op_tok)

    if target_ty.endswith('[]'):
        # aceptamos 'array' o 'object' (new T[...])
        if expr_ty not in ('array', 'object'):
            errors.append(_mk(op_tok.lexpos, 1, line, col,
                              f"Incompatibilidad de tipos: se esperaba '{target_ty}' y se asigna '{expr_ty}'."))
        return

    if target_ty == 'String':
        if expr_ty not in ('String',):
            errors.append(_mk(op_tok.lexpos, 1, line, col,
                              f"Incompatibilidad de tipos: se esperaba 'String' y se asigna '{expr_ty}'."))
        return

    if target_ty == 'boolean':
        if expr_ty not in ('boolean',):
            errors.append(_mk(op_tok.lexpos, 1, line, col,
                              f"Incompatibilidad de tipos: se esperaba 'boolean' y se asigna '{expr_ty}'."))
        return

    if target_ty == 'char':
        if expr_ty not in ('char',):
            errors.append(_mk(op_tok.lexpos, 1, line, col,
                              f"Incompatibilidad de tipos: se esperaba 'char' y se asigna '{expr_ty}'."))
        return

    # numéricos
    if is_numeric(target_ty):
        if not is_numeric(expr_ty):
            errors.append(_mk(op_tok.lexpos, 1, line, col,
                              f"Incompatibilidad de tipos: se esperaba tipo numérico y se asigna '{expr_ty}'."))
        return



def _check_compound_compat(errors, code, op_tok, target_ty: str, expr_ty: str):
    """Validación para += -= *= /= %= (permite String += String/numeric)."""
    def is_numeric(ty): return ty == 'numeric' or ty in (
        'byte', 'short', 'int', 'long', 'float', 'double'
    )

    line = _line_of(op_tok)
    col = _col_of(code, op_tok)

    if target_ty == 'String' and op_tok.type == 'SUMAASIGNAR':
        if expr_ty in ('String', 'numeric'):
            return
        errors.append(_mk(op_tok.lexpos, 1, line, col,
                          f"Incompatibilidad: 'String' no puede concatenar '{expr_ty}'."))
        return

    # cualquier otra compuesta espera numéricos
    if not is_numeric(target_ty) or not is_numeric(expr_ty):
        errors.append(_mk(op_tok.lexpos, 1, line, col,
                          f"Incompatibilidad: operador '{op_tok.type}' requiere tipos numéricos."))
        return



def analyze_semantics(code: str) -> List[Dict]:
    """
    Semántico ligero pero robusto:
      - Registra clases (CLASS IDENTIFICADOR)
      - Detecta métodos con modificadores, retorno (tipo|VOID), nombre y parámetros; inyecta params al abrir '{'
      - Scopes por llaves { }
      - Declaraciones de variable (arrays prefijo/sufijo) y con inicialización
      - Asignaciones simples y compuestas con verificación de tipos
      - Uso no declarado y redeclaración
      - Ignora System.out.println y llamadas a método para "uso no declarado"
      - Tipado de expresiones con literales, identificadores declarados, new, operadores
    Devuelve lista de dicts {start,length,line,col,message}
    """
    errors: List[Dict] = []
    lx = construir_lexer()
    lx.input(code)

    toks = []
    while True:
        t = lx.token()
        if not t:
            break
        toks.append(t)

    scopes: List[Dict[str, str]] = [ {} ]
    class_names: set = set()

    pending_method_params: List[Tuple[str, str, object]] = []
    waiting_method_body_brace = False

    def declare(tok_name: object, typ: str):
        name = tok_name.value if hasattr(tok_name, 'value') else str(tok_name)
        cur = scopes[-1]
        if name in cur:
            errors.append(_mk(tok_name.lexpos, _tok_len(tok_name), _line_of(tok_name), _col_of(code, tok_name),
                              f"Redeclaración de variable '{name}' en el mismo alcance."))
        else:
            cur[name] = typ

    def resolve(name: str) -> Optional[str]:
        for s in reversed(scopes):
            if name in s:
                return s[name]
        return None

    i = 0
    while i < len(toks):
        t = toks[i]
        tt = t.type

        # Abrir/Cerrar scopes
        if tt == 'LLAIZQ':
            scopes.append({})
            if waiting_method_body_brace and pending_method_params:
                for pname, ptype, ptok in pending_method_params:
                    declare(ptok, ptype)
                pending_method_params = []
                waiting_method_body_brace = False
            i += 1
            continue

        if tt == 'LLADER':
            if len(scopes) > 1:
                scopes.pop()
            i += 1
            continue

        if tt == 'CLASS':
            name_tok = _peek(toks, i, 1)
            if name_tok and name_tok.type == 'IDENTIFICADOR':
                class_names.add(name_tok.value)
                i += 2
                continue
            i += 1
            continue

        j = i
        while j < len(toks) and _is_modifier(toks[j].type):
            j += 1
        if j < len(toks) and (_is_type_token(toks[j].type) or toks[j].type == 'VOID'):
            # retorno
            if _peek(toks, j, 1) and _peek(toks, j, 1).type == 'IDENTIFICADOR':
                # nombre del método
                if _peek(toks, j, 2) and _peek(toks, j, 2).type == 'PARIZQ':
                    params, after_paren = _parse_parameter_list(toks, j + 2)
                    pending_method_params = params
                    waiting_method_body_brace = True
                    i = after_paren
                    continue


        if _is_type_token(tt):
            decl_ty = _token_type_name(t)
            # Forma prefijo: T [] IDENT
            name_tok = _peek(toks, i, 1)
            used_prefix_arr = False
            if name_tok and name_tok.type == 'CORIZQ':
                closeb = _peek(toks, i, 2)
                name_tok2 = _peek(toks, i, 3)
                if closeb and closeb.type == 'CORDER' and name_tok2 and name_tok2.type == 'IDENTIFICADOR':
                    decl_ty = decl_ty + '[]'
                    name_tok = name_tok2
                    used_prefix_arr = True

            if name_tok and name_tok.type == 'IDENTIFICADOR':
                declare(name_tok, decl_ty)

                # sufijo: T IDENT []
                if not used_prefix_arr:
                    b1 = _peek(toks, i, 2)
                    b2 = _peek(toks, i, 3)
                    if b1 and b1.type == 'CORIZQ' and b2 and b2.type == 'CORDER':
                        decl_ty = decl_ty + '[]'
                        scopes[-1][name_tok.value] = decl_ty
                        i += 2  # avancemos sobre [] después del nombre

                # ¿Asignación?
                assign_tok = _peek(toks, i, 2 if not used_prefix_arr else 4)
                if assign_tok and assign_tok.type in ASSIGN_OPS:
                    expr_start = i + (3 if not used_prefix_arr else 5)
                    expr_ty, nxt = _expr_type(toks, expr_start, resolve)

                    if assign_tok.type == 'ASIGNAR':
                        _check_assign_compat(errors, code, assign_tok, decl_ty, expr_ty)
                    else:
                        _check_compound_compat(errors, code, assign_tok, decl_ty, expr_ty)

                    i = max(expr_start, nxt)
                    continue
                else:
                    i += (2 if not used_prefix_arr else 4)
                    continue

        if tt == 'IDENTIFICADOR':
            name = t.value

            if name in class_names:
                i += 1
                continue

            if name in BUILTIN_CHAIN or _is_member_access(toks, i):
                i += 1
                continue

            if _is_method_call(toks, i):
                i += 1
                continue

            nxt = _peek(toks, i, 1)
            if nxt and nxt.type in ASSIGN_OPS:
                decl_ty = resolve(name)
                if decl_ty is None and name != 'args':
                    errors.append(_mk(t.lexpos, _tok_len(t), _line_of(t), _col_of(code, t),
                                      f"Variable '{name}' no declarada en este alcance."))

                expr_ty, stop = _expr_type(toks, i + 2, resolve)
                if decl_ty:
                    if nxt.type == 'ASIGNAR':
                        _check_assign_compat(errors, code, nxt, decl_ty, expr_ty)
                    else:
                        _check_compound_compat(errors, code, nxt, decl_ty, expr_ty)
                i = max(i + 2, stop)
                continue
            else:
                # uso simple: validar declaración (excepto args/System)
                if resolve(name) is None and name not in BUILTIN_CHAIN and name != 'args':
                    errors.append(_mk(t.lexpos, _tok_len(t), _line_of(t), _col_of(code, t),
                                      f"Uso de variable '{name}' no declarada."))
                i += 1
                continue

        i += 1

    return errors
