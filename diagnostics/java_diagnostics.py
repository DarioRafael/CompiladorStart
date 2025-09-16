# -*- coding: utf-8 -*-
# diagnostics/java_diagnostics.py
from typing import List, Dict, Tuple, Optional
from lexer.analizador_lexico import construir_lexer

def _mk(idx: int, length: int, line: int, col: int, msg: str) -> Dict:
    return {"start": idx, "length": length, "line": line, "col": col, "message": msg}

def _col_from_index(src: str, idx: int) -> int:
    # columna 1-based
    prev_nl = src.rfind('\n', 0, idx)
    if prev_nl < 0:
        return idx + 1
    return idx - prev_nl

def _line_from_index(src: str, idx: int) -> int:
    return src.count('\n', 0, idx) + 1

def _scan_structure(src: str) -> List[Dict]:
    """
    Escaneo carácter-a-carácter:
      - desbalance () {} []
      - comillas " ' sin cerrar (respeta escapes y comentarios)
    Devuelve lista de errores con posiciones.
    """
    errors: List[Dict] = []

    paren_stack: List[Tuple[int, int]] = []   # (idx, line)
    brace_stack: List[Tuple[int, int]] = []
    bracket_stack: List[Tuple[int, int]] = []

    in_sl_comment = False
    in_ml_comment = False
    in_single = False
    in_double = False

    single_start_idx = -1
    double_start_idx = -1

    i = 0
    n = len(src)

    while i < n:
        c = src[i]
        nxt = src[i+1] if i+1 < n else ''

        # comentarios
        if not in_single and not in_double:
            if not in_ml_comment and c == '/' and nxt == '/':
                in_sl_comment = True
                i += 2
                continue
            if not in_sl_comment and c == '/' and nxt == '*':
                in_ml_comment = True
                i += 2
                continue

        if in_sl_comment:
            if c == '\n':
                in_sl_comment = False
            i += 1
            continue

        if in_ml_comment:
            if c == '*' and nxt == '/':
                in_ml_comment = False
                i += 2
                continue
            i += 1
            continue

        # strings / chars (respetar escapes)
        if not in_single and c == '"' and not in_double:
            in_double = True
            double_start_idx = i
            i += 1
            continue
        elif in_double:
            if c == '\\':  # escape
                i += 2
                continue
            if c == '"':
                in_double = False
                i += 1
                continue
            i += 1
            continue

        if not in_double and c == "'" and not in_single:
            in_single = True
            single_start_idx = i
            i += 1
            continue
        elif in_single:
            if c == '\\':  # escape
                i += 2
                continue
            if c == "'":
                in_single = False
                i += 1
                continue
            i += 1
            continue

        # balanceo de (), {}, []
        if c == '(':
            paren_stack.append((i, _line_from_index(src, i)))
        elif c == ')':
            if paren_stack:
                paren_stack.pop()
            else:
                line = _line_from_index(src, i)
                col = _col_from_index(src, i)
                errors.append(_mk(i, 1, line, col, "Paréntesis de cierre ')' sin apertura."))
        elif c == '{':
            brace_stack.append((i, _line_from_index(src, i)))
        elif c == '}':
            if brace_stack:
                brace_stack.pop()
            else:
                line = _line_from_index(src, i)
                col = _col_from_index(src, i)
                errors.append(_mk(i, 1, line, col, "Llave de cierre '}' sin apertura."))
        elif c == '[':
            bracket_stack.append((i, _line_from_index(src, i)))
        elif c == ']':
            if bracket_stack:
                bracket_stack.pop()
            else:
                line = _line_from_index(src, i)
                col = _col_from_index(src, i)
                errors.append(_mk(i, 1, line, col, "Corchete de cierre ']' sin apertura."))

        i += 1

    # fin de archivo: comillas abiertas
    if in_double and double_start_idx >= 0:
        line = _line_from_index(src, double_start_idx)
        col = _col_from_index(src, double_start_idx)
        errors.append(_mk(double_start_idx, 1, line, col, 'Cadena no cerrada (falta ").'))
    if in_single and single_start_idx >= 0:
        line = _line_from_index(src, single_start_idx)
        col = _col_from_index(src, single_start_idx)
        errors.append(_mk(single_start_idx, 1, line, col, "Carácter no cerrado (falta ')."))

    # aperturas sin cierre
    for idx, _ln in paren_stack:
        errors.append(_mk(idx, 1, _line_from_index(src, idx), _col_from_index(src, idx), "Paréntesis de apertura '(' sin cierre."))
    for idx, _ln in brace_stack:
        errors.append(_mk(idx, 1, _line_from_index(src, idx), _col_from_index(src, idx), "Llave de apertura '{' sin cierre."))
    for idx, _ln in bracket_stack:
        errors.append(_mk(idx, 1, _line_from_index(src, idx), _col_from_index(src, idx), "Corchete de apertura '[' sin cierre."))

    return errors

def _scan_missing_semicolon_sout(src: str) -> List[Dict]:
    """
    Usa el lexer para detectar patrones:
        System . out . (print|println) ( ... )  [; esperado]
    Si tras el PARDER que cierra no aparece PUNTOCOMA inmediato, marca error en el ')'.
    """
    errors: List[Dict] = []
    lx = construir_lexer()
    lx.input(src)

    toks = []
    while True:
        t = lx.token()
        if not t: break
        toks.append(t)

    i = 0
    n = len(toks)

    while i < n:
        t = toks[i]
        if t.type == 'SYSTEM':
            # Expect: SYSTEM PUNTO OUT PUNTO (PRINT|PRINTLN) PARIZQ ... PARDER [PUNTOCOMA]
            if i+4 < n and toks[i+1].type == 'PUNTO' and toks[i+2].type == 'OUT' and \
               toks[i+3].type == 'PUNTO' and toks[i+4].type in ('PRINT', 'PRINTLN'):
                j = i + 5
                if j < n and toks[j].type == 'PARIZQ':
                    # saltar hasta PARDER que cierra
                    depth = 1
                    j += 1
                    while j < n and depth > 0:
                        if toks[j].type == 'PARIZQ':
                            depth += 1
                        elif toks[j].type == 'PARDER':
                            depth -= 1
                            if depth == 0:
                                break
                        j += 1
                    if j < n and toks[j].type == 'PARDER':
                        # mirar siguiente token
                        nxt = toks[j+1] if j+1 < n else None
                        if not nxt or nxt.type != 'PUNTOCOMA':
                            # error en el ) final
                            idx = toks[j].lexpos
                            line = toks[j].lineno
                            col = _col_from_index(src, idx)
                            errors.append(_mk(idx, 1, line, col, "Falta ';' después de System.out.print/println(...)."))
                        # avanzar
                        i = j + 1
                        continue
        i += 1

    return errors

def diagnose(code: str) -> List[Dict]:
    """
    Devuelve una lista de errores con:
      - start, length, line, col, message
    Cubre:
      • Desbalance de (), {}, [] y comillas
      • Falta ';' tras System.out.print/println(...)
    """
    errs: List[Dict] = []
    errs.extend(_scan_structure(code))
    errs.extend(_scan_missing_semicolon_sout(code))
    return errs
