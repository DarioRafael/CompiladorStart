# -*- coding: utf-8 -*-
import os
import re
import shutil
import tempfile

from PyQt5 import QtCore


class JavaRunner(QtCore.QObject):

    started = QtCore.pyqtSignal(str)
    output = QtCore.pyqtSignal(str)
    finished = QtCore.pyqtSignal(int)
    error = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._tmpdir = None
        self._proc = None
        self._class_name = None

    def stop(self):
        if self._proc and self._proc.state() != QtCore.QProcess.NotRunning:
            self._proc.kill()

    # -------------------------------
    # API principal
    # -------------------------------
    def run_code(self, source_code: str):
        self._cleanup()

        if not source_code.strip():
            self.error.emit("No hay código para ejecutar.")
            self.finished.emit(1)
            return

        # Extraer nombre de clase pública (o fallback)
        class_name = self._extract_public_class(source_code) or "Main"
        self._class_name = class_name

        # Crear dir temporal y escribir archivo
        self._tmpdir = tempfile.mkdtemp(prefix="java_run_")
        java_path = os.path.join(self._tmpdir, f"{class_name}.java")
        try:
            with open(java_path, "w", encoding="utf-8") as f:
                f.write(source_code)
        except Exception as e:
            self.error.emit(f"No se pudo escribir el archivo temporal: {e}")
            self.finished.emit(1)
            return

        # Compilar
        self._compile(java_path)

    # -------------------------------
    # Utilidades
    # -------------------------------
    _re_public_class = re.compile(r'^\s*public\s+class\s+([A-Za-z_]\w*)', re.MULTILINE)

    def _extract_public_class(self, src: str):
        m = self._re_public_class.search(src)
        return m.group(1) if m else None

    # -------------------------------
    # Compilación / Ejecución
    # -------------------------------
    def _compile(self, java_path: str):
        if not shutil.which("javac"):
            self.error.emit("No se encontró 'javac' en PATH. Instala JDK y configura PATH.")
            self.finished.emit(1)
            return

        self.started.emit("compile")

        self._proc = QtCore.QProcess(self)
        self._proc.setProgram("javac")
        self._proc.setArguments(["-d", self._tmpdir, java_path])
        self._wire_process(step="compile")
        self._proc.start()

    def _run(self):
        if not shutil.which("java"):
            self.error.emit("No se encontró 'java' en PATH. Instala JRE/JDK y configura PATH.")
            self.finished.emit(1)
            return

        self.started.emit("run")

        self._proc = QtCore.QProcess(self)
        self._proc.setProgram("java")
        self._proc.setArguments(["-cp", self._tmpdir, self._class_name])
        self._wire_process(step="run")
        self._proc.start()

    def _wire_process(self, step: str):
        self._proc.readyReadStandardOutput.connect(
            lambda: self._emit_text(self._proc.readAllStandardOutput()))
        self._proc.readyReadStandardError.connect(
            lambda: self._emit_text(self._proc.readAllStandardError()))
        self._proc.finished.connect(lambda code, _st: self._on_finished(step, code))

    def _emit_text(self, qbytearray):
        try:
            text = bytes(qbytearray).decode("utf-8", errors="ignore")
        except Exception:
            text = str(bytes(qbytearray), errors="ignore")
        if text:
            self.output.emit(text)

    def _on_finished(self, step: str, code: int):
        if step == "compile":
            if code == 0:
                self._run()
            else:
                self.finished.emit(code)
        else:
            self.finished.emit(code)

    def _cleanup(self):
        # Detener proceso previo
        if self._proc and self._proc.state() != QtCore.QProcess.NotRunning:
            self._proc.kill()
        self._proc = None

        # Borrar carpeta temporal anterior
        if self._tmpdir and os.path.isdir(self._tmpdir):
            try:
                shutil.rmtree(self._tmpdir, ignore_errors=True)
            except Exception:
                pass
        self._tmpdir = None
        self._class_name = None
