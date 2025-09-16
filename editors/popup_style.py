# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import QListView, QAbstractItemView, QGraphicsDropShadowEffect
from PyQt5.QtGui import QFont, QPalette, QColor
from PyQt5.QtCore import Qt, QSize

class StyledCompleterPopup(QListView):
    """
    Popup para QCompleter con estilo moderno, altura dinámica y mínimo visible
    (evita que con 1 solo elemento se vea todo negro).
    """
    def __init__(self, parent=None, *, max_visible_rows=8):
        super().__init__(parent)
        self._max_visible_rows = max_visible_rows
        self._row_height = None
        self._setup_ui()

    def _setup_ui(self):
        # Interacción
        self.setUniformItemSizes(True)
        self.setAlternatingRowColors(False)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.setMouseTracking(True)

        # Fuente
        f = QFont("Consolas", 11)
        self.setFont(f)

        self.setSpacing(2)
        self.setStyleSheet(self._style_sheet())

        # Paleta
        pal = QPalette()
        pal.setColor(QPalette.Base, QColor("#1f1f1f"))
        pal.setColor(QPalette.Text, QColor("#f0f0f0"))
        self.setPalette(pal)

        # Sombra
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(22)
        shadow.setColor(QColor(0, 0, 0, 180))
        shadow.setOffset(0, 8)
        self.setGraphicsEffect(shadow)

        # Ancho mínimo para que no colapse
        self.setMinimumWidth(260)

        # Altura mínima por si hay 1 solo ítem (se ajusta de nuevo en sync_to_model)
        self._ensure_min_height()

    def _style_sheet(self) -> str:
        bg      = "#1f1f1f"
        border  = "#2b2b2b"
        hover   = "#2a2a2a"
        sel_bg  = "#3478f6"
        sel_fg  = "#ffffff"
        fg      = "#f0f0f0"
        sep     = "#303030"
        radius  = 12
        pad_y   = 10
        pad_x   = 16

        return f"""
QListView {{
    background: {bg};
    color: {fg};
    border: 1px solid {border};
    border-radius: {radius}px;
    outline: none;
    padding: 8px;
    selection-background-color: {sel_bg};
    selection-color: {sel_fg};
}}
QListView::item {{
    padding: {pad_y}px {pad_x}px;
    border-bottom: 1px solid {sep};
    margin: 1px 0;
}}
QListView::item:last {{
    border-bottom: 0;
}}
QListView::item:hover {{
    background: {hover};
}}
QListView::item:selected {{
    background: {sel_bg};
    color: {sel_fg};
}}
QScrollBar:vertical {{
    background: transparent;
    width: 10px;
    margin: 6px 2px 6px 0;
}}
QScrollBar::handle:vertical {{
    background: {hover};
    min-height: 30px;
    border-radius: 5px;
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}
"""

    def sizeHintForRowSafe(self) -> int:
        """Estimación robusta de altura de fila (fuente + padding)."""
        if self._row_height is not None:
            return self._row_height
        # base: alto de fuente + padding (aprox coincide con stylesheet)
        self._row_height = max(self.fontMetrics().height() + 16, 26)
        return self._row_height

    def _ensure_min_height(self):
        """Asegura una altura mínima suficiente para ver 1 fila cómoda."""
        row_h = self.sizeHintForRowSafe()
        # + padding del contenedor (8 arriba + 8 abajo) ~ 16
        self.setMinimumHeight(row_h + 16)

    def sync_to_model(self, model):
        """
        Llamar tras actualizar el modelo del QCompleter.
        Ajusta altura (hasta max_visible_rows) y se asegura de que con 1 ítem se vea.
        """
        rows = model.rowCount()
        row_h = self.sizeHintForRowSafe()

        # Altura objetivo: min(n_filas, max_visible_rows)
        visible_rows = min(rows, self._max_visible_rows) if rows > 0 else 1
        target_h = (row_h * visible_rows) + 16  # + padding del contenedor

        # Fijar altura resultante
        self.setFixedHeight(target_h)
        # Reasegurar mínimo por si rows == 1
        self._ensure_min_height()

        # Selecciona la primera fila para que siempre se pinte algo
        if rows > 0:
            idx0 = model.index(0, 0)
            if idx0.isValid():
                self.setCurrentIndex(idx0)
