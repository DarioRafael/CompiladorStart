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
        self.home.bt_lexico.clicked.connect(self.ev_lexico)
        self.home.bt_sintactico.clicked.connect(self.ev_sintactico)
        self.home.bt_archivo.clicked.connect(self.ev_archivo)
        self.home.bt_limpiar.clicked.connect(self.ev_limpiar)
        self.home.bt_simbolos.clicked.connect(self.mostrar_tabla_simbolos)
        self.home.bt_arbol.clicked.connect(self.generar_recorridos)
        self.home.bt_arbolLR.clicked.connect(self.generar_arbol_lr)  # respeta tu nombre de botón

        # Atajos (si existen en tu Ui_home)
        try:
            self.home.shortcut_run_lexical.activated.connect(self.ev_lexico)
            self.home.shortcut_run_syntactic.activated.connect(self.ev_sintactico)
            self.home.shortcut_open.activated.connect(self.ev_archivo)
            self.home.shortcut_clear.activated.connect(self.ev_limpiar)
            self.home.shortcut_tree.activated.connect(self.generar_recorridos)
        except Exception:
            # Si alguno no existe, simplemente lo ignoramos
            pass

        # Estado inicial
        self.home.estado.showMessage("Analizador de código Java - Desarrollado con PyQt5 y PLY")
        self.analisis_sintactico_realizado = False

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

            for i, token in enumerate(resultados):
                # Alternancia de filas
                if usar_fondo_oscuro:
                    color_fondo = QColor("#1E1E1E")
                    color_texto = QColor("#FFFFFF")
                else:
                    color_fondo = QColor("#2D2D2D")
                    color_texto = QColor("#FFFFFF")
                usar_fondo_oscuro = not usar_fondo_oscuro

                linea = str(token.get("linea", "0"))
                tipo = token.get("tipo", "DESCONOCIDO")
                valor = str(token.get("valor", ""))
                lexema = valor
                patron = self._patron_por_tipo(tipo)

                if tipo == "ERROR":
                    color_fondo = QColor("#7E2D40")
                    color_texto = QColor("#FFFFFF")

                items = [
                    QTableWidgetItem(linea),
                    QTableWidgetItem(tipo),
                    QTableWidgetItem(lexema),
                    QTableWidgetItem(patron),
                ]

                for col, it in enumerate(items):
                    it.setBackground(color_fondo)
                    it.setForeground(color_texto)
                    self.home.tb_lexico.setItem(i, col, it)

            self.home.tb_lexico.setAlternatingRowColors(False)
            self.home.tb_lexico.resizeColumnsToContents()
            self.home.estado.showMessage(f"Análisis léxico completado: {len(resultados)} tokens encontrados")
            self.home.analysisTabs.setCurrentIndex(0)

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

        simbolos = tabla_simbolos.obtener_todos()
        if not simbolos:
            self.home.estado.showMessage("No hay símbolos definidos en la tabla de símbolos")
            return

        self.home.tb_simbolos.setRowCount(len(simbolos))

        for i, (nombre, info) in enumerate(simbolos.items()):
            # Fondo blanco + texto negro (corrige el contraste)
            bg = QColor("#FFFFFF")
            fg = QColor("#FFFFFF")

            item_nombre = QTableWidgetItem(nombre)
            item_tipo = QTableWidgetItem(info.get("tipo", ""))
            item_valor = QTableWidgetItem(str(info.get("valor", "")))
            item_linea = QTableWidgetItem(str(info.get("linea", "")))
            item_alcance = QTableWidgetItem(info.get("alcance", "global"))

            items = [item_nombre, item_tipo, item_valor, item_linea, item_alcance]
            for it in items:
                it.setBackground(bg)
                it.setForeground(fg)
                f = it.font(); f.setBold(True); it.setFont(f)

            self.home.tb_simbolos.setItem(i, 0, item_nombre)
            self.home.tb_simbolos.setItem(i, 1, item_tipo)
            self.home.tb_simbolos.setItem(i, 2, item_valor)
            self.home.tb_simbolos.setItem(i, 3, item_linea)
            self.home.tb_simbolos.setItem(i, 4, item_alcance)

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
        self.home.tb_lexico.setRowCount(0)
        self.home.tx_sintactico.clear()
        self.home.tb_simbolos.setRowCount(0)
        self.home.treeWidget.clear()
        tabla_simbolos.limpiar()
        self.home.estado.showMessage("Todos los campos han sido limpiados")
        self.analisis_sintactico_realizado = False
        self.home.bt_arbol.setEnabled(True)
        self.home.bt_arbolLR.setEnabled(True)
