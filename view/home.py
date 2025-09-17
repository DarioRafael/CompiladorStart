# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui, QtWidgets
from .line_numbered_textedit import CodeEditor  # Import the new CodeEditor


class Ui_home(object):
    def setupUi(self, home):
        home.setObjectName("home")
        home.resize(1200, 800)
        home.setMinimumSize(QtCore.QSize(1000, 700))

        # Estilos generales
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
                font-size: 13px;
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

            QPushButton:hover {
                background-color: #505050;
                border-color: #606060;
            }

            QPushButton:pressed {
                background-color: #303030;
                border-color: #404040;
            }

            QLabel {
                color: #FFFFFF;
                font-size: 14px;
                font-weight: bold;
            }

            QTabWidget::pane {
                border: 1px solid #3E3E3E;
                background: #2D2D2D;
            }

            QTabBar::tab {
                background: #404040;
                color: #FFFFFF;
                padding: 8px 16px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                margin-right: 2px;
            }

            QTabBar::tab:selected {
                background: #505050;
                border-color: #3E3E3E;
            }

            QTreeWidget {
                background-color: #1E1E1E;
                color: #DCDCDC;
                border: 2px solid #3E3E3E;
                border-radius: 4px;
                outline: none;
            }

            QTreeWidget::item {
                padding: 6px;
                margin: 1px;
            }

            QTreeWidget::item:selected {
                background-color: #3A5C85;
                color: #FFFFFF;
            }

            QTreeWidget::branch:has-children:!has-siblings:closed,
            QTreeWidget::branch:closed:has-children:has-siblings {
                border-image: none;
                image: url(:/images/branch-closed.png);
            }

            QTreeWidget::branch:open:has-children:!has-siblings,
            QTreeWidget::branch:open:has-children:has-siblings  {
                border-image: none;
                image: url(:/images/branch-open.png);
            }
        """)

        self.centralWidget = QtWidgets.QWidget(home)
        self.centralWidget.setObjectName("centralWidget")

        # Layout principal
        self.mainLayout = QtWidgets.QVBoxLayout(self.centralWidget)
        self.mainLayout.setContentsMargins(20, 20, 20, 20)
        self.mainLayout.setSpacing(15)

        # Título
        self.titleLabel = QtWidgets.QLabel("Analizador de Código Java", self.centralWidget)
        self.titleLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.titleLabel.setStyleSheet("""
            QLabel {
                font-size: 28px;
                font-weight: bold;
                color: #F89406;
                padding: 10px;
            }
        """)
        self.mainLayout.addWidget(self.titleLabel)

        # Área de código fuente
        self.sourceGroup = QtWidgets.QGroupBox("Código Fuente Java")
        self.sourceGroup.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                border: 2px solid #3E3E3E;
                border-radius: 6px;
                margin-top: 12px;
                padding-top: 12px;
            }

            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 5px;
                color: #F89406;
                font-weight: bold;
            }
        """)

        self.sourceLayout = QtWidgets.QVBoxLayout(self.sourceGroup)
        self.tx_ingreso = CodeEditor()
        self.tx_ingreso.setPlaceholderText("Escribe tu código Java aquí o carga un archivo...")
        self.sourceLayout.addWidget(self.tx_ingreso)
        self.mainLayout.addWidget(self.sourceGroup)

        # Controles superiores
        self.topControls = QtWidgets.QHBoxLayout()

        self.bt_archivo = QtWidgets.QPushButton("Cargar Archivo")
        self.bt_archivo.setIcon(QtGui.QIcon.fromTheme("document-open"))
        self.bt_archivo.setStyleSheet("""
            QPushButton {
                background-color: #3279B7;
                border-color: #3C8DCC;
            }
            QPushButton:hover {
                background-color: #3C8DCC;
            }
        """)

        self.bt_run = QtWidgets.QPushButton("Run")
        self.bt_run.setIcon(QtGui.QIcon.fromTheme("media-playback-start"))
        self.bt_run.setStyleSheet("""
            QPushButton {
                background-color: #3279B7;
                border-color: #3C8DCC;
            }
            QPushButton:hover {
                background-color: #3C8DCC;
            }
        """)

        self.bt_limpiar = QtWidgets.QPushButton("Limpiar")
        self.bt_limpiar.setIcon(QtGui.QIcon.fromTheme("edit-clear"))
        self.bt_limpiar.setToolTip("Limpiar todo")

        # === Botones de Zoom ===
        self.bt_zoom_out = QtWidgets.QPushButton("—")  # guion largo para estética
        self.bt_zoom_out.setFixedWidth(40)
        self.bt_zoom_out.setToolTip("Zoom -  (Shift + “-”)")
        self.bt_zoom_out.setStyleSheet("QPushButton { min-width: 40px; }")

        self.bt_zoom_in = QtWidgets.QPushButton("+")
        self.bt_zoom_in.setFixedWidth(40)
        self.bt_zoom_in.setToolTip("Zoom +  (Shift + “+”)")
        self.bt_zoom_in.setStyleSheet("QPushButton { min-width: 40px; }")

        self.topControls.addWidget(self.bt_archivo)
        self.topControls.addWidget(self.bt_run)
        self.topControls.addWidget(self.bt_limpiar)
        self.topControls.addStretch()
        # Añadimos los botones de zoom del lado derecho
        self.topControls.addWidget(QtWidgets.QLabel("Zoom:"))
        self.topControls.addWidget(self.bt_zoom_out)
        self.topControls.addWidget(self.bt_zoom_in)

        self.mainLayout.addLayout(self.topControls)

        # Panel de análisis con pestañas
        self.analysisTabs = QtWidgets.QTabWidget()
        self.analysisTabs.setStyleSheet("""
            QTabWidget::tab-bar {
                alignment: center;
            }
        """)

        # ====== Pestaña: Análisis Léxico ======
        self.lexicalTab = QtWidgets.QWidget()
        self.lexicalLayout = QtWidgets.QVBoxLayout(self.lexicalTab)

        self.tb_lexico = QtWidgets.QTableWidget()
        self.tb_lexico.setColumnCount(4)
        self.tb_lexico.setHorizontalHeaderLabels(["Línea", "Componente Léxico", "Lexema", "Patrón"])
        self.tb_lexico.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        self.tb_lexico.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        self.tb_lexico.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)
        self.tb_lexico.horizontalHeader().setSectionResizeMode(3, QtWidgets.QHeaderView.Stretch)
        self.tb_lexico.verticalHeader().setVisible(False)
        self.tb_lexico.setAlternatingRowColors(True)
        self.tb_lexico.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)
        self.tb_lexico.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.lexicalLayout.addWidget(self.tb_lexico)
        self.analysisTabs.addTab(self.lexicalTab, "Análisis Léxico")

        # ====== Pestaña: Análisis Sintáctico ======
        self.syntaxTab = QtWidgets.QWidget()
        self.syntaxLayout = QtWidgets.QVBoxLayout(self.syntaxTab)
        self.tx_sintactico = QtWidgets.QTextEdit()
        self.tx_sintactico.setPlaceholderText("Resultados del análisis sintáctico...")
        self.tx_sintactico.setReadOnly(True)
        self.syntaxLayout.addWidget(self.tx_sintactico)
        self.analysisTabs.addTab(self.syntaxTab, "Análisis Sintáctico")

        # ====== Pestaña: Tabla de Símbolos ======
        self.symbolsTab = QtWidgets.QWidget()
        self.symbolsLayout = QtWidgets.QVBoxLayout(self.symbolsTab)
        self.tb_simbolos = QtWidgets.QTableWidget()
        self.tb_simbolos.setColumnCount(5)
        self.tb_simbolos.setHorizontalHeaderLabels(["Nombre", "Tipo", "Valor", "Línea", "Alcance"])
        self.tb_simbolos.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        self.tb_simbolos.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        self.tb_simbolos.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
        self.tb_simbolos.horizontalHeader().setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeToContents)
        self.tb_simbolos.horizontalHeader().setSectionResizeMode(4, QtWidgets.QHeaderView.ResizeToContents)
        self.tb_simbolos.verticalHeader().setVisible(False)
        self.tb_simbolos.setAlternatingRowColors(True)
        self.tb_simbolos.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)
        self.tb_simbolos.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.symbolsLayout.addWidget(self.tb_simbolos)
        self.analysisTabs.addTab(self.symbolsTab, "Tabla de Símbolos")

        # ====== Pestaña: Recorridos del Árbol ======
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

        # ====== Pestaña: Triplos ======
        self.triplesTab = QtWidgets.QWidget()
        self.triplesLayout = QtWidgets.QVBoxLayout(self.triplesTab)

        self.tb_triplos = QtWidgets.QTableWidget()
        self.tb_triplos.setColumnCount(4)
        self.tb_triplos.setHorizontalHeaderLabels(["Índice", "Operador", "Arg1", "Arg2/Resultado"])
        self.tb_triplos.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        self.tb_triplos.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        self.tb_triplos.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)
        self.tb_triplos.horizontalHeader().setSectionResizeMode(3, QtWidgets.QHeaderView.Stretch)
        self.tb_triplos.verticalHeader().setVisible(False)
        self.tb_triplos.setAlternatingRowColors(True)
        self.tb_triplos.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)
        self.tb_triplos.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.triplesLayout.addWidget(self.tb_triplos)

        self.analysisTabs.addTab(self.triplesTab, "Triplos")

        # ====== Pestaña: Cuádruplos ======
        self.quadruplesTab = QtWidgets.QWidget()
        self.quadruplesLayout = QtWidgets.QVBoxLayout(self.quadruplesTab)

        self.tb_cuadruplos = QtWidgets.QTableWidget()
        self.tb_cuadruplos.setColumnCount(5)
        self.tb_cuadruplos.setHorizontalHeaderLabels(["#", "Operador", "Arg1", "Arg2", "Resultado"])
        self.tb_cuadruplos.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        self.tb_cuadruplos.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        self.tb_cuadruplos.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)
        self.tb_cuadruplos.horizontalHeader().setSectionResizeMode(3, QtWidgets.QHeaderView.Stretch)
        self.tb_cuadruplos.horizontalHeader().setSectionResizeMode(4, QtWidgets.QHeaderView.Stretch)
        self.tb_cuadruplos.verticalHeader().setVisible(False)
        self.tb_cuadruplos.setAlternatingRowColors(True)
        self.tb_cuadruplos.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)
        self.tb_cuadruplos.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.quadruplesLayout.addWidget(self.tb_cuadruplos)

        self.analysisTabs.addTab(self.quadruplesTab, "Cuádruplos")

        # ====== Pestaña: Salida del código ======
        self.outputTab = QtWidgets.QWidget()
        self.outputLayout = QtWidgets.QVBoxLayout(self.outputTab)

        # Cabecera de estado/acción
        self.outputHeader = QtWidgets.QHBoxLayout()
        self.lb_output_status = QtWidgets.QLabel("Salida del código (solo diseño):")
        self.lb_output_status.setStyleSheet("QLabel { color: #F0AD4E; }")
        self.bt_output_clear = QtWidgets.QPushButton("Limpiar salida")
        self.bt_output_clear.setIcon(QtGui.QIcon.fromTheme("edit-clear"))
        self.bt_output_clear.setStyleSheet("""
            QPushButton {
                background-color: #5F5F5F;
                border-color: #6A6A6A;
            }
            QPushButton:hover {
                background-color: #6A6A6A;
            }
        """)
        self.outputHeader.addWidget(self.lb_output_status)
        self.outputHeader.addStretch()
        self.outputHeader.addWidget(self.bt_output_clear)
        self.outputLayout.addLayout(self.outputHeader)

        # Consola de salida
        self.tx_output = QtWidgets.QPlainTextEdit()
        self.tx_output.setReadOnly(True)
        self.tx_output.setPlaceholderText("Aquí aparecerá la salida del programa...")
        self.tx_output.setObjectName("tx_output_console")
        self.outputLayout.addWidget(self.tx_output)

        self.analysisTabs.addTab(self.outputTab, "Salida del código")

        # Agregar el TabWidget al layout principal
        self.mainLayout.addWidget(self.analysisTabs)

        # Controles inferiores
        self.bottomControls = QtWidgets.QHBoxLayout()
        self.bottomControls.setSpacing(20)

        self.bt_lexico = QtWidgets.QPushButton("Analizar Léxico")
        self.bt_lexico.setIcon(QtGui.QIcon.fromTheme("edit-find"))
        self.bt_lexico.setStyleSheet("""
            QPushButton {
                background-color: #57A64A;
                border-color: #65B158;
            }
            QPushButton:hover {
                background-color: #65B158;
            }
        """)

        self.bt_sintactico = QtWidgets.QPushButton("Analizar Sintaxis")
        self.bt_sintactico.setIcon(QtGui.QIcon.fromTheme("dialog-ok-apply"))
        self.bt_sintactico.setStyleSheet("""
            QPushButton {
                background-color: #D69D45;
                border-color: #E0A64D;
            }
            QPushButton:hover {
                background-color: #E0A64D;
            }
        """)

        self.bt_simbolos = QtWidgets.QPushButton("Ver Tabla Símbolos")
        self.bt_simbolos.setIcon(QtGui.QIcon.fromTheme("x-office-spreadsheet"))
        self.bt_simbolos.setStyleSheet("""
            QPushButton {
                background-color: #5F9EA0;
                border-color: #70AEB0;
            }
            QPushButton:hover {
                background-color: #70AEB0;
            }
        """)

        self.bt_arbol = QtWidgets.QPushButton("Generar Recorridos")
        self.bt_arbol.setIcon(QtGui.QIcon.fromTheme("view-list-tree"))
        self.bt_arbol.setStyleSheet("""
            QPushButton {
                background-color: #9370DB;
                border-color: #A080DD;
            }
            QPushButton:hover {
                background-color: #A080DD;
            }
        """)

        self.bt_arbolLR = QtWidgets.QPushButton("Generar Árbol LR")
        self.bt_arbol_lr = self.bt_arbolLR

        self.bottomControls.addWidget(self.bt_lexico)
        self.bottomControls.addWidget(self.bt_sintactico)
        self.bottomControls.addWidget(self.bt_simbolos)
        self.bottomControls.addWidget(self.bt_arbol)
        self.bottomControls.addWidget(self.bt_arbolLR)
        self.bottomControls.addStretch()

        self.mainLayout.addLayout(self.bottomControls)

        # Barra de estado
        self.estado = QtWidgets.QStatusBar(home)
        self.estado.setStyleSheet("""
            QStatusBar {
                background-color: #252526;
                color: #858585;
                font-size: 12px;
                border-top: 1px solid #3C3C3C;
                padding: 5px;
            }
        """)
        home.setStatusBar(self.estado)

        # Configuración de teclas de acceso rápido
        self.shortcut_run_lexical = QtWidgets.QShortcut(QtGui.QKeySequence("F5"), home)
        self.shortcut_run_syntactic = QtWidgets.QShortcut(QtGui.QKeySequence("F6"), home)
        self.shortcut_open = QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+O"), home)
        self.shortcut_clear = QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+L"), home)
        self.shortcut_tree = QtWidgets.QShortcut(QtGui.QKeySequence("F7"), home)
        self.shortcut_output = QtWidgets.QShortcut(QtGui.QKeySequence("F9"), home)  # Ir a salida (atajo opcional)

        home.setCentralWidget(self.centralWidget)

        # Establecer texto inicial y tooltips
        self.retranslateUi(home)
        QtCore.QMetaObject.connectSlotsByName(home)

        # ===== Conexiones de UI básicas (navegación de diseño) =====
        self.bt_run.clicked.connect(lambda: self.analysisTabs.setCurrentWidget(self.outputTab))
        self.shortcut_output.activated.connect(lambda: self.analysisTabs.setCurrentWidget(self.outputTab))
        self.bt_output_clear.clicked.connect(self.tx_output.clear)

    # Actualizaciones para el método retranslateUi en la clase Ui_home
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

        self.bt_lexico.setText(_translate("home", "Analizar Léxico"))
        self.bt_lexico.setToolTip(_translate("home", "Realizar análisis léxico (F5)"))

        self.bt_sintactico.setText(_translate("home", "Analizar Sintaxis"))
        self.bt_sintactico.setToolTip(_translate("home", "Realizar análisis sintáctico (F6)"))

        self.bt_simbolos.setText(_translate("home", "Ver Tabla Símbolos"))
        self.bt_simbolos.setToolTip(_translate("home", "Mostrar tabla de símbolos"))

        self.bt_arbol.setText(_translate("home", "Visualizar Recorridos"))
        self.bt_arbol.setToolTip(_translate("home", "Visualización gráfica de recorridos: pre-orden, in-orden y post-orden (F7)"))

        self.bt_arbolLR.setText(_translate("home", "Generar Árbol LR"))

        self.bt_archivo.setText(_translate("home", "Cargar Archivo"))
        self.bt_archivo.setToolTip(_translate("home", "Abrir un archivo Java (Ctrl+O)"))

        self.bt_run.setText(_translate("home", "Run"))
        self.bt_run.setToolTip(_translate("home", "Ejecutar el código y mostrar la salida"))

        self.bt_limpiar.setText(_translate("home", "Limpiar"))
        self.bt_limpiar.setToolTip(_translate("home", "Limpiar todos los campos (Ctrl+L)"))

        # Tooltips de zoom (atalhos de teclado)
        self.bt_zoom_in.setToolTip(_translate("home", "Zoom + (Shift + “+”)"))
        self.bt_zoom_out.setToolTip(_translate("home", "Zoom - (Shift + “-”)"))

        self.sourceGroup.setTitle(_translate("home", "Código Fuente Java"))
        self.lb_output_status.setText(_translate("home", "Salida del código (solo diseño):"))
        self.bt_output_clear.setText(_translate("home", "Limpiar salida"))
