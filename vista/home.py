# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui, QtWidgets


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
                font-family: 'Segoe UI';
            }

            QTextEdit {
                background-color: #1E1E1E;
                color: #DCDCDC;
                border: 2px solid #3E3E3E;
                border-radius: 4px;
                padding: 10px;
                font-family: 'Consolas';
                font-size: 12px;
                selection-background-color: #3E3E3E;
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
        self.titleLabel = QtWidgets.QLabel("Compilador Avanzado", self.centralWidget)
        self.titleLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.titleLabel.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #569CD6;
                padding: 10px;
            }
        """)
        self.mainLayout.addWidget(self.titleLabel)

        # Área de código fuente
        self.sourceGroup = QtWidgets.QGroupBox("Código Fuente")
        self.sourceGroup.setStyleSheet("QGroupBox { font-size: 16px; }")
        self.sourceLayout = QtWidgets.QVBoxLayout(self.sourceGroup)

        self.tx_ingreso = QtWidgets.QTextEdit()
        self.tx_ingreso.setPlaceholderText("Escribe tu código aquí o carga un archivo...")
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

        self.bt_limpiar = QtWidgets.QPushButton()
        self.bt_limpiar.setIcon(QtGui.QIcon.fromTheme("edit-clear"))
        self.bt_limpiar.setToolTip("Limpiar todo")

        self.topControls.addWidget(self.bt_archivo)
        self.topControls.addWidget(self.bt_limpiar)
        self.topControls.addStretch()

        self.mainLayout.addLayout(self.topControls)

        # Panel de análisis con pestañas
        self.analysisTabs = QtWidgets.QTabWidget()

        # Pestaña de análisis léxico
        self.lexicalTab = QtWidgets.QWidget()
        self.lexicalLayout = QtWidgets.QVBoxLayout(self.lexicalTab)
        self.tx_lexico = QtWidgets.QTextEdit()
        self.tx_lexico.setPlaceholderText("Resultados del análisis léxico...")
        self.lexicalLayout.addWidget(self.tx_lexico)
        self.analysisTabs.addTab(self.lexicalTab, "Léxico")

        # Pestaña de análisis sintáctico
        self.syntaxTab = QtWidgets.QWidget()
        self.syntaxLayout = QtWidgets.QVBoxLayout(self.syntaxTab)
        self.tx_sintactico = QtWidgets.QTextEdit()
        self.tx_sintactico.setPlaceholderText("Resultados del análisis sintáctico...")
        self.syntaxLayout.addWidget(self.tx_sintactico)
        self.analysisTabs.addTab(self.syntaxTab, "Sintáctico")

        self.mainLayout.addWidget(self.analysisTabs)

        # Controles inferiores
        self.bottomControls = QtWidgets.QHBoxLayout()
        self.bottomControls.setSpacing(20)

        self.bt_lexico = QtWidgets.QPushButton("Analizar Léxico")
        self.bt_lexico.setIcon(QtGui.QIcon.fromTheme("edit-find"))
        self.bt_lexico.setStyleSheet("background-color: #57A64A; border-color: #65B158;")

        self.bt_sintactico = QtWidgets.QPushButton("Analizar Sintaxis")
        self.bt_sintactico.setIcon(QtGui.QIcon.fromTheme("dialog-ok-apply"))
        self.bt_sintactico.setStyleSheet("background-color: #D69D45; border-color: #E0A64D;")

        self.bottomControls.addWidget(self.bt_lexico)
        self.bottomControls.addWidget(self.bt_sintactico)
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
            }
        """)
        home.setStatusBar(self.estado)

        home.setCentralWidget(self.centralWidget)

        self.retranslateUi(home)
        QtCore.QMetaObject.connectSlotsByName(home)

    def retranslateUi(self, home):
        _translate = QtCore.QCoreApplication.translate
        home.setWindowTitle(_translate("home", "Compilador Avanzado"))
        self.analysisTabs.setTabText(0, _translate("home", "Análisis Léxico"))
        self.analysisTabs.setTabText(1, _translate("home", "Análisis Sintáctico"))
        self.bt_lexico.setText(_translate("home", "Analizar Léxico"))
        self.bt_sintactico.setText(_translate("home", "Analizar Sintaxis"))
        self.bt_archivo.setText(_translate("home", "Cargar Archivo"))
        self.bt_limpiar.setText(_translate("home", "Limpiar"))
        self.sourceGroup.setTitle(_translate("home", "Código Fuente"))