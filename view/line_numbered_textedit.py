# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtGui, QtWidgets


class LineNumberArea(QtWidgets.QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self._editor = editor

    def sizeHint(self):
        return QtCore.QSize(self._editor.lineNumberAreaWidth(), 0)

    def paintEvent(self, event):
        self._editor.lineNumberAreaPaintEvent(event)

    def wheelEvent(self, event: QtGui.QWheelEvent):
        # Reenvía el evento al editor para que funcione el zoom sobre el gutter
        self._editor.wheelEvent(event)


class CodeEditor(QtWidgets.QPlainTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)

        # ==== Básico ====
        self.setLineWrapMode(QtWidgets.QPlainTextEdit.NoWrap)
        self.setTabStopDistance(4 * self.fontMetrics().horizontalAdvance(" "))

        font = QtGui.QFont("Consolas", 20)
        self.setFont(font)

        pal = self.palette()
        pal.setColor(QtGui.QPalette.Base, QtGui.QColor("#1E1E1E"))
        pal.setColor(QtGui.QPalette.Text, QtGui.QColor("#DCDCDC"))
        self.setPalette(pal)

        # ==== Contenedores para extraSelections ====
        self._externalExtraSelections = []
        self._trailing_extras = []
        self._brace_extras = []
        self._error_lines = set()

        # ==== Área de números de línea ====
        self._lineNumberArea = LineNumberArea(self)
        self.blockCountChanged.connect(self._updateLineNumberAreaWidth)
        self.updateRequest.connect(self._updateLineNumberArea)
        self.cursorPositionChanged.connect(self._onCursorMoved)
        self._updateLineNumberAreaWidth(0)

        # ==== Inicializaciones ====
        self._init_indent_guides()
        self._init_ruler()
        self._init_trailing_ws()
        self._init_brace_match()
        self._init_current_line_highlight()

        # Eventos de cambio de texto
        self.textChanged.connect(self._update_trailing_ws_highlight)

        # Scrollbars
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)

        # Composición inicial
        self._recompose_extras()

    # ========= Zoom público (para botones) =========
    def zoom_in(self, checked: bool = False):
        self._apply_zoom_steps(+1)

    def zoom_out(self, checked: bool = False):
        self._apply_zoom_steps(-1)

    def zoom_reset(self, size_pt: int = 11, checked: bool = False):
        font = self.font()
        font.setPointSize(size_pt)
        self.setFont(font)
        self.setTabStopDistance(4 * self.fontMetrics().horizontalAdvance(" "))
        self._updateLineNumberAreaWidth(0)
        self._recompose_extras()
        self.viewport().update()
        self._lineNumberArea.update()

    # =========================================================
    # Área de números de línea
    # =========================================================
    def lineNumberAreaWidth(self):
        digits = len(str(max(1, self.blockCount())))
        return 10 + self.fontMetrics().horizontalAdvance("9") * digits

    def _updateLineNumberAreaWidth(self, _):
        self.setViewportMargins(self.lineNumberAreaWidth(), 0, 0, 0)

    def _updateLineNumberArea(self, rect, dy):
        if dy:
            self._lineNumberArea.scroll(0, dy)
        else:
            self._lineNumberArea.update(0, rect.y(), self._lineNumberArea.width(), rect.height())
        if rect.contains(self.viewport().rect()):
            self._updateLineNumberAreaWidth(0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self._lineNumberArea.setGeometry(QtCore.QRect(cr.left(), cr.top(),
                                                      self.lineNumberAreaWidth(), cr.height()))

    def lineNumberAreaPaintEvent(self, event):
        painter = QtGui.QPainter(self._lineNumberArea)
        painter.fillRect(event.rect(), QtGui.QColor("#252526"))
        painter.setFont(self.font())

        block = self.firstVisibleBlock()
        blockNumber = block.blockNumber()
        top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        bottom = top + self.blockBoundingRect(block).height()

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(blockNumber + 1)
                color = QtGui.QColor("#FF6B68") if (blockNumber + 1) in self._error_lines else QtGui.QColor("#858585")
                painter.setPen(color)
                painter.drawText(0, int(top), self._lineNumberArea.width() - 5, self.fontMetrics().height(),
                                 QtCore.Qt.AlignRight, number)

            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            blockNumber += 1

    # =========================================================
    # Destacados / Resaltados
    # =========================================================
    def _init_current_line_highlight(self):
        self.cursorPositionChanged.connect(self._update_current_line_selection)
        self._update_current_line_selection()

    def _update_current_line_selection(self):
        selection = QtWidgets.QTextEdit.ExtraSelection()
        lineColor = QtGui.QColor("#333333")
        selection.format.setBackground(lineColor)
        selection.format.setProperty(QtGui.QTextFormat.FullWidthSelection, True)
        selection.cursor = self.textCursor()
        selection.cursor.clearSelection()
        self._current_line_fmt = selection
        self._recompose_extras()

    def _init_indent_guides(self):
        pass

    def _init_ruler(self):
        pass

    def _init_trailing_ws(self):
        self._trailing_extras = []

    def _update_trailing_ws_highlight(self):
        self._trailing_extras = []
        doc = self.document()
        block = doc.firstBlock()
        while block.isValid():
            text = block.text()
            m = len(text) - len(text.rstrip())
            if m > 0:
                sel = QtWidgets.QTextEdit.ExtraSelection()
                sel.cursor = QtGui.QTextCursor(block)
                sel.cursor.movePosition(QtGui.QTextCursor.EndOfBlock)
                sel.cursor.movePosition(QtGui.QTextCursor.Left, QtGui.QTextCursor.KeepAnchor, m)
                sel.format.setBackground(QtGui.QColor("#553333"))
                self._trailing_extras.append(sel)
            block = block.next()
        self._recompose_extras()

    def _init_brace_match(self):
        self._brace_extras = []

    # =========================================================
    # ExtraSelections composition
    # =========================================================
    def _compose_extra_selections(self):
        ext = self._externalExtraSelections or []
        tr = self._trailing_extras or []
        br = self._brace_extras or []
        cur = [self._current_line_fmt] if hasattr(self, "_current_line_fmt") else []
        return ext + tr + br + cur

    def _recompose_extras(self):
        super().setExtraSelections(self._compose_extra_selections())

    # =========================================================
    # Errores en gutter
    # =========================================================
    # En CodeEditor
    def set_error_lines(self, lines):
        # Acepta iterables con enteros (1-based). Filtra None/<=0.
        try:
            clean = {int(x) for x in (lines or []) if isinstance(x, (int,)) and x > 0}
        except Exception:
            clean = set()
            for x in (lines or []):
                try:
                    xi = int(x)
                    if xi > 0:
                        clean.add(xi)
                except Exception:
                    pass
        self._error_lines = clean
        self._lineNumberArea.update()

    # =========================================================
    # Eventos
    # =========================================================
    def setExtraSelections(self, selections):
        """Captura selecciones externas (diagnósticos) y recompone con las internas."""
        self._externalExtraSelections = list(selections or [])
        self._recompose_extras()

    def _onCursorMoved(self):
        self._update_current_line_selection()

    # ============================
    # Zoom con Shift + rueda
    # ============================
    def wheelEvent(self, event: QtGui.QWheelEvent):
        mods = event.modifiers()
        wants_zoom = bool(mods & QtCore.Qt.ShiftModifier)
        if wants_zoom:
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

    # ============================
    # Zoom con Shift + (+/-)
    # ============================
    def keyPressEvent(self, event: QtGui.QKeyEvent):
        super().keyPressEvent(event)

    # Lógica central del zoom
    def _apply_zoom_steps(self, steps: int):
        font = self.font()
        size = font.pointSize() if font.pointSize() > 0 else max(
            8, int(font.pixelSize() / self.logicalDpiY() * 72)
        )
        new_size = max(8, min(48, size + steps))  # límites 8–48 pt
        if new_size == size:
            return
        font.setPointSize(new_size)
        self.setFont(font)
        self.setTabStopDistance(4 * self.fontMetrics().horizontalAdvance(" "))
        self._updateLineNumberAreaWidth(0)
        self._recompose_extras()
        self.viewport().update()
        self._lineNumberArea.update()
