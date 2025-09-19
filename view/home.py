# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui, QtWidgets
from .line_numbered_textedit import CodeEditor  # Import the new CodeEditor
from intermediate_code.generador_triplos import GeneradorTriplos
from intermediate_code.generador_cuadruplos import GeneradorCuadruplos


class ZoomablePlainTextEdit(QtWidgets.QPlainTextEdit):
    def __init__(self, *args, min_pt=8, max_pt=48, start_pt=11, **kwargs):
        super().__init__(*args, **kwargs)
        self._min_pt = min_pt
        self._max_pt = max_pt
        f = self.font()
        f.setPointSize(start_pt)
        self.setFont(f)

    def _apply_zoom_steps(self, steps: int):
        f = self.font()
        size = f.pointSize() if f.pointSize() > 0 else max(
            self._min_pt, int(f.pixelSize() / self.logicalDpiY() * 72)
        )
        new_size = max(self._min_pt, min(self._max_pt, size + steps))
        if new_size == size:
            return
        f.setPointSize(new_size)
        self.setFont(f)

    def wheelEvent(self, event: QtGui.QWheelEvent):
        if event.modifiers() & QtCore.Qt.ShiftModifier:
            angle = event.angleDelta().y()
            pixel = event.pixelDelta().y()
            if angle != 0:
                steps = int(angle / 120) if angle % 120 == 0 else (1 if angle > 0 else -1)
            elif pixel != 0:
                steps = 1 if pixel > 0 else -1
            else:
                steps = 0
            if steps:
                self._apply_zoom_steps(steps)
                event.accept()
                return
        super().wheelEvent(event)

    def keyPressEvent(self, event: QtGui.QKeyEvent):
        if event.modifiers() & QtCore.Qt.ShiftModifier:
            if event.key() in (QtCore.Qt.Key_Plus, QtCore.Qt.Key_Equal):
                self._apply_zoom_steps(+1)
                return
            if event.key() in (QtCore.Qt.Key_Minus, QtCore.Qt.Key_Underscore):
                self._apply_zoom_steps(-1)
                return
        super().keyPressEvent(event)


class Ui_home(object):

    # ==========================
    # Helper: crear tabla uniforme
    # ==========================
    def _crear_tabla(self, columnas: int, headers: list) -> QtWidgets.QTableWidget:
        t = QtWidgets.QTableWidget()
        t.setColumnCount(columnas)
        t.setHorizontalHeaderLabels(headers)

        # Comportamiento y aspecto (igual que Triplos/Cuádruplos)
        t.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)
        t.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        t.verticalHeader().setVisible(False)
        t.setAlternatingRowColors(False)
        t.setFont(QtGui.QFont("Consolas", 14))
        t.verticalHeader().setDefaultSectionSize(40)
        t.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        # Redimensionamiento de columnas
        header = t.horizontalHeader()
        # Primeras columnas a tamaño de contenido, resto a Stretch
        for i in range(columnas):
            if i <= 1:
                header.setSectionResizeMode(i, QtWidgets.QHeaderView.ResizeToContents)
            else:
                header.setSectionResizeMode(i, QtWidgets.QHeaderView.Stretch)
        header.setStretchLastSection(True)

        # Estilo oscuro homogéneo
        t.setStyleSheet("""
            QTableWidget { background-color: #000000; color: #FFFFFF; gridline-color: #333333; }
            QHeaderView::section { background-color: #111111; color: #FFFFFF; }
            QTableWidget::item:selected { background-color: #2A2A2A; color: #FFFFFF; }
        """)
        return t

    # ==========================
    # Stubs (reemplaza con tu lógica real)
    # ==========================
    def mi_analizador_lexico(self, codigo: str):
        """
        Devuelve lista de filas: [linea, componente, lexema, patron]
        Reemplaza con tu analizador real.
        """
        # Demo mínima: retorna algo para ver el layout
        if not codigo.strip():
            return []
        return [
            [1, "IDENT", "Main", r"[A-Za-z_]\w*"],
            [2, "KW", "public", r"(public|class|static|void)"],
        ]

    def mi_constructor_tabla_simbolos(self):
        """
        Devuelve lista de filas: [nombre, tipo, valor, linea, alcance, direccion]
        Reemplaza con tu construcción real.
        """
        return [
            ["x", "int", "10", 3, "local", "0x0010"],
            ["y", "float", "3.14", 4, "local", "0x0014"],
        ]

    # ==========================
    # UI principal
    # ==========================
    def setupUi(self, home):
        home.setObjectName("home")
        home.resize(1200, 800)
        home.setMinimumSize(QtCore.QSize(1000, 700))

        # Generadores
        self.generador_triplos = GeneradorTriplos()
        self.generador_cuadruplos = GeneradorCuadruplos()

        # Estilos globales
        home.setStyleSheet("""
            QWidget {
                background-color: #2D2D2D;
                color: #FFFFFF;
                font-family: 'Segoe UI', 'Arial', sans-serif;
            }
            QTextEdit, QPlainTextEdit {
                background-color: #1E1E1E;
                color: #DCDCDC;
                border: 2px solid #3E3E3E;
                border-radius: 4px;
                padding: 10px;
                font-family: 'Consolas', 'Courier New', monospace;
                selection-background-color: #3E3E3E;
                line-height: 1.3;
            }
            QTableWidget {
                background-color: #1E1E1E;
                color: #DCDCDC;
                border: 2px solid #3E3E3E;
                border-radius: 4px;
                gridline-color: #505050;
                selection-background-color: #3A5C85;
                selection-color: #FFFFFF;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 13px;
            }
            QTableWidget::item {
                padding: 4px;
                border-bottom: 1px solid #4E4E4E;
            }
            QHeaderView::section {
                background-color: #383838;
                color: #FFFFFF;
                padding: 8px;
                border: 1px solid #505050;
                font-weight: bold;
            }
            QPushButton {
                background-color: #404040;
                border: 2px solid #505050;
                border-radius: 4px;
                padding: 8px 16px;
                min-width: 120px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #505050; border-color: #606060; }
            QPushButton:pressed { background-color: #303030; border-color: #404040; }
            QLabel { color: #FFFFFF; font-size: 14px; font-weight: bold; }
            QTabWidget::pane { border: 1px solid #3E3E3E; background: #2D2D2D; }
            QTabBar::tab {
                background: #404040; color: #FFFFFF; padding: 8px 16px;
                border-top-left-radius: 4px; border-top-right-radius: 4px; margin-right: 2px;
            }
            QTabBar::tab:selected { background: #505050; border-color: #3E3E3E; }
            QTreeWidget {
                background-color: #1E1E1E; color: #DCDCDC; border: 2px solid #3E3E3E;
                border-radius: 4px; outline: none;
            }
            QTreeWidget::item { padding: 6px; margin: 1px; }
            QTreeWidget::item:selected { background-color: #3A5C85; color: #FFFFFF; }
        """)

        self.centralWidget = QtWidgets.QWidget(home)
        self.mainLayout = QtWidgets.QVBoxLayout(self.centralWidget)
        self.mainLayout.setContentsMargins(20, 20, 20, 20)
        self.mainLayout.setSpacing(15)

        # Título
        self.titleLabel = QtWidgets.QLabel("Analizador de Código Java", self.centralWidget)
        self.titleLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.titleLabel.setStyleSheet("QLabel { font-size: 28px; font-weight: bold; color: #F89406; padding: 10px; }")
        self.mainLayout.addWidget(self.titleLabel)

        # Código fuente
        self.sourceGroup = QtWidgets.QGroupBox("Código Fuente Java")
        self.sourceGroup.setStyleSheet("""
            QGroupBox {
                font-size: 16px; border: 2px solid #3E3E3E; border-radius: 6px;
                margin-top: 12px; padding-top: 12px;
            }
            QGroupBox::title {
                subcontrol-origin: margin; subcontrol-position: top center;
                padding: 0 5px; color: #F89406; font-weight: bold;
            }
        """)
        self.sourceLayout = QtWidgets.QVBoxLayout(self.sourceGroup)
        self.tx_ingreso = CodeEditor()
        self.tx_ingreso.setPlaceholderText("Escribe tu código Java aquí o carga un archivo...")

        # Código por defecto con marcador $0
        default_code = (
            "public class Main {\n"
            "    public static void main(String[] args) {\n"
            "        $0\n"
            "    }\n"
            "}"
        )
        self.tx_ingreso.setPlainText(default_code)
        texto = self.tx_ingreso.toPlainText()
        pos = texto.find("$0")
        if pos != -1:
            texto = texto.replace("$0", "")
            self.tx_ingreso.setPlainText(texto)
            cur = self.tx_ingreso.textCursor()
            cur.setPosition(pos)
            self.tx_ingreso.setTextCursor(cur)

        self.sourceLayout.addWidget(self.tx_ingreso)
        self.mainLayout.addWidget(self.sourceGroup)

        # Controles superiores
        self.topControls = QtWidgets.QHBoxLayout()
        self.bt_archivo = QtWidgets.QPushButton("Cargar Archivo")
        self.bt_archivo.setIcon(QtGui.QIcon.fromTheme("document-open"))
        self.bt_archivo.setStyleSheet("QPushButton { background-color: #3279B7; border-color: #3C8DCC; }"
                                      "QPushButton:hover { background-color: #3C8DCC; }")

        self.bt_run = QtWidgets.QPushButton("Run")
        self.bt_run.setIcon(QtGui.QIcon.fromTheme("media-playback-start"))
        self.bt_run.setStyleSheet("QPushButton { background-color: #3279B7; border-color: #3C8DCC; }"
                                  "QPushButton:hover { background-color: #3C8DCC; }")

        self.bt_limpiar = QtWidgets.QPushButton("Limpiar")
        self.bt_limpiar.setIcon(QtGui.QIcon.fromTheme("edit-clear"))
        self.bt_limpiar.setToolTip("Limpiar todo")

        self.bt_zoom_out = QtWidgets.QPushButton("—")
        self.bt_zoom_out.setFixedWidth(40)
        self.bt_zoom_out.setToolTip("Zoom -  (Shift + \"-\")")
        self.bt_zoom_in = QtWidgets.QPushButton("+")
        self.bt_zoom_in.setFixedWidth(40)
        self.bt_zoom_in.setToolTip("Zoom +  (Shift + \"+\")")

        self.topControls.addWidget(self.bt_archivo)
        self.topControls.addWidget(self.bt_run)
        self.topControls.addWidget(self.bt_limpiar)
        self.topControls.addStretch()
        self.topControls.addWidget(QtWidgets.QLabel("Zoom:"))
        self.topControls.addWidget(self.bt_zoom_out)
        self.topControls.addWidget(self.bt_zoom_in)
        self.mainLayout.addLayout(self.topControls)

        # Tabs
        self.analysisTabs = QtWidgets.QTabWidget()
        self.analysisTabs.setStyleSheet("QTabWidget::tab-bar { alignment: center; }")

        # --- Léxico (igual que Triplos/Cuádruplos)
        self.lexicalTab = QtWidgets.QWidget()
        self.lexicalLayout = QtWidgets.QVBoxLayout(self.lexicalTab)
        self.lexicalLayout.setContentsMargins(0, 0, 0, 0)
        self.lexicalLayout.setSpacing(0)
        self.tb_lexico = self._crear_tabla(
            4, ["Línea", "Componente Léxico", "Lexema", "Patrón"]
        )
        self.lexicalLayout.addWidget(self.tb_lexico, 1)
        self.analysisTabs.addTab(self.lexicalTab, "Análisis Léxico")

        # --- Sintáctico
        self.syntaxTab = QtWidgets.QWidget()
        self.syntaxLayout = QtWidgets.QVBoxLayout(self.syntaxTab)
        self.tx_sintactico = QtWidgets.QTextEdit()
        self.tx_sintactico.setPlaceholderText("Resultados del análisis sintáctico...")
        self.tx_sintactico.setReadOnly(True)
        self.syntaxLayout.addWidget(self.tx_sintactico)
        self.analysisTabs.addTab(self.syntaxTab, "Análisis Sintáctico")

        # --- Símbolos (igual que Triplos/Cuádruplos)
        self.symbolsTab = QtWidgets.QWidget()
        self.symbolsLayout = QtWidgets.QVBoxLayout(self.symbolsTab)
        self.symbolsLayout.setContentsMargins(0, 0, 0, 0)
        self.symbolsLayout.setSpacing(0)
        self.tb_simbolos = self._crear_tabla(
            6, ["Nombre", "Tipo", "Valor", "Línea", "Alcance", "Dirección"]
        )
        # Ajuste fino de resize (primera col stretch, resto como toca)
        header_sym = self.tb_simbolos.horizontalHeader()
        header_sym.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        for i in range(1, 6):
            if i <= 4:
                header_sym.setSectionResizeMode(i, QtWidgets.QHeaderView.ResizeToContents)
            else:
                header_sym.setSectionResizeMode(i, QtWidgets.QHeaderView.Stretch)

        self.symbolsLayout.addWidget(self.tb_simbolos, 1)
        self.analysisTabs.addTab(self.symbolsTab, "Tabla de Símbolos")

        # --- Recorridos del Árbol
        self.parseTreeTab = QtWidgets.QWidget()
        self.parseTreeLayout = QtWidgets.QVBoxLayout(self.parseTreeTab)
        self.treeWidget = QtWidgets.QTreeWidget()
        self.treeWidget.setHeaderLabel("Recorridos del Árbol")
        self.treeWidget.setColumnCount(1)
        self.treeWidget.setHeaderHidden(False)
        self.treeWidget.header().setDefaultSectionSize(400)
        self.treeWidget.header().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        self.treeWidget.setIndentation(25)
        self.treeWidget.setAnimated(True)
        self.treeWidget.setFont(QtGui.QFont("Consolas", 11))
        self.parseTreeLayout.addWidget(self.treeWidget)
        self.analysisTabs.addTab(self.parseTreeTab, "Recorridos del Árbol")

        # --- Triplos
        self.triplesTab = QtWidgets.QWidget()
        self.triplesLayout = QtWidgets.QVBoxLayout(self.triplesTab)
        self.tb_triplos = self._crear_tabla(
            4, ["Índice", "Operador", "Arg1", "Arg2/Resultado"]
        )
        # Afinar resize como lo tenías
        header_tri = self.tb_triplos.horizontalHeader()
        header_tri.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        header_tri.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        header_tri.setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)
        header_tri.setSectionResizeMode(3, QtWidgets.QHeaderView.Stretch)
        self.triplesLayout.addWidget(self.tb_triplos)
        self.analysisTabs.addTab(self.triplesTab, "Triplos")

        # --- Cuádruplos
        self.quadruplesTab = QtWidgets.QWidget()
        self.quadruplesLayout = QtWidgets.QVBoxLayout(self.quadruplesTab)
        self.tb_cuadruplos = self._crear_tabla(
            5, ["#", "Operador", "Arg1", "Arg2", "Resultado"]
        )
        header_cua = self.tb_cuadruplos.horizontalHeader()
        header_cua.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        header_cua.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        header_cua.setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)
        header_cua.setSectionResizeMode(3, QtWidgets.QHeaderView.Stretch)
        header_cua.setSectionResizeMode(4, QtWidgets.QHeaderView.Stretch)
        self.quadruplesLayout.addWidget(self.tb_cuadruplos)
        self.analysisTabs.addTab(self.quadruplesTab, "Cuádruplos")

        # --- Salida
        self.outputTab = QtWidgets.QWidget()
        self.outputLayout = QtWidgets.QVBoxLayout(self.outputTab)
        self.outputHeader = QtWidgets.QHBoxLayout()
        self.lb_output_status = QtWidgets.QLabel("Salida del código (solo diseño):")
        self.lb_output_status.setStyleSheet("QLabel { color: #F0AD4E; }")
        self.bt_output_clear = QtWidgets.QPushButton("Limpiar salida")
        self.bt_output_clear.setIcon(QtGui.QIcon.fromTheme("edit-clear"))
        self.bt_output_clear.setStyleSheet("QPushButton { background-color: #5F5F5F; border-color: #6A6A6A; }"
                                           "QPushButton:hover { background-color: #6A6A6A; }")
        self.outputHeader.addWidget(self.lb_output_status)
        self.outputHeader.addStretch()
        self.outputHeader.addWidget(self.bt_output_clear)
        self.outputLayout.addLayout(self.outputHeader)

        self.tx_output = ZoomablePlainTextEdit(start_pt=20)
        self.tx_output.setReadOnly(True)
        self.tx_output.setPlaceholderText("Aquí aparecerá la salida del programa...")
        self.tx_output.setObjectName("tx_output_console")
        self.outputLayout.addWidget(self.tx_output)
        self.analysisTabs.addTab(self.outputTab, "Salida del código")

        # Tabs al layout principal
        self.mainLayout.addWidget(self.analysisTabs)

        # Controles inferiores
        self.bottomControls = QtWidgets.QHBoxLayout()
        self.bottomControls.setSpacing(20)
        self.bt_lexico = QtWidgets.QPushButton("Analizar Léxico")
        self.bt_lexico.setIcon(QtGui.QIcon.fromTheme("edit-find"))
        self.bt_lexico.setStyleSheet("QPushButton { background-color: #57A64A; border-color: #65B158; }"
                                     "QPushButton:hover { background-color: #65B158; }")
        self.bt_sintactico = QtWidgets.QPushButton("Analizar Sintaxis")
        self.bt_sintactico.setIcon(QtGui.QIcon.fromTheme("dialog-ok-apply"))
        self.bt_sintactico.setStyleSheet("QPushButton { background-color: #D69D45; border-color: #E0A64D; }"
                                         "QPushButton:hover { background-color: #E0A64D; }")
        self.bt_simbolos = QtWidgets.QPushButton("Ver Tabla Símbolos")
        self.bt_simbolos.setIcon(QtGui.QIcon.fromTheme("x-office-spreadsheet"))
        self.bt_simbolos.setStyleSheet("QPushButton { background-color: #5F9EA0; border-color: #70AEB0; }"
                                       "QPushButton:hover { background-color: #70AEB0; }")
        self.bt_arbol = QtWidgets.QPushButton("Generar Recorridos")
        self.bt_arbol.setIcon(QtGui.QIcon.fromTheme("view-list-tree"))
        self.bt_arbol.setStyleSheet("QPushButton { background-color: #9370DB; border-color: #A080DD; }"
                                    "QPushButton:hover { background-color: #A080DD; }")
        self.bt_arbolLR = QtWidgets.QPushButton("Generar Árbol LR")
        self.bt_arbol_lr = self.bt_arbolLR

        self.bt_triplos = QtWidgets.QPushButton("Generar Triplos")
        self.bt_triplos.setIcon(QtGui.QIcon.fromTheme("applications-system"))
        self.bt_triplos.setStyleSheet("QPushButton { background-color: #B85450; border-color: #C85854; }"
                                      "QPushButton:hover { background-color: #C85854; }")
        self.bt_cuadruplos = QtWidgets.QPushButton("Generar Cuádruplos")
        self.bt_cuadruplos.setIcon(QtGui.QIcon.fromTheme("applications-system"))
        self.bt_cuadruplos.setStyleSheet("QPushButton { background-color: #8B4513; border-color: #A0521A; }"
                                         "QPushButton:hover { background-color: #A0521A; }")

        self.bottomControls.addWidget(self.bt_lexico)
        self.bottomControls.addWidget(self.bt_sintactico)
        self.bottomControls.addWidget(self.bt_simbolos)
        self.bottomControls.addWidget(self.bt_arbol)
        self.bottomControls.addWidget(self.bt_arbolLR)
        self.bottomControls.addWidget(self.bt_triplos)
        self.bottomControls.addWidget(self.bt_cuadruplos)
        self.bottomControls.addStretch()
        self.mainLayout.addLayout(self.bottomControls)

        # Status bar
        self.estado = QtWidgets.QStatusBar(home)
        self.estado.setStyleSheet("""
            QStatusBar {
                background-color: #252526; color: #858585; font-size: 12px;
                border-top: 1px solid #3C3C3C; padding: 5px;
            }
        """)
        home.setStatusBar(self.estado)

        # Shortcuts
        self.shortcut_run_lexical = QtWidgets.QShortcut(QtGui.QKeySequence("F5"), home)
        self.shortcut_run_syntactic = QtWidgets.QShortcut(QtGui.QKeySequence("F6"), home)
        self.shortcut_open = QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+O"), home)
        self.shortcut_clear = QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+L"), home)
        self.shortcut_tree = QtWidgets.QShortcut(QtGui.QKeySequence("F7"), home)
        self.shortcut_output = QtWidgets.QShortcut(QtGui.QKeySequence("F9"), home)

        home.setCentralWidget(self.centralWidget)

        # Traducciones / tooltips
        self.retranslateUi(home)
        QtCore.QMetaObject.connectSlotsByName(home)

        # Conexiones básicas
        self.bt_run.clicked.connect(lambda: self.analysisTabs.setCurrentWidget(self.outputTab))
        self.shortcut_output.activated.connect(lambda: self.analysisTabs.setCurrentWidget(self.outputTab))
        self.bt_output_clear.clicked.connect(self.tx_output.clear)

        # Conexiones de análisis
        self.bt_lexico.clicked.connect(self.analizar_lexico)
        self.bt_simbolos.clicked.connect(self.ver_tabla_simbolos)

        # Triplos / Cuádruplos
        self.bt_triplos.clicked.connect(self.llenar_tabla_triplos)
        self.bt_cuadruplos.clicked.connect(self.llenar_tabla_cuadruplos)

    # ==========================
    # Acciones
    # ==========================
    def analizar_lexico(self):
        # Import local para evitar ciclos
        from lexer.analizador_lexico import prueba as prueba_lexica, tabla_simbolos
        from PyQt5 import QtCore, QtWidgets
        from PyQt5.QtGui import QColor

        codigo = self.tx_ingreso.toPlainText().strip()
        if not codigo:
            self.estado.showMessage("No hay código para analizar.", 3000)
            return

        try:
            tabla_simbolos.limpiar()
        except Exception:
            pass

        try:
            resultados = prueba_lexica(codigo)

            self.tb_lexico.setUpdatesEnabled(False)
            self.tb_lexico.clearContents()
            self.tb_lexico.setRowCount(len(resultados))

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
                    "CLASS", "PUBLIC", "PRIVATE", "PROTECTED", "STATIC", "FINAL", "VOID", "INT", "FLOAT",
                    "DOUBLE", "BOOLEAN", "CHAR", "STRING", "IF", "ELSE", "FOR", "WHILE", "DO", "SWITCH",
                    "CASE", "DEFAULT", "BREAK", "CONTINUE", "RETURN", "SYSTEM", "OUT", "PRINTLN", "PRINT"
                }
                if tipo in palabras_reservadas:
                    return "Palabra reservada"
                return patrones.get(tipo, "")

            usar_fondo_oscuro = True
            for i, token in enumerate(resultados):
                if usar_fondo_oscuro:
                    color_fondo = QColor("#1E1E1E");
                    color_texto = QColor("#FFFFFF")
                else:
                    color_fondo = QColor("#2D2D2D");
                    color_texto = QColor("#FFFFFF")
                usar_fondo_oscuro = not usar_fondo_oscuro

                linea = str(token.get("linea", "0"))
                tipo = token.get("tipo", "DESCONOCIDO")
                lexema = str(token.get("valor", ""))
                patron = _patron_por_tipo(tipo)

                if tipo == "ERROR":
                    color_fondo = QColor("#7E2D40");
                    color_texto = QColor("#FFFFFF")

                items = [
                    QtWidgets.QTableWidgetItem(linea),
                    QtWidgets.QTableWidgetItem(tipo),
                    QtWidgets.QTableWidgetItem(lexema),
                    QtWidgets.QTableWidgetItem(patron),
                ]
                for col, it in enumerate(items):
                    it.setBackground(color_fondo)
                    it.setForeground(color_texto)
                    it.setTextAlignment(QtCore.Qt.AlignCenter)
                    self.tb_lexico.setItem(i, col, it)

            self.tb_lexico.setUpdatesEnabled(True)
            self.analysisTabs.setCurrentWidget(self.lexicalTab)
            self.estado.showMessage(f"Análisis léxico completado: {len(resultados)} tokens", 3000)

        except Exception as e:
            import traceback;
            traceback.print_exc()
            self.estado.showMessage(f"Error durante el análisis léxico: {e}", 5000)

    def ver_tabla_simbolos(self):
        # Import local para evitar ciclos
        from lexer.analizador_lexico import tabla_simbolos
        from PyQt5.QtGui import QColor
        from PyQt5 import QtWidgets, QtCore

        simbolos = {}
        try:
            simbolos = tabla_simbolos.obtener_todos()  # dict nombre -> info
        except Exception:
            pass

        if not simbolos:
            self.tb_simbolos.setRowCount(0)
            self.estado.showMessage("No hay símbolos definidos en la tabla de símbolos", 3000)
            self.analysisTabs.setCurrentWidget(self.symbolsTab)
            return

        # Asignador sencillo (inline) para demo/visual (64-bit)
        def asignar_direcciones(symtab: dict):
            align = 8

            def al_up(n, a):
                return ((n + (a - 1)) // a) * a

            _sizes = {"INT": 4, "FLOAT": 4, "DOUBLE": 8, "BOOLEAN": 1, "CHAR": 1, "LONG": 8, "SHORT": 2, "BYTE": 1,
                      "VOID": 0, "STRING": 8, "REFERENCE": 8}

            def sz(tipo):
                return _sizes.get((tipo or "").upper(), 8)

            global_off = 0
            frames = {}  # alcance -> locals_off (neg)
            out = {}
            for name in sorted(symtab.keys()):
                info = symtab[name] or {}
                tipo = info.get("tipo", "")
                alcance = info.get("alcance", "global")
                is_global = (alcance or "global").lower() in ("global", "namespace", "module")
                s = max(1, sz(tipo));
                s = al_up(s, align)
                if is_global:
                    base = al_up(global_off, align)
                    out[name] = f"GLOBAL+{base}"
                    global_off = base + s
                else:
                    fr = frames.setdefault(alcance, 0)
                    fr -= s
                    frames[alcance] = fr
                    out[name] = f"[FP{fr}]" if fr < 0 else f"[FP+{fr}]"
            return out

        addr_map = asignar_direcciones(simbolos)

        self.tb_simbolos.setUpdatesEnabled(False)
        self.tb_simbolos.clearContents()
        names = sorted(simbolos.keys())
        self.tb_simbolos.setRowCount(len(names))

        bg = QColor("#1E1E1E");
        fg = QColor("#DCDCDC")

        for i, nombre in enumerate(names):
            info = simbolos[nombre]
            tipo = info.get("tipo", "")
            valor = str(info.get("valor", ""))
            linea = str(info.get("linea", ""))
            alcance = info.get("alcance", "global")
            direccion = addr_map.get(nombre, "")

            items = [
                QtWidgets.QTableWidgetItem(nombre),
                QtWidgets.QTableWidgetItem(tipo),
                QtWidgets.QTableWidgetItem(valor),
                QtWidgets.QTableWidgetItem(linea),
                QtWidgets.QTableWidgetItem(alcance),
                QtWidgets.QTableWidgetItem(direccion),
            ]
            for it in items:
                it.setBackground(bg);
                it.setForeground(fg)
                it.setTextAlignment(QtCore.Qt.AlignCenter)
            for col, it in enumerate(items):
                self.tb_simbolos.setItem(i, col, it)

        self.tb_simbolos.setUpdatesEnabled(True)
        self.analysisTabs.setCurrentWidget(self.symbolsTab)
        self.estado.showMessage(f"Tabla de símbolos: {len(names)} símbolos", 3000)

    def llenar_tabla_triplos(self):
        try:
            codigo = self.tx_ingreso.toPlainText()
            if not codigo.strip():
                self.estado.showMessage("No hay código para procesar", 3000)
                return

            triplos = self.generador_triplos.generar_desde_codigo(codigo)

            self.tb_triplos.setRowCount(0)
            if not triplos:
                self.estado.showMessage("No se generaron triplos - verificar el código", 3000)
                return

            triplos_data = self.generador_triplos.obtener_triplos_para_tabla()
            self.tb_triplos.setRowCount(len(triplos_data))
            for row, triplo_row in enumerate(triplos_data):
                for col, value in enumerate(triplo_row):
                    item = QtWidgets.QTableWidgetItem(str(value))
                    item.setTextAlignment(QtCore.Qt.AlignCenter)
                    self.tb_triplos.setItem(row, col, item)

            self.analysisTabs.setCurrentWidget(self.triplesTab)
            est = self.generador_triplos.obtener_estadisticas()
            self.estado.showMessage(
                f"Generados {est['total_triplos']} triplos, {est['etiquetas_generadas']} etiquetas", 3000
            )

        except Exception as e:
            import traceback
            traceback.print_exc()
            self.estado.showMessage(f"Error generando triplos: {e}", 5000)

    def llenar_tabla_cuadruplos(self):
        try:
            codigo = self.tx_ingreso.toPlainText()
            if not codigo.strip():
                self.estado.showMessage("No hay código para procesar", 3000)
                return

            cuadruplos = self.generador_cuadruplos.generar_desde_codigo(codigo)

            self.tb_cuadruplos.setRowCount(0)
            if not cuadruplos:
                self.estado.showMessage("No se generaron cuádruplos - verificar el código", 3000)
                return

            cuadruplos_data = self.generador_cuadruplos.obtener_cuadruplos_para_tabla()
            self.tb_cuadruplos.setRowCount(len(cuadruplos_data))
            for row, cuadruplo_row in enumerate(cuadruplos_data):
                for col, value in enumerate(cuadruplo_row):
                    item = QtWidgets.QTableWidgetItem(str(value))
                    item.setTextAlignment(QtCore.Qt.AlignCenter)
                    self.tb_cuadruplos.setItem(row, col, item)

            self.analysisTabs.setCurrentWidget(self.quadruplesTab)
            est = self.generador_cuadruplos.obtener_estadisticas()
            self.estado.showMessage(
                f"Generados {est['total_cuadruplos']} cuádruplos, {est['temporales_generados']} temporales", 3000
            )

        except Exception as e:
            import traceback
            traceback.print_exc()
            self.estado.showMessage(f"Error generando cuádruplos: {e}", 5000)

    # ==========================
    # Traducciones
    # ==========================
    def retranslateUi(self, home):
        _translate = QtCore.QCoreApplication.translate
        home.setWindowTitle(_translate("home", "Analizador de Código Java"))
        self.analysisTabs.setTabText(0, _translate("home", "Análisis Léxico"))
        self.analysisTabs.setTabText(1, _translate("home", "Análisis Sintáctico"))
        self.analysisTabs.setTabText(2, _translate("home", "Tabla de Símbolos"))
        self.analysisTabs.setTabText(3, _translate("home", "Recorridos del Árbol"))
        self.analysisTabs.setTabText(4, _translate("home", "Triplos"))
        self.analysisTabs.setTabText(5, _translate("home", "Cuádruplos"))
        self.analysisTabs.setTabText(6, _translate("home", "Salida del código"))

        self.bt_lexico.setToolTip(_translate("home", "Realizar análisis léxico (F5)"))
        self.bt_sintactico.setToolTip(_translate("home", "Realizar análisis sintáctico (F6)"))
        self.bt_simbolos.setToolTip(_translate("home", "Mostrar tabla de símbolos"))
        self.bt_arbol.setToolTip(_translate("home", "Visualización de recorridos: pre, in y post-orden (F7)"))
        self.bt_arbolLR.setText(_translate("home", "Generar Árbol LR"))
        self.bt_triplos.setToolTip(_translate("home", "Generar representación en triplos del código"))
        self.bt_cuadruplos.setToolTip(_translate("home", "Generar representación en cuádruplos del código"))
        self.bt_archivo.setToolTip(_translate("home", "Abrir un archivo Java (Ctrl+O)"))
        self.bt_run.setToolTip(_translate("home", "Ejecutar el código y mostrar la salida"))
        self.bt_limpiar.setToolTip(_translate("home", "Limpiar todos los campos (Ctrl+L)"))
        self.bt_zoom_in.setToolTip(_translate("home", "Zoom + (Shift + \"+\")"))
        self.bt_zoom_out.setToolTip(_translate("home", "Zoom - (Shift + \"-\")"))
        self.sourceGroup.setTitle(_translate("home", "Código Fuente Java"))
        self.lb_output_status.setText(_translate("home", "Salida del código (solo diseño):"))
        self.bt_output_clear.setText(_translate("home", "Limpiar salida"))
