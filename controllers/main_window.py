# -*- coding: utf-8 -*-
import os
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QTableWidgetItem, QMessageBox, QTextEdit, QPlainTextEdit
from PyQt5.QtGui import QColor, QBrush, QFont, QTextCharFormat, QTextCursor

# Ui (tu archivo existente)
from view.home import Ui_home

# Analizadores y utilidades (tus archivos existentes)
from lexer.analizador_lexico import prueba as prueba_lexica, tabla_simbolos
from syntactic.analizador_sintactico import prueba_sintactica
from highlighters.java_highlighter import JavaHighlighter

from diagnostics.java_diagnostics import diagnose as diag_struct
from semantics.java_semantics import analyze_semantics as diag_sem
from editors.completer import JavaAutoCompleter, JAVA_KEYWORDS

# >>> Runner Java (nuevo)
from runners.java_runner import JavaRunner

# >>> Desensamblador / “ensamblador JVM” (nuevo)
from assembler.bytecode_disassembler import JavaBytecodeDisassembler


# ===============================
#   Asignador de Direcciones
# ===============================
class AddressAllocator:
    """
    Asigna direcciones simulando un runtime 64-bit:
      - GLOBAL: offsets crecientes (DATA segment)
      - STACK (por alcance/función): locales en offsets negativos desde FP
      - Parámetros (si 'categoria' == 'param'): offsets positivos desde FP
    Alineación configurable (por defecto 8).
    """
    def __init__(self, word_size=8, align=8):
        self.word_size = word_size
        self.align = align
        self.global_off = 0
        # Por cada alcance (función/bloque) tenemos un frame con contadores
        self.frames = {}  # scope -> {'locals_off': 0 (neg), 'params_off': base_pos}

        # punto de partida típico para params (depende de ABI; educativo):
        # suponemos FP+16 primer parámetro
        self.param_base = 16

    # tamaños por tipo (puedes ajustar a tu gusto/arquitectura)
    _type_sizes = {
        "INT": 4, "FLOAT": 4, "DOUBLE": 8, "BOOLEAN": 1, "CHAR": 1,
        "LONG": 8, "SHORT": 2, "BYTE": 1, "VOID": 0,
        # En Java, String/objetos son referencias (punteros) -> 8 bytes en 64-bit
        "STRING": 8, "REFERENCE": 8,
    }

    def size_of(self, tipo: str, override_bytes: int = None) -> int:
        if override_bytes is not None:
            return override_bytes
        t = (tipo or "").upper()
        return self._type_sizes.get(t, self.word_size)  # por defecto, referencia

    def _align_up(self, n: int, a: int) -> int:
        return ((n + (a - 1)) // a) * a

    def _align_down(self, n: int, a: int) -> int:
        return -self._align_up(abs(n), a)

    def _frame(self, scope: str):
        fr = self.frames.get(scope)
        if not fr:
            fr = {"locals_off": 0, "params_off": self.param_base}
            self.frames[scope] = fr
        return fr

    def _is_global(self, info: dict) -> bool:
        alc = (info.get("alcance") or "global").lower()
        return alc in ("global", "namespace", "module")

    def _is_param(self, info: dict) -> bool:
        return (info.get("categoria") or "").lower() == "param"

    def allocate(self, symbol_table: dict) -> dict:
        """
        symbol_table: dict nombre -> info (de tu tabla actual)
        Devuelve dict nombre -> {'segment': 'GLOBAL'|'STACK', 'offset': int, 'addr_str': str}
        """
        out = {}
        # Orden estable: primero globales (para que se vean ordenados bonitos)
        names = list(symbol_table.keys())
        names.sort()

        for name in names:
            info = symbol_table[name] or {}
            tipo = info.get("tipo", "")
            alcance = info.get("alcance", "global")
            override_sz = None
            if "tamaño" in info:
                try:
                    # tamaño en elementos (ej: arrays)
                    override_sz = int(info["tamaño"]) * self.size_of(tipo)
                except Exception:
                    pass

            sz = self.size_of(tipo, override_bytes=override_sz)
            sz = max(1, sz)  # nunca 0 por seguridad
            sz_al = self._align_up(sz, self.align)

            if self._is_global(info):
                # GLOBAL: offsets crecientes
                base = self._align_up(self.global_off, self.align)
                addr = f"GLOBAL+{base}"
                out[name] = {"segment": "GLOBAL", "offset": base, "addr_str": addr}
                self.global_off = base + sz_al
            else:
                # STACK por alcance
                fr = self._frame(alcance)
                if self._is_param(info):
                    # parámetros: positivos desde FP (educativo)
                    pos = self._align_up(fr["params_off"], self.align)
                    addr = f"[FP+{pos}]"
                    out[name] = {"segment": "STACK", "offset": pos, "addr_str": addr}
                    fr["params_off"] = pos + sz_al
                else:
                    # locales: negativos desde FP
                    # vamos “creciendo” hacia abajo
                    neg = fr["locals_off"] - sz_al
                    neg_al = self._align_down(neg, self.align)
                    addr = f"[FP{neg_al}]" if neg_al < 0 else f"[FP+{neg_al}]"
                    out[name] = {"segment": "STACK", "offset": neg_al, "addr_str": addr}
                    fr["locals_off"] = neg_al
        return out


class Main(QMainWindow):
    """Clase principal de la aplicación"""

    def __init__(self):
        super().__init__()

        # Instanciar la UI
        self.home = Ui_home()
        self.home.setupUi(self)

        # Resaltador de sintaxis Java
        self.highlighter = JavaHighlighter(self.home.tx_ingreso.document())

        self._last_errors = []
        self.home.tx_ingreso.textChanged.connect(self._run_live_diagnostics)
        self.home.tx_ingreso.cursorPositionChanged.connect(self._maybe_show_error_in_status)
        self.home.tx_ingreso.setTabChangesFocus(False)

        self._init_autocomplete()

        # Conectar eventos
        self.home.bt_sintactico.clicked.connect(self.ev_sintactico)
        self.home.bt_archivo.clicked.connect(self.ev_archivo)
        self.home.bt_limpiar.clicked.connect(self.ev_limpiar)
        self.home.bt_arbol.clicked.connect(self.generar_recorridos)
        self.home.bt_arbolLR.clicked.connect(self.generar_arbol_lr)  # respeta tu nombre de botón
        self.home.bt_zoom_in.clicked.connect(self.home.tx_ingreso.zoom_in)
        self.home.bt_zoom_out.clicked.connect(self.home.tx_ingreso.zoom_out)

        # Atajos (si existen en tu Ui_home)
        try:
            self.home.shortcut_run_syntactic.activated.connect(self.ev_sintactico)
            self.home.shortcut_open.activated.connect(self.ev_archivo)
            self.home.shortcut_clear.activated.connect(self.ev_limpiar)
            self.home.shortcut_tree.activated.connect(self.generar_recorridos)
        except Exception:
            # Si alguno no existe, simplemente lo ignoramos
            pass

        # --- Runner Java (integración completa) ---
        self.runner = JavaRunner(parent=self)
        self.runner.started.connect(self._on_runner_started)   # "compile" | "run"
        self.runner.output.connect(self._append_output)        # stdout/stderr
        self.runner.finished.connect(self._on_runner_finished) # exit code
        self.runner.error.connect(self._on_runner_error)       # errores de preparación

        # Click en Run => compilar/ejecutar
        self.home.bt_run.clicked.connect(self._on_run_clicked)

        # --- Assembler / javap (integración completa) ---
        self.asm = JavaBytecodeDisassembler(parent=self)

        # Señales -> UI
        self.asm.started.connect(self._on_asm_started)       # "compile" | "disasm"
        self.asm.output.connect(self._append_asm_stream)     # stdout/stderr en vivo
        self.asm.result.connect(self._set_asm_full_listing)  # listado final completo
        self.asm.error.connect(self._on_asm_error)           # errores de preparación
        self.asm.finished.connect(self._on_asm_finished)     # exit code

        # Botón Ensamblador / atajos
        try:
            self.home.bt_asm.clicked.connect(self._on_generate_asm)
        except Exception:
            pass
        try:
            self.home.bt_asm_clear.clicked.connect(lambda: self.home.tx_asm.clear())
        except Exception:
            pass
        try:
            self.home.shortcut_asm.activated.connect(self._on_generate_asm)
        except Exception:
            pass

        # Estado inicial
        self.home.estado.showMessage("Analizador de código Java - Desarrollado con PyQt5 y PLY")
        self.analisis_sintactico_realizado = False

    # =======================
    #   RUN / OUTPUT HANDLERS
    # =======================
    def _on_run_clicked(self):
        code = self.home.tx_ingreso.toPlainText().strip()
        if not code:
            QMessageBox.warning(self, "Advertencia", "No hay código para ejecutar.")
            return

        # Ir a la pestaña de salida y limpiar consola
        try:
            self.home.analysisTabs.setCurrentWidget(self.home.outputTab)
            self.home.tx_output.clear()
            self.home.lb_output_status.setText("Compilando y ejecutando...")
        except Exception:
            pass  # por si aún no existe la pestaña (aunque en tu Ui sí existe)

        # Deshabilitar Run mientras compila/ejecuta
        self.home.bt_run.setEnabled(False)
        self.home.estado.showMessage("Preparando ejecución...")

        # Ejecutar (estructura simple: un archivo, sin package, con public class y main)
        self.runner.run_code(code)

    def _on_runner_started(self, stage: str):
        # stage: "compile" o "run"
        try:
            self.home.analysisTabs.setCurrentWidget(self.home.outputTab)
            self.home.lb_output_status.setText("Compilando..." if stage == "compile" else "Ejecutando...")
        except Exception:
            pass
        self.home.estado.showMessage("Compilando..." if stage == "compile" else "Ejecutando...")

    def _append_output(self, text: str):
        try:
            self.home.tx_output.moveCursor(QTextCursor.End)
            self.home.tx_output.insertPlainText(text)
            self.home.tx_output.moveCursor(QTextCursor.End)
        except Exception:
            pass

    def _on_runner_finished(self, code: int):
        self.home.bt_run.setEnabled(True)
        if code == 0:
            self.home.estado.showMessage("Ejecución finalizada correctamente.", 5000)
            try:
                self.home.lb_output_status.setText("Finalizado.")
            except Exception:
                pass
        else:
            self.home.estado.showMessage(f"Finalizado con errores (código {code}).", 5000)
            try:
                self.home.lb_output_status.setText(f"Finalizado con errores (código {code}).")
            except Exception:
                pass

    def _on_runner_error(self, message: str):
        self.home.bt_run.setEnabled(True)
        try:
            self.home.analysisTabs.setCurrentWidget(self.home.outputTab)
            self.home.lb_output_status.setText("Error")
            self.home.tx_output.appendPlainText(f"[ERROR] {message}\n")
        except Exception:
            pass
        self.home.estado.showMessage("Error al preparar/ejecutar.", 5000)

    # =======================
    #   ASM / DISASSEMBLER
    # =======================
    def _on_generate_asm(self):
        code = self.home.tx_ingreso.toPlainText().strip()
        if not code:
            QMessageBox.warning(self, "Advertencia", "No hay código para ensamblar.")
            return

        # Ir a la pestaña de ensamblador y limpiar consola ASM
        try:
            self.home.analysisTabs.setCurrentWidget(self.home.asmTab)
            self.home.tx_asm.clear()
            self.home.lb_asm_status.setText("Compilando y desensamblando...")
        except Exception:
            pass

        # Deshabilitar botón mientras corre
        try:
            self.home.bt_asm.setEnabled(False)
        except Exception:
            pass
        self.home.estado.showMessage("Preparando desensamblado (javac + javap)...")

        # Ejecutar pipeline (javac -> javap)
        self.asm.disassemble(code)

    def _on_asm_started(self, stage: str):
        # stage: "compile" o "disasm"
        try:
            self.home.analysisTabs.setCurrentWidget(self.home.asmTab)
            self.home.lb_asm_status.setText("Compilando..." if stage == "compile" else "Ensamblando...")
        except Exception:
            pass
        self.home.estado.showMessage("Compilando..." if stage == "compile" else "Generando código ensamblador...")

    def _append_asm_stream(self, text: str):
        # flujo en vivo (stdout/stderr) mientras corre
        try:
            self.home.tx_asm.moveCursor(QTextCursor.End)
            self.home.tx_asm.insertPlainText(text)
            self.home.tx_asm.moveCursor(QTextCursor.End)
        except Exception:
            pass

    def _set_asm_full_listing(self, listing: str):
        # listado completo de javap (cuando termina ok)
        try:
            self.home.tx_asm.setPlainText(listing)
            self.home.tx_asm.moveCursor(QTextCursor.Start)
        except Exception:
            pass

    def _on_asm_error(self, message: str):
        try:
            self.home.analysisTabs.setCurrentWidget(self.home.asmTab)
            self.home.lb_asm_status.setText("Error")
            self.home.tx_asm.appendPlainText(f"[ERROR] {message}\n")
        except Exception:
            pass
        self.home.estado.showMessage("Error al generar ensamblador.", 5000)

    def _on_asm_finished(self, code: int):
        try:
            self.home.bt_asm.setEnabled(True)
        except Exception:
            pass

        if code == 0:
            self.home.estado.showMessage("Código ensamblador generado correctamente.", 5000)
            try:
                self.home.lb_asm_status.setText("Finalizado.")
            except Exception:
                pass
        else:
            self.home.estado.showMessage(f"Desensamblado finalizado con errores (código {code}).", 5000)
            try:
                self.home.lb_asm_status.setText(f"Finalizado con errores (código {code}).")
            except Exception:
                pass

    # -----------------------------
    # Utilidad: expresión por tipo
    # -----------------------------
    @staticmethod
    def _patron_por_tipo(tipo: str) -> str:
        patrones = {
            "IDENTIFICADOR": r"[a-zA-Z_][a-zA-Z_0-9]*",
            "ENTERO": r"\d+",
            "DECIMAL": r"\d+\.\d+",
            "CADENA": r"\"[^\"]*\"",
            "CARACTER": r"'[^']'",
            "SUMA": r"\+",
            "RESTA": r"-",
            "MULT": r"\*",
            "DIV": r"/",
            "MODULO": r"%",
            "INCREMENTO": r"\+\+",
            "DECREMENTO": r"--",
            "ASIGNAR": r"=",
            "IGUAL": r"==",
            "MENORQUE": r"<",
            "MAYORQUE": r">",
            "MENORIGUAL": r"<=",
            "MAYORIGUAL": r">=",
            "DISTINTO": r"!=",
            "AND": r"&&",
            "OR": r"\|\|",
            "NOT": r"!",
            "PARIZQ": r"\(",
            "PARDER": r"\)",
            "LLAIZQ": r"{",
            "LLADER": r"}",
            "CORIZQ": r"\[",
            "CORDER": r"\]",
            "PUNTOCOMA": r";",
            "COMA": r",",
            "PUNTO": r"\.",
        }
        palabras_reservadas = {
            "CLASS", "PUBLIC", "PRIVATE", "PROTECTED", "STATIC", "FINAL",
            "VOID", "INT", "FLOAT", "DOUBLE", "BOOLEAN", "CHAR", "STRING",
            "IF", "ELSE", "FOR", "WHILE", "DO", "SWITCH", "CASE", "DEFAULT",
            "BREAK", "CONTINUE", "RETURN", "SYSTEM", "OUT", "PRINTLN", "PRINT"
        }
        if tipo in palabras_reservadas:
            return "Palabra reservada"
        return patrones.get(tipo, "Desconocido")

    # -----------------------------
    # Análisis léxico
    # -----------------------------
    def ev_lexico(self):
        self.home.tb_lexico.setRowCount(0)
        codigo = self.home.tx_ingreso.toPlainText().strip()

        if not codigo:
            QMessageBox.warning(self, "Advertencia", "No hay código para analizar.")
            return

        try:
            tabla_simbolos.limpiar()
            resultados = prueba_lexica(codigo)

            self.home.tb_lexico.setRowCount(len(resultados))
            usar_fondo_oscuro = True

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error durante el análisis léxico: {str(e)}")
            self.home.estado.showMessage(f"Error: {str(e)}")

    # -----------------------------
    # Análisis sintáctico
    # -----------------------------
    def ev_sintactico(self):
        """Ejecuta pre-diagnóstico (estructural+semántico) y luego el análisis sintáctico PLY."""
        # Limpiar panel de salida sintáctica
        self.home.tx_sintactico.clear()

        # Obtener código
        codigo = self.home.tx_ingreso.toPlainText().strip()
        if not codigo:
            QMessageBox.warning(self, "Advertencia", "No hay código para analizar.")
            return

        # ====== Pre-chequeo estructural + semántico (subraya y bloquea si hay errores) ======
        pre = []
        try:
            pre.extend(diag_struct(codigo))  # (), {}, [], "..." y '...', /*...*/
        except Exception:
            pass
        try:
            pre.extend(diag_sem(codigo))  # redeclaración, uso no declarado, tipos incompatibles, etc.
        except Exception:
            pass

        if pre:
            # pinta subrayado rojo
            self._last_errors = pre
            self._apply_diagnostics(pre)
            # marcas en gutter si tu editors lo soporta
            try:
                if hasattr(self.home.tx_ingreso, "set_error_lines"):
                    self.home.tx_ingreso.set_error_lines(sorted({e["line"] for e in pre}))
            except Exception:
                pass

            # listar en el panel sintáctico
            html = "<html><body style='color:#DCDCDC; font-family: Consolas, monospace;'>"
            for e in pre:
                html += f"<p style='color:#FF6B68;'>Error (L{e['line']}:C{e['col']}). {e['message']}</p>"
            html += "</body></html>"
            self.home.tx_sintactico.setHtml(html)

            # bloquear árboles y marcar estado
            self.analisis_sintactico_realizado = False
            self.home.bt_arbol.setEnabled(False)
            self.home.bt_arbolLR.setEnabled(False)
            self.home.estado.showMessage("Errores detectados en diagnóstico previo. Corrige y vuelve a intentar.")
            self.home.analysisTabs.setCurrentIndex(1)
            return
        # =====================================================================

        # Si llegamos aquí, no hubo errores previos: limpiar subrayados/gutter
        self._last_errors = []
        self._apply_diagnostics([])
        try:
            if hasattr(self.home.tx_ingreso, "set_error_lines"):
                self.home.tx_ingreso.set_error_lines([])
        except Exception:
            pass

        # ====== Análisis sintáctico PLY (tu flujo original) ======
        try:
            tabla_simbolos.limpiar()
            resultados = prueba_sintactica(codigo)

            html_output = "<html><body style='color:#DCDCDC; font-family: Consolas, monospace;'>"
            for item in resultados:
                if "Error" in item:
                    html_output += f"<p style='color:#FF6B68;'>{item}</p>"
                elif "Advertencia" in item:
                    html_output += f"<p style='color:#FFA500;'>{item}</p>"
                else:
                    html_output += f"<p>{item}</p>"
            html_output += "</body></html>"
            self.home.tx_sintactico.setHtml(html_output)

            tiene_errores = any("Error" in item for item in resultados)
            self.analisis_sintactico_realizado = not tiene_errores

            # habilitar/bloquear botones de árbol
            self.home.bt_arbol.setEnabled(self.analisis_sintactico_realizado)
            self.home.bt_arbolLR.setEnabled(self.analisis_sintactico_realizado)

            if tiene_errores:
                self.home.estado.showMessage(
                    "Análisis sintáctico completado con errores. No se pueden generar árboles."
                )
            else:
                self.home.estado.showMessage(
                    "Análisis sintáctico completado correctamente. Puede generar los árboles."
                )

            self.home.analysisTabs.setCurrentIndex(1)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error durante el análisis sintáctico: {str(e)}")
            self.home.estado.showMessage(f"Error: {str(e)}")
            self.analisis_sintactico_realizado = False
            self.home.bt_arbol.setEnabled(False)
            self.home.bt_arbolLR.setEnabled(False)

    # -----------------------------
    # Recorridos del árbol (Pre/In/Post)
    # -----------------------------
    def generar_recorridos(self):
        codigo = self.home.tx_ingreso.toPlainText().strip()
        if not codigo:
            QMessageBox.warning(self, "Advertencia", "No hay código para analizar.")
            return

        if not self.analisis_sintactico_realizado:
            resp = QMessageBox.question(
                self,
                "Realizar análisis sintáctico",
                "Es necesario realizar un análisis sintáctico antes de generar los recorridos. ¿Desea hacerlo ahora?",
                QMessageBox.Yes | QMessageBox.No
            )
            if resp == QMessageBox.Yes:
                self.ev_sintactico()
                if not self.analisis_sintactico_realizado:
                    return
            else:
                return

        self.home.treeWidget.clear()
        self.home.treeWidget.setHeaderLabel("Recorridos del Árbol")
        header_font = QFont("Consolas", 12, QFont.Bold)
        self.home.treeWidget.headerItem().setFont(0, header_font)
        self.home.treeWidget.headerItem().setForeground(0, QBrush(QColor('#F89406')))

        try:
            from trees.recorridos_arbol import visualizar_recorridos_arbol  # tu archivo existente
            ok = visualizar_recorridos_arbol(codigo, self.home.treeWidget)
            if not ok:
                QMessageBox.warning(
                    self,
                    "Error al generar recorridos",
                    "No se pudieron generar los recorridos debido a errores sintácticos."
                )
                return

            self.home.analysisTabs.setCurrentIndex(3)
            self.home.estado.showMessage(
                "Recorridos del árbol generados correctamente (Pre-orden, In-orden, Post-orden)"
            )
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al generar los recorridos del árbol: {str(e)}")
            self.home.estado.showMessage(f"Error: {str(e)}")

    # -----------------------------
    # Árbol LR (o árbol jerárquico)
    # -----------------------------
    def generar_arbol_lr(self):
        codigo = self.home.tx_ingreso.toPlainText().strip()
        if not codigo:
            QMessageBox.warning(self, "Advertencia", "No hay código para analizar.")
            return

        if not self.analisis_sintactico_realizado:
            resp = QMessageBox.question(
                self,
                "Realizar análisis sintáctico",
                "Es necesario realizar un análisis sintáctico antes de generar los árboles. ¿Desea hacerlo ahora?",
                QMessageBox.Yes | QMessageBox.No
            )
            if resp == QMessageBox.Yes:
                self.ev_sintactico()
                if not self.analisis_sintactico_realizado:
                    return
            else:
                return

        try:
            from trees.arbol_visual import mostrar_arbol_recorridos  # tu archivo existente
            ok = mostrar_arbol_recorridos(codigo, self)
            if not ok:
                QMessageBox.warning(
                    self,
                    "Error al generar árbol",
                    "No se pudo generar el árbol debido a errores en el código."
                )
                return

            self.home.estado.showMessage("Árbol generado correctamente.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al generar el árbol: {str(e)}")
            self.home.estado.showMessage(f"Error: {str(e)}")

    # -----------------------------
    # Tabla de símbolos
    # -----------------------------
    def mostrar_tabla_simbolos(self):
        self.home.tb_simbolos.setRowCount(0)
        self.home.tb_simbolos.setAlternatingRowColors(False)

        simbolos = tabla_simbolos.obtener_todos()  # dict nombre -> info
        if not simbolos:
            self.home.estado.showMessage("No hay símbolos definidos en la tabla de símbolos")
            return

        # 1) Asignar direcciones
        allocator = AddressAllocator(word_size=8, align=8)  # “realista” 64-bit
        addr_map = allocator.allocate(simbolos)  # nombre -> {addr_str, ...}

        # 2) Pintar tabla
        self.home.tb_simbolos.setRowCount(len(simbolos))

        # Estilo legible (fondo oscuro, texto claro)
        bg = QColor("#1E1E1E")
        fg = QColor("#DCDCDC")

        # Orden consistente
        names = list(simbolos.keys())
        names.sort()

        for i, nombre in enumerate(names):
            info = simbolos[nombre]
            tipo = info.get("tipo", "")
            valor = str(info.get("valor", ""))
            linea = str(info.get("linea", ""))
            alcance = info.get("alcance", "global")
            addr_str = addr_map.get(nombre, {}).get("addr_str", "")

            items = [
                QTableWidgetItem(nombre),
                QTableWidgetItem(tipo),
                QTableWidgetItem(valor),
                QTableWidgetItem(linea),
                QTableWidgetItem(alcance),
                QTableWidgetItem(addr_str),
            ]
            for col, it in enumerate(items):
                it.setBackground(bg)
                it.setForeground(fg)
                f = it.font()
                f.setBold(True)
                it.setFont(f)
                self.home.tb_simbolos.setItem(i, col, it)

        self.home.tb_simbolos.resizeColumnsToContents()
        self.home.estado.showMessage(f"Tabla de símbolos: {len(simbolos)} símbolos encontrados")
        self.home.analysisTabs.setCurrentIndex(2)

    def _apply_diagnostics(self, errors):
        edit = self.home.tx_ingreso
        selections = []

        fmt = QTextCharFormat()
        fmt.setUnderlineColor(QColor("#FF4D4D"))
        fmt.setUnderlineStyle(QTextCharFormat.WaveUnderline)

        doc = edit.document()
        for e in errors:
            start = max(0, min(e["start"], doc.characterCount() - 1))
            length = max(1, min(e["length"], doc.characterCount() - start - 1))

            cur = QTextCursor(doc)
            cur.setPosition(start)
            cur.setPosition(start + length, QTextCursor.KeepAnchor)

            sel = QTextEdit.ExtraSelection()  # ✅ siempre esta clase
            sel.cursor = cur
            sel.format = fmt
            selections.append(sel)

        # deja que CodeEditor componga con sus propios highlights
        try:
            edit.setExtraSelections(selections)
        except Exception:
            edit.setExtraSelections(selections)

    def _run_live_diagnostics(self):
        code = self.home.tx_ingreso.toPlainText()
        errs = []
        try:
            errs.extend(diag_struct(code))
        except Exception:
            pass
        try:
            errs.extend(diag_sem(code))
        except Exception:
            pass

        self._last_errors = errs
        self._apply_diagnostics(errs)

        # marcas en gutter si tu editors lo soporta
        try:
            if hasattr(self.home.tx_ingreso, "set_error_lines"):
                self.home.tx_ingreso.set_error_lines(sorted({e["line"] for e in errs}))
        except Exception:
            pass

        if errs:
            self.home.estado.showMessage(f"{len(errs)} problemas detectados.")
        else:
            self.home.estado.showMessage("Sin problemas.")

    def _maybe_show_error_in_status(self):
        edit = self.home.tx_ingreso
        pos = edit.textCursor().position()
        for e in self._last_errors:
            if e["start"] <= pos <= e["start"] + e["length"]:
                self.home.estado.showMessage(f"Error (L{e['line']}:C{e['col']}): {e['message']}")
                return

    def _init_autocomplete(self):
        # función que aporta palabras dinámicas (variables y métodos) desde la tabla de símbolos
        def dynamic_words():
            try:
                syms = tabla_simbolos.obtener_todos()  # dict {nombre: info}
                # nombres "limpios" (sin prefijo global. si tu tabla usa 'global.X', recórtalo)
                out = []
                for k in syms.keys():
                    # si viniera con "scope.nombre", quita el prefijo para autocompletar
                    name = k.split('.', 1)[1] if '.' in k else k
                    out.append(name)
                # agrega también palabras reservadas por si la tabla está vacía
                out.extend(JAVA_KEYWORDS)
                # únicos
                out = list(dict.fromkeys(out))
                return out
            except Exception:
                return list(JAVA_KEYWORDS)

        self._completer = JavaAutoCompleter(self.home.tx_ingreso, dynamic_words)

    # -----------------------------
    # Archivo / Limpiar
    # -----------------------------
    def ev_archivo(self):
        opciones = QFileDialog.Options()
        nombre_archivo, _ = QFileDialog.getOpenFileName(
            self,
            "Abrir Archivo Java",
            "test_programs",  # Relative path from project root
            "Archivos Texto (*.txt);;Archivos de Java (*.java);;Todos los archivos (*)",
            options=opciones
        )

        if nombre_archivo:
            try:
                with open(nombre_archivo, 'r', encoding='utf-8') as f:
                    contenido = f.read()
                    self.home.tx_ingreso.setPlainText(contenido)
                self.home.estado.showMessage(f"Archivo cargado: {os.path.basename(nombre_archivo)}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo abrir el archivo: {str(e)}")

    def ev_limpiar(self):
        self.home.tx_ingreso.clear()
        self.home.lb_output_status.clear()
        self.home.tb_lexico.setRowCount(0)
        self.home.tx_sintactico.clear()
        self.home.tb_simbolos.setRowCount(0)
        self.home.treeWidget.clear()
        tabla_simbolos.limpiar()
        self.home.estado.showMessage("Todos los campos han sido limpiados")
        self.analisis_sintactico_realizado = False
        self.home.bt_arbol.setEnabled(True)
        self.home.bt_arbolLR.setEnabled(True)
