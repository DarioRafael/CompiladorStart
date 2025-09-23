# ===== añade en Ui_home =====

def ensamblar_masm(self):
    """Genera el ejemplo MASM del factorial y llena el panel integrado."""
    try:
        self._masm_factorial_demo()  # nuevo
        self.analysisTabs.setCurrentWidget(self.masmTab)
        self.estado.showMessage("MASM (factorial) generado.", 3000)
    except Exception as e:
        import traceback; traceback.print_exc()
        self.estado.showMessage(f"Error al preparar MASM: {e}", 5000)

def _masm_factorial_demo(self):
    """
    Demo: Factorial en MASM (16 bits estilo .MODEL SMALL).
    Mapea variables a offsets del frame usando tu tabla:
      numero    -> [FP-0x08]
      factorial -> [FP-0x10]
      i         -> [FP-0x0C]   (intermedio entre ambos)
    """
    # --- MASM plano (izquierda)
    masm_plain = (
        "; --------- Factorial (demo) ---------\n"
        ".MODEL SMALL\n"
        ".STACK 100h\n"
        ".DATA\n"
        "msg  DB 'El factorial es: $'\n"
        ".CODE\n"
        "main PROC\n"
        "    ; prólogo\n"
        "    push bp\n"
        "    mov  bp, sp\n"
        "    sub  sp, 16           ; reserva locals (simbolos: main.main = [FP-10])\n"
        "\n"
        "    ; numero = 5  (en [bp-08])\n"
        "    mov  ax, 5\n"
        "    mov  [bp-08], ax      ; numero (tabla: main.args = [FP-08])\n"
        "\n"
        "    ; factorial = 1  (en [bp-10])\n"
        "    mov  ax, 1\n"
        "    mov  [bp-10], ax      ; factorial (tabla: main.main = [FP-10])\n"
        "\n"
        "    ; i = 1  (en [bp-0C])\n"
        "    mov  ax, 1\n"
        "    mov  [bp-0C], ax\n"
        "\n"
        "L0:\n"
        "    ; if (i <= numero) ?\n"
        "    mov  ax, [bp-0C]      ; i\n"
        "    cmp  ax, [bp-08]      ; numero\n"
        "    jg   L1\n"
        "\n"
        "    ; factorial = factorial * i\n"
        "    mov  ax, [bp-10]\n"
        "    imul word ptr [bp-0C]\n"
        "    mov  [bp-10], ax\n"
        "\n"
        "    ; i = i + 1\n"
        "    mov  ax, [bp-0C]\n"
        "    add  ax, 1\n"
        "    mov  [bp-0C], ax\n"
        "    jmp  L0\n"
        "\n"
        "L1:\n"
        "    ; mostrar mensaje (solo demo)\n"
        "    mov  ax, @data\n"
        "    mov  ds, ax\n"
        "    lea  dx, msg\n"
        "    mov  ah, 09h\n"
        "    int  21h\n"
        "    ; (imprimir decimal omitido en demo)\n"
        "\n"
        "    ; epílogo\n"
        "    mov  sp, bp\n"\
        "    pop  bp\n"
        "    ret\n"
        "main ENDP\n"
        "END main\n"
    )
    self.masmPane.set_plain_code(masm_plain)

    # --- Tabla (derecha/arriba). Direcciones ficticias progresivas para la demo
    rows = [
        ["00401000", "main",  "push", "bp",                "; prólogo"],
        ["00401001", "",      "mov",  "bp, sp",           ""],
        ["00401003", "",      "sub",  "sp, 16",           "; locals (hasta [FP-10])"],
        ["00401006", "",      "mov",  "ax, 5",            ""],
        ["00401008", "",      "mov",  "[bp-08], ax",      "; numero"],
        ["0040100B", "",      "mov",  "ax, 1",            ""],
        ["0040100D", "",      "mov",  "[bp-10], ax",      "; factorial"],
        ["00401010", "",      "mov",  "ax, 1",            ""],
        ["00401012", "",      "mov",  "[bp-0C], ax",      "; i"],
        ["00401015", "L0",    "mov",  "ax, [bp-0C]",      "; i"],
        ["00401018", "",      "cmp",  "ax, [bp-08]",      "; numero"],
        ["0040101B", "",      "jg",   "L1",               ""],
        ["0040101D", "",      "mov",  "ax, [bp-10]",      "; factorial"],
        ["00401020", "",      "imul", "word ptr [bp-0C]", "; * i"],
        ["00401023", "",      "mov",  "[bp-10], ax",      "; factorial"],
        ["00401026", "",      "mov",  "ax, [bp-0C]",      "; i"],
        ["00401029", "",      "add",  "ax, 1",            ""],
        ["0040102B", "",      "mov",  "[bp-0C], ax",      "; i"],
        ["0040102E", "",      "jmp",  "L0",               ""],
        ["00401030", "L1",    "mov",  "ax, @data",        ""],
        ["00401033", "",      "mov",  "ds, ax",           ""],
        ["00401035", "",      "lea",  "dx, msg",          ""],
        ["00401038", "",      "mov",  "ah, 09h",          ""],
        ["0040103A", "",      "int",  "21h",              ""],
        ["0040103C", "",      "mov",  "sp, bp",           "; epílogo"],
        ["0040103E", "",      "pop",  "bp",               ""],
        ["0040103F", "",      "ret",  "",                 ""],
    ]
    self.masmPane.load_masm_rows(rows)

    # --- Registros (derecha/abajo). Ejemplo final tras el bucle: 5! = 120
    regs = {
        "AX": 120,       # resultado del factorial en AX
        "BX": 0,
        "CX": 0,
        "DX": 0,
        "SI": 0,
        "DI": 0,
        "BP": 0xFF00,    # ficticio sólo para mostrar formato
        "SP": 0xFEF0,
    }
    self.masmPane.load_registers(regs)
