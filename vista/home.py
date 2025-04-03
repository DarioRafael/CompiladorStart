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

            QTextEdit {
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

        #self.tx_ingreso = QtWidgets.QTextEdit()
        self.tx_ingreso = CodeEditor()


        self.tx_ingreso.setPlaceholderText("Escribe tu código Java aquí o carga un archivo...")
        self.tx_ingreso.setLineWrapMode(QtWidgets.QTextEdit.NoWrap)
        self.tx_ingreso.setTabStopWidth(40)  # 4 espacios para tabs
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

        self.bt_limpiar = QtWidgets.QPushButton("Limpiar")
        self.bt_limpiar.setIcon(QtGui.QIcon.fromTheme("edit-clear"))
        self.bt_limpiar.setToolTip("Limpiar todo")

        self.topControls.addWidget(self.bt_archivo)
        self.topControls.addWidget(self.bt_limpiar)
        self.topControls.addStretch()

        self.mainLayout.addLayout(self.topControls)

        # Panel de análisis con pestañas
        self.analysisTabs = QtWidgets.QTabWidget()
        self.analysisTabs.setStyleSheet("""
            QTabWidget::tab-bar {
                alignment: center;
            }
        """)

        # Pestaña de análisis léxico
        self.lexicalTab = QtWidgets.QWidget()
        self.lexicalLayout = QtWidgets.QVBoxLayout(self.lexicalTab)

        # Usar tabla en lugar de textEdit para el análisis léxico
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

        # Pestaña de análisis sintáctico
        self.syntaxTab = QtWidgets.QWidget()
        self.syntaxLayout = QtWidgets.QVBoxLayout(self.syntaxTab)
        self.tx_sintactico = QtWidgets.QTextEdit()
        self.tx_sintactico.setPlaceholderText("Resultados del análisis sintáctico...")
        self.tx_sintactico.setReadOnly(True)
        self.syntaxLayout.addWidget(self.tx_sintactico)
        self.analysisTabs.addTab(self.syntaxTab, "Análisis Sintáctico")

        # Pestaña de tabla de símbolos
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

        self.bottomControls.addWidget(self.bt_lexico)
        self.bottomControls.addWidget(self.bt_sintactico)
        self.bottomControls.addWidget(self.bt_simbolos)
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

        home.setCentralWidget(self.centralWidget)

        # Establecer texto inicial y tooltips
        self.retranslateUi(home)
        QtCore.QMetaObject.connectSlotsByName(home)

    def retranslateUi(self, home):
        _translate = QtCore.QCoreApplication.translate
        home.setWindowTitle(_translate("home", "Analizador de Código Java"))
        self.analysisTabs.setTabText(0, _translate("home", "Análisis Léxico"))
        self.analysisTabs.setTabText(1, _translate("home", "Análisis Sintáctico"))
        self.analysisTabs.setTabText(2, _translate("home", "Tabla de Símbolos"))
        self.bt_lexico.setText(_translate("home", "Analizar Léxico"))
        self.bt_lexico.setToolTip(_translate("home", "Realizar análisis léxico (F5)"))
        self.bt_sintactico.setText(_translate("home", "Analizar Sintaxis"))
        self.bt_sintactico.setToolTip(_translate("home", "Realizar análisis sintáctico (F6)"))
        self.bt_simbolos.setText(_translate("home", "Ver Tabla Símbolos"))
        self.bt_simbolos.setToolTip(_translate("home", "Mostrar tabla de símbolos"))
        self.bt_archivo.setText(_translate("home", "Cargar Archivo"))
        self.bt_archivo.setToolTip(_translate("home", "Abrir un archivo Java (Ctrl+O)"))
        self.bt_limpiar.setText(_translate("home", "Limpiar"))
        self.bt_limpiar.setToolTip(_translate("home", "Limpiar todos los campos (Ctrl+L)"))
        self.sourceGroup.setTitle(_translate("home", "Código Fuente Java"))