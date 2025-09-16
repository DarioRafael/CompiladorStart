# -*- coding: utf-8 -*-
# editors/completer.py
from typing import List, Callable, Tuple
import re
from PyQt5.QtCore import Qt, QStringListModel, QObject, QEvent, QTimer
from PyQt5.QtWidgets import QCompleter, QListView, QApplication
from PyQt5.QtGui import QTextCursor
from editors.popup_style import StyledCompleterPopup

JAVA_KEYWORDS = [
    "if", "else", "for", "while", "do", "switch", "case", "default",
    "break", "continue", "return", "try", "catch", "finally", "throw", "throws",
    "public", "private", "protected", "static", "final", "abstract",
    "native", "strictfp", "synchronized", "transient", "volatile",
    "class", "interface", "enum", "extends", "implements",
    "void", "int", "long", "short", "byte", "float", "double", "boolean", "char", "String",
    "new", "this", "super", "package", "import", "instanceof",
    "true", "false", "null",
]

SYSTEM_OUT_MEMBERS = ["print", "println", "printf"]

SNIPPETS = {
    "sout": "System.out.println($0);",
    "soutf": "System.out.printf($0);",
    "psvm": "public static void main(String[] args) {\n    $0\n}",
    "fori": "for (int i = 0; i < $0; i++) {\n}",
    "if": "if ($0) {\n}",
    "else": "else {\n    $0\n}",
    "!": (
        "public class Main {\n"
        "    public static void main(String[] args) {\n"
        "        $0\n"
        "    }\n"
        "}"
    ),
}

_word_re = re.compile(r"[A-Za-z_][A-Za-z_0-9]*$")

def _current_prefix(editor) -> str:
    doc = editor.document()
    tc = editor.textCursor()
    pos = tc.position()

    start = max(0, pos - 128)
    try:
        cur = QTextCursor(doc)
        cur.setPosition(start)
        cur.setPosition(pos, QTextCursor.KeepAnchor)
        text = cur.selectedText()
    except Exception:
        text = ""

    text = text.replace("\u2029", "\n").split("\n")[-1]
    m = _word_re.search(text)
    return m.group(0) if m else ""

class JavaAutoCompleter(QObject):
    def __init__(self, editor, dynamic_words_cb: Callable[[], List[str]]):
        super().__init__(editor)
        self.editor = editor
        self.dynamic_words_cb = dynamic_words_cb

        self.model = QStringListModel()
        self.completer = QCompleter(self.model)
        self.completer.setWidget(self.editor)  # anclado al editor
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)

        popup = StyledCompleterPopup(self.editor, max_visible_rows=8)
        self.completer.setPopup(popup)
        self._popup = popup  # <<< guarda referencia
        try:
            self.completer.setFilterMode(Qt.MatchContains)
        except Exception:
            pass
        self.completer.setWrapAround(False)
        self.completer.setCompletionMode(QCompleter.PopupCompletion)
        self.completer.setMaxVisibleItems(12)


        # Aceptar con activado (Enter/clic cuando el popup tiene foco)
        self.completer.activated[str].connect(self._insert_completion)
        # Aceptar también con clic aunque el foco lo tenga el editor
       # self.completer.popup().clicked.connect(self._on_popup_clicked)

        self.completer.popup().installEventFilter(self)

        self.editor.installEventFilter(self)
        self.editor.viewport().installEventFilter(self)

        self.editor.textChanged.connect(self._maybe_complete)
        self._last_prefix = ""

        # offset vertical para mostrar el popup DEBAJO del cursor
        self._popup_offset_y = self.editor.fontMetrics().height() + 4

    # ---------- helpers ----------
    def _refresh_candidates(self, prefix: str, is_member: bool) -> List[str]:
        base = list(JAVA_KEYWORDS)
        try:
            dyn = self.dynamic_words_cb() or []
            base.extend(dyn)
        except Exception:
            pass

        if is_member:
            return SYSTEM_OUT_MEMBERS

        base.extend(list(SNIPPETS.keys()))

        pref = (prefix or "").lower()
        uniq, seen = [], set()
        for w in base:
            if w and w not in seen:
                seen.add(w)
                uniq.append(w)

        begins = [w for w in uniq if w.lower().startswith(pref)]
        contains = [w for w in uniq if pref in w.lower() and not w.lower().startswith(pref)]
        return begins + contains

    def _is_member_trigger(self) -> bool:
        tc = self.editor.textCursor()
        pos = tc.position()
        if pos == 0:
            return False
        tc.setPosition(pos - 1)
        tc.setPosition(pos, QTextCursor.KeepAnchor)
        return tc.selectedText() == "."

    # ---------- insertion ----------
    def _text_for_accept(self) -> str:
        # 1) lo que esté realmente seleccionado en el popup
        try:
            idx = self.completer.popup().currentIndex()
            if idx.isValid():
                txt = self.completer.completionModel().data(idx, Qt.DisplayRole)
                if txt:
                    return str(txt)
        except Exception:
            pass
        # 2) fallback: currentCompletion o primer item
        try:
            txt = self.completer.currentCompletion()
            if txt:
                return str(txt)
        except Exception:
            pass
        try:
            idx0 = self.completer.completionModel().index(0, 0)
            txt = self.completer.completionModel().data(idx0, Qt.DisplayRole)
            if txt:
                return str(txt)
        except Exception:
            pass
        return ""

    def _insert_completion(self, text: str):
        if text in SNIPPETS:
            self._insert_snippet(SNIPPETS[text])
            return
        prefix = _current_prefix(self.editor)
        tc = self.editor.textCursor()
        tc.beginEditBlock()
        for _ in range(len(prefix)):
            tc.deletePreviousChar()
        tc.insertText(text)
        tc.endEditBlock()
        self.completer.popup().hide()

    def _insert_snippet(self, snippet: str):
        prefix = _current_prefix(self.editor)
        out = snippet
        cursor_offset = out.find("$0")
        if cursor_offset >= 0:
            out = out.replace("$0", "")
        tc = self.editor.textCursor()
        tc.beginEditBlock()
        for _ in range(len(prefix)):
            tc.deletePreviousChar()
        anchor_pos = tc.position()
        tc.insertText(out)
        if cursor_offset >= 0:
            tc.setPosition(anchor_pos + cursor_offset)
        self.editor.setTextCursor(tc)
        tc.endEditBlock()
        self.completer.popup().hide()

    def _on_popup_clicked(self, index):
        txt = self.completer.completionModel().data(index, Qt.DisplayRole)
        if txt:
            self._insert_completion(str(txt))

    # ---------- triggers ----------
    def _position_popup(self, select_first=False):
        cr = self.editor.cursorRect()
        cr.translate(0, self._popup_offset_y)  # debajo del caret
        cr.setWidth(280)
        self.completer.complete(cr)

        if select_first:
            try:
                self.completer.setCurrentRow(0)
            except Exception:
                try:
                    idx0 = self.completer.completionModel().index(0, 0)
                    if idx0.isValid():
                        self.completer.popup().setCurrentIndex(idx0)
                except Exception:
                    pass

    def _maybe_complete(self):
        if not self.editor.isVisible():
            return

        was_visible = self.completer.popup().isVisible()
        is_member = self._is_member_trigger()
        prefix = "" if is_member else _current_prefix(self.editor)

        if not is_member and len(prefix) < 1:
            self.completer.popup().hide()
            return

        if prefix != self._last_prefix or is_member:
            cands = self._refresh_candidates(prefix, is_member)
            if not cands:
                self.completer.popup().hide()
                return
            self.model.setStringList(cands)
            try:
                self.completer.setCompletionPrefix(prefix)
            except Exception:
                pass
            self._last_prefix = prefix

        self._position_popup(select_first=not was_visible)

    # ---------- events ----------
    def eventFilter(self, obj, ev):
        if obj is self.completer.popup():
            if ev.type() == QEvent.KeyPress:
                if ev.key() in (Qt.Key_Tab, Qt.Key_Enter, Qt.Key_Return):
                    txt = self._text_for_accept()
                    if txt:
                        self._insert_completion(txt)
                        return True
                if ev.key() == Qt.Key_Escape:
                    self.completer.popup().hide()
                    return True
            return False

        if obj is self.editor or obj is self.editor.viewport():
            if ev.type() == QEvent.KeyPress:
                popup_visible = self.completer.popup().isVisible()

                # Ctrl+Espacio -> forzar popup
                if ev.key() == Qt.Key_Space and (ev.modifiers() & Qt.ControlModifier):
                    QTimer.singleShot(0, self._force_popup)
                    return True

                if popup_visible:
                    # ⬇️ reenvía navegación al popup
                    if ev.key() in (Qt.Key_Up, Qt.Key_Down, Qt.Key_PageUp, Qt.Key_PageDown, Qt.Key_Home, Qt.Key_End):
                        QApplication.sendEvent(self.completer.popup(), ev)
                        return True

                    if ev.key() == Qt.Key_Tab:
                        txt = self._text_for_accept()
                        if txt:
                            self._insert_completion(txt)
                            return True
                    if ev.key() == Qt.Key_Escape:
                        self.completer.popup().hide()
                        return True
                    if ev.key() in (Qt.Key_Enter, Qt.Key_Return):
                        return False  # salto de línea normal

                QTimer.singleShot(0, self._maybe_complete)
                return False

        return super().eventFilter(obj, ev)

    def _force_popup(self):
        if not self.editor.isVisible():
            return
        is_member = self._is_member_trigger()
        prefix = "" if is_member else _current_prefix(self.editor)
        cands = self._refresh_candidates(prefix, is_member)
        if not cands:
            self.completer.popup().hide()
            return
        self.model.setStringList(cands)
        try:
            self.completer.setCompletionPrefix(prefix)
        except Exception:
            pass
        self._position_popup()
