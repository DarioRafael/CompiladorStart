from dataclasses import dataclass
from typing import List, Optional
from PyQt5 import QtCore, QtGui, QtWidgets

@dataclass
class ErrorItem:
    idx: int
    tipo: str           # "Léxico" | "Sintáctico" | "Semántico" | etc.
    mensaje: str
    linea: Optional[int] = None
    columna: Optional[int] = None
    sugerencia: str = ""

class ErrorTableView:
    """
    Encapsula la Tabla de Errores:
      - carga de filas con colores
      - limpiar
      - enfocar pestaña
      - mostrar mensaje en status bar (si existe)
    """
    def __init__(
        self,
        table: QtWidgets.QTableWidget,
        tab_widget: Optional[QtWidgets.QTabWidget] = None,
        tab_page: Optional[QtWidgets.QWidget] = None,
        status_bar: Optional[QtWidgets.QStatusBar] = None
    ):
        self.table = table
        self.tab_widget = tab_widget
        self.tab_page = tab_page
        self.status_bar = status_bar

        # Ajustes base (por si el creador genérico no lo hace)
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["#", "Tipo", "Mensaje", "Línea"])
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)  # #
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)  # Tipo
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)  # Mensaje
        # La línea la mostraremos junto con el mensaje, no en una columna aparte

        # Colores
        self.color_lex = QtGui.QColor("#56B6C2")
        self.color_sint = QtGui.QColor("#C678DD")
        self.color_sem = QtGui.QColor("#E5C07B")
        self.color_msg = QtGui.QColor("#FFFFFF")
        self.bg_dark1 = QtGui.QColor("#1E1E1E")
        self.bg_dark2 = QtGui.QColor("#2D2D2D")

    # -------- API pública --------
    def clear(self):
        self.table.setRowCount(0)

    def focus(self):
        if self.tab_widget is not None and self.tab_page is not None:
            self.tab_widget.setCurrentWidget(self.tab_page)

    def set_status(self, text: str, msec: int = 3000):
        if self.status_bar is not None:
            self.status_bar.showMessage(text, msec)

    def load_items(self, items: List[ErrorItem]):
        self.table.setUpdatesEnabled(False)
        self.table.clearContents()
        self.table.setRowCount(len(items))

        alt = False
        for row, it in enumerate(items):
            bg = self.bg_dark1 if alt else self.bg_dark2
            alt = not alt

            cols = [
                str(it.idx),
                it.tipo,
                it.mensaje,
                "" if it.linea is None else str(it.linea),
                "" if it.columna is None else str(it.columna),
                it.sugerencia or "",
            ]
            for col_idx, text in enumerate(cols):
                cell = QtWidgets.QTableWidgetItem(text)
                cell.setTextAlignment(QtCore.Qt.AlignCenter)
                cell.setBackground(bg)
                # Color por tipo en columna "Tipo"
                if col_idx == 1:
                    t = (it.tipo or "").upper()
                    if t.startswith("LÉXICO") or t.startswith("LEXICO"):
                        cell.setForeground(self.color_lex)
                    elif t.startswith("SINTÁCTICO") or t.startswith("SINTACTICO"):
                        cell.setForeground(self.color_sint)
                    elif t.startswith("SEMÁNTICO") or t.startswith("SEMANTICO"):
                        cell.setForeground(self.color_sem)
                # Mensaje siempre blanco legible
                if col_idx == 2:
                    cell.setForeground(self.color_msg)
                self.table.setItem(row, col_idx, cell)

        self.table.setUpdatesEnabled(True)

    def show_items(self, items: List[ErrorItem], status_prefix: str = "Tabla de errores actualizada"):
        self.load_items(items)
        self.focus()
        self.set_status(f"{status_prefix}: {len(items)} entradas.", 3000)

    @staticmethod
    def from_demo() -> List[ErrorItem]:
        return [
            ErrorItem(1, "Sintáctico", "Se esperaba ';' antes de '}'", 5, 18, "Agrega ';' al final de la instrucción"),
            ErrorItem(2, "Semántico", "Variable 'x' no declarada", 8, 9, "Declara 'x' antes de usarla"),
            ErrorItem(3, "Léxico", "Token inválido '@'", 2, 12, "Elimina o corrige el carácter"),
        ]
