# -*- coding: utf-8 -*-
from PyQt5.QtGui import QSyntaxHighlighter, QTextCharFormat, QFont, QColor
from PyQt5.QtCore import QRegExp


class JavaHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super(JavaHighlighter, self).__init__(parent)
        self.highlighting_rules = []

        # Palabras clave
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("#569CD6"))
        keyword_format.setFontWeight(QFont.Bold)

        java_keywords = [
            "abstract", "assert", "boolean", "break", "byte", "case", "catch",
            "char", "class", "const", "continue", "default", "do", "double",
            "else", "enum", "extends", "final", "finally", "float", "for", "if",
            "implements", "import", "instanceof", "int", "interface", "long",
            "native", "new", "package", "private", "protected", "public", "return",
            "short", "static", "strictfp", "super", "switch", "synchronized",
            "this", "throw", "throws", "transient", "try", "void", "volatile", "while"
        ]
        for kw in java_keywords:
            self.highlighting_rules.append((QRegExp(r"\b" + kw + r"\b"), keyword_format))

        # Tipos comunes
        type_format = QTextCharFormat()
        type_format.setForeground(QColor("#4EC9B0"))
        type_format.setFontWeight(QFont.Bold)
        for t in ["String", "Object", "List", "Map", "Set"]:
            self.highlighting_rules.append((QRegExp(r"\b" + t + r"\b"), type_format))

        # Literales y números
        lit_format = QTextCharFormat()
        lit_format.setForeground(QColor("#B5CEA8"))
        for lit in ["true", "false", "null"]:
            self.highlighting_rules.append((QRegExp(r"\b" + lit + r"\b"), lit_format))
        self.highlighting_rules.append((QRegExp(r"\b[0-9]+\b"), lit_format))

        # Cadenas y caracteres
        str_format = QTextCharFormat()
        str_format.setForeground(QColor("#CE9178"))
        rx = QRegExp("\".*\"")
        rx.setMinimal(True)
        self.highlighting_rules.append((rx, str_format))
        self.highlighting_rules.append((QRegExp(r"'.'"), str_format))

        # Comentarios
        single_cmt = QTextCharFormat()
        single_cmt.setForeground(QColor("#608B4E"))
        self.highlighting_rules.append((QRegExp(r"//[^\n]*"), single_cmt))

        self.multiline_comment_format = QTextCharFormat()
        self.multiline_comment_format.setForeground(QColor("#608B4E"))
        self.comment_start_expression = QRegExp(r"/\*")
        self.comment_end_expression = QRegExp(r"\*/")

    def highlightBlock(self, text):
        # Reglas simples
        for pattern, fmt in self.highlighting_rules:
            expr = QRegExp(pattern)
            index = expr.indexIn(text)
            while index >= 0:
                length = expr.matchedLength()
                self.setFormat(index, length, fmt)
                index = expr.indexIn(text, index + length)

        # Comentarios multilínea
        self.setCurrentBlockState(0)
        start_index = 0
        if self.previousBlockState() != 1:
            start_index = self.comment_start_expression.indexIn(text)

        while start_index >= 0:
            end_index = self.comment_end_expression.indexIn(text, start_index)
            if end_index == -1:
                self.setCurrentBlockState(1)
                comment_length = len(text) - start_index
            else:
                comment_length = end_index - start_index + self.comment_end_expression.matchedLength()
            self.setFormat(start_index, comment_length, self.multiline_comment_format)
            start_index = self.comment_start_expression.indexIn(text, start_index + comment_length)
