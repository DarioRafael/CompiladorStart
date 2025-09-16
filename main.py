#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from PyQt5.QtWidgets import QApplication
from controllers.main_window import Main


def iniciar():
    app = QApplication(sys.argv)
    ventana = Main()
    ventana.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    iniciar()
