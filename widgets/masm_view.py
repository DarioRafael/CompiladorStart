# widgets/masm_view.py
# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtGui, QtWidgets

class MasmOutputView(QtWidgets.QWidget):
    """
    Vista dividida para MASM:
      izquierda: código MASM plano (QPlainTextEdit)
      derecha:   splitter vertical con tabla de instrucciones + tabla de registros
    """
    def __init__(self, crear_tabla_fn, parent=None):
        super().__init__(parent)
        self._crear_tabla = crear_tabla_fn
        self._build_ui()

    def _build_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.splitH = QtWidgets.QSplitter(QtCore.Qt.Horizontal, self)
        self.splitH.setChildrenCollapsible(False)

        # --- Izquierda (MASM plano)
        left = QtWidgets.QWidget()
        left_layout = QtWidgets.QVBoxLayout(left)
        left_layout.setContentsMargins(0, 0, 0, 0)

        header_left = QtWidgets.QHBoxLayout()
        self.lb_left = QtWidgets.QLabel("Código MASM (Plano):")
        self.lb_left.setStyleSheet("QLabel { color: #F0AD4E; }")
        self.bt_left_clear = QtWidgets.QPushButton("Limpiar")
        self.bt_left_clear.setIcon(QtGui.QIcon.fromTheme("edit-clear"))
        header_left.addWidget(self.lb_left)
        header_left.addStretch()
        header_left.addWidget(self.bt_left_clear)
        left_layout.addLayout(header_left)

        self.tx_masm_plain = QtWidgets.QPlainTextEdit()
        f = self.tx_masm_plain.font(); f.setPointSize(16)
        self.tx_masm_plain.setFont(f)
        self.tx_masm_plain.setPlaceholderText("; Escribe/pega aquí tu MASM...")
        left_layout.addWidget(self.tx_masm_plain)

        self.bt_left_clear.clicked.connect(self.tx_masm_plain.clear)

        # --- Derecha (vertical: tabla instrucciones / registros)
        right = QtWidgets.QSplitter(QtCore.Qt.Vertical, self)
        right.setChildrenCollapsible(False)

        # Arriba: tabla MASM
        top_w = QtWidgets.QWidget()
        top_l = QtWidgets.QVBoxLayout(top_w)
        top_l.setContentsMargins(0, 0, 0, 0)

        hdr_top = QtWidgets.QHBoxLayout()
        self.lb_masm_status = QtWidgets.QLabel("Tabla de Ensamblador MASM:")
        self.lb_masm_status.setStyleSheet("QLabel { color: #F0AD4E; }")
        self.bt_masm_clear = QtWidgets.QPushButton("Limpiar tabla")
        self.bt_masm_clear.setIcon(QtGui.QIcon.fromTheme("edit-clear"))
        hdr_top.addWidget(self.lb_masm_status)
        hdr_top.addStretch()
        hdr_top.addWidget(self.bt_masm_clear)
        top_l.addLayout(hdr_top)

        self.tb_masm = self._crear_tabla(
            5, ["Dirección", "Etiqueta", "Mnemónico", "Operandos", "Comentario"]
        )
        h = self.tb_masm.horizontalHeader()
        h.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        h.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        h.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
        h.setSectionResizeMode(3, QtWidgets.QHeaderView.Stretch)
        h.setSectionResizeMode(4, QtWidgets.QHeaderView.Stretch)
        top_l.addWidget(self.tb_masm)
        self.bt_masm_clear.clicked.connect(lambda: self.tb_masm.setRowCount(0))

        # Abajo: tabla registros
        bottom_w = QtWidgets.QWidget()
        bottom_l = QtWidgets.QVBoxLayout(bottom_w)
        bottom_l.setContentsMargins(0, 0, 0, 0)

        hdr_regs = QtWidgets.QHBoxLayout()
        self.lb_regs = QtWidgets.QLabel("Registros:")
        self.lb_regs.setStyleSheet("QLabel { color: #F0AD4E; }")
        self.bt_regs_clear = QtWidgets.QPushButton("Limpiar registros")
        self.bt_regs_clear.setIcon(QtGui.QIcon.fromTheme("edit-clear"))
        hdr_regs.addWidget(self.lb_regs)
        hdr_regs.addStretch()
        hdr_regs.addWidget(self.bt_regs_clear)
        bottom_l.addLayout(hdr_regs)

        self.tb_regs = self._crear_tabla(3, ["Registro", "Valor (Hex)", "Valor (Dec)"])
        hr = self.tb_regs.horizontalHeader()
        hr.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        hr.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        hr.setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)
        bottom_l.addWidget(self.tb_regs)
        self.bt_regs_clear.clicked.connect(lambda: self.tb_regs.setRowCount(0))

        right.addWidget(top_w)
        right.addWidget(bottom_w)
        right.setSizes([300, 200])

        self.splitH.addWidget(left)
        self.splitH.addWidget(right)
        self.splitH.setSizes([600, 600])

        layout.addWidget(self.splitH)

    # -------- API pública --------
    def set_plain_code(self, text: str):
        self.tx_masm_plain.setPlainText(text or "")

    def load_masm_rows(self, rows):
        self.tb_masm.setUpdatesEnabled(False)
        self.tb_masm.clearContents()
        self.tb_masm.setRowCount(len(rows))
        for i, (addr, label, mn, ops, cmt) in enumerate(rows):
            items = [
                QtWidgets.QTableWidgetItem(addr),
                QtWidgets.QTableWidgetItem(label),
                QtWidgets.QTableWidgetItem(mn),
                QtWidgets.QTableWidgetItem(ops),
                QtWidgets.QTableWidgetItem(cmt),
            ]
            for j, it in enumerate(items):
                it.setTextAlignment(QtCore.Qt.AlignCenter)
                if j == 1 and label:
                    it.setForeground(QtGui.QColor("#61AFEF"))   # etiqueta
                if j == 2:
                    it.setForeground(QtGui.QColor("#E5C07B"))   # mnemónico
                self.tb_masm.setItem(i, j, it)
        self.tb_masm.setUpdatesEnabled(True)

    def load_registers(self, reg_map):
        self.tb_regs.setUpdatesEnabled(False)
        self.tb_regs.clearContents()
        regs = list(reg_map.items())
        self.tb_regs.setRowCount(len(regs))
        for i, (name, val) in enumerate(regs):
            if isinstance(val, int):
                hexv = f"0x{val:08X}"
                decv = str(val)
            else:
                try:
                    iv = int(val)
                    hexv = f"0x{iv:08X}"
                    decv = str(iv)
                except Exception:
                    hexv, decv = str(val), "-"
            it0 = QtWidgets.QTableWidgetItem(name); it0.setForeground(QtGui.QColor("#4EC9B0"))
            it1 = QtWidgets.QTableWidgetItem(hexv)
            it2 = QtWidgets.QTableWidgetItem(decv)
            for it in (it0, it1, it2):
                it.setTextAlignment(QtCore.Qt.AlignCenter)
            self.tb_regs.setItem(i, 0, it0)
            self.tb_regs.setItem(i, 1, it1)
            self.tb_regs.setItem(i, 2, it2)
        self.tb_regs.setUpdatesEnabled(True)

    def clear_all(self):
        self.tx_masm_plain.clear()
        self.tb_masm.setRowCount(0)
        self.tb_regs.setRowCount(0)

    # ------------------------------------------------------------------
    # Factorial (sustituye al demo). demo_fill delega a factorial_fill.
    # ------------------------------------------------------------------
    def demo_fill(self):
        # por si quedó alguna llamada antigua
        self.factorial_fill()

    def factorial_fill(self, numero: int = 5):
        """
        Factorial demo (dinámico):
          numero     -> [BP-08]
          i          -> [BP-0C]
          factorial  -> [BP-10]
        Llena MASM plano, la tabla y los registros usando el 'numero' recibido.
        """
        # --- sanitizar y calcular resultado (AX guarda el low 16-bit como en 8086)
        try:
            n = int(numero)
        except Exception:
            n = 5
        n = max(0, n)

        fact = 1
        for i in range(1, n + 1):
            fact = (fact * i) & 0xFFFF  # imitar que solo AX se conserva

        # --- 1) MASM plano
        masm_plain = (
            "; --------- Factorial (demo) ---------\n"
            ".MODEL SMALL\n"
            ".STACK 100h\n"
            ".DATA\n"
            "msg  DB 'El factorial es: $'\n"
            ".CODE\n"
            "main PROC\n"
            "    ; prologo\n"
            "    push bp\n"
            "    mov  bp, sp\n"
            "    sub  sp, 16            ; locals (hasta [BP-10])\n"
            "\n"
            f"    ; numero = {n}  (en [BP-08])\n"
            f"    mov  ax, {n}\n"
            "    mov  [bp-08], ax       ; numero\n"
            "\n"
            "    ; factorial = 1  (en [BP-10])\n"
            "    mov  ax, 1\n"
            "    mov  [bp-10], ax       ; factorial\n"
            "\n"
            "    ; i = 1  (en [BP-0C])\n"
            "    mov  ax, 1\n"
            "    mov  [bp-0C], ax       ; i\n"
            "\n"
            "L0:\n"
            "    ; while (i <= numero)\n"
            "    mov  ax, [bp-0C]       ; i\n"
            "    cmp  ax, [bp-08]       ; numero\n"
            "    jg   L1\n"
            "\n"
            "    ; factorial *= i\n"
            "    mov  ax, [bp-10]\n"
            "    imul word ptr [bp-0C]\n"
            "    mov  [bp-10], ax\n"
            "\n"
            "    ; i++\n"
            "    mov  ax, [bp-0C]\n"
            "    add  ax, 1\n"
            "    mov  [bp-0C], ax\n"
            "    jmp  L0\n"
            "\n"
            "L1:\n"
            "    ; (demo) imprimir texto fijo\n"
            "    mov  ax, @data\n"
            "    mov  ds, ax\n"
            "    lea  dx, msg\n"
            "    mov  ah, 09h\n"
            "    int  21h\n"
            "\n"
            "    ; epilogo\n"
            "    mov  sp, bp\n"
            "    pop  bp\n"
            "    ret\n"
            "main ENDP\n"
            "END main\n"
        )
        self.set_plain_code(masm_plain)

        # --- 2) Tabla de instrucciones (solo cambia el mov ax, <n>)
        rows = [
            ["00401000", "main", "push", "bp", "; prologo"],
            ["00401001", "", "mov", "bp, sp", ""],
            ["00401003", "", "sub", "sp, 16", "; locals (hasta [BP-10])"],
            ["00401006", "", "mov", f"ax, {n}", ""],
            ["00401008", "", "mov", "[bp-08], ax", "; numero"],
            ["0040100B", "", "mov", "ax, 1", ""],
            ["0040100D", "", "mov", "[bp-10], ax", "; factorial"],
            ["00401010", "", "mov", "ax, 1", ""],
            ["00401012", "", "mov", "[bp-0C], ax", "; i"],
            ["00401015", "L0", "mov", "ax, [bp-0C]", "; i"],
            ["00401018", "", "cmp", "ax, [bp-08]", "; numero"],
            ["0040101B", "", "jg", "L1", ""],
            ["0040101D", "", "mov", "ax, [bp-10]", "; factorial"],
            ["00401020", "", "imul", "word ptr [bp-0C]", "; * i"],
            ["00401023", "", "mov", "[bp-10], ax", "; factorial"],
            ["00401026", "", "mov", "ax, [bp-0C]", "; i"],
            ["00401029", "", "add", "ax, 1", ""],
            ["0040102B", "", "mov", "[bp-0C], ax", "; i"],
            ["0040102E", "", "jmp", "L0", ""],
            ["00401030", "L1", "mov", "ax, @data", ""],
            ["00401033", "", "mov", "ds, ax", ""],
            ["00401035", "", "lea", "dx, msg", ""],
            ["00401038", "", "mov", "ah, 09h", ""],
            ["0040103A", "", "int", "21h", ""],
            ["0040103C", "", "mov", "sp, bp", "; epilogo"],
            ["0040103E", "", "pop", "bp", ""],
            ["0040103F", "", "ret", "", ""],
        ]
        self.load_masm_rows(rows)

        # --- 3) Registros (AX = factorial(n) & 0xFFFF para imitar 16-bit)
        regs = {
            "AX": fact,
            "BX": 0,
            "CX": 0,
            "DX": 0,
            "SI": 0,
            "DI": 0,
            "BP": 0xFF00,  # ficticios para formato
            "SP": 0xFEF0,
        }
        self.load_registers(regs)
