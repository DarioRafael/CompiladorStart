# -*- coding: utf-8 -*-
import os
import re
import sys
import shutil
import tempfile
from pathlib import Path
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

        # Rutas al JDK embebido (si existe)
        self._java_paths = self._locate_embedded_java()

    # ===============================
    # API principal
    # ===============================
    def stop(self):
        if self._proc and self._proc.state() != QtCore.QProcess.NotRunning:
            self._proc.kill()

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

    # ===============================
    # Utilidades
    # ===============================
    _re_public_class = re.compile(r'^\s*public\s+class\s+([A-Za-z_]\w*)', re.MULTILINE)

    def _extract_public_class(self, src: str):
        m = self._re_public_class.search(src)
        return m.group(1) if m else None

    def _find_base_with_runtimes(self) -> Path:
        """
        Devuelve el primer directorio ascendente (o _MEIPASS/CWD) que contenga 'runtimes'.
        """
        # 1) PyInstaller
        meipass = getattr(sys, "_MEIPASS", None)
        if meipass:
            p = Path(meipass)
            if (p / "runtimes").exists():
                return p

        # 2) Ascender desde este archivo
        here = Path(__file__).resolve()
        for p in [here.parent, *here.parents]:
            if (p / "runtimes").exists():
                return p

        # 3) CWD como último intento
        cwd = Path.cwd()
        if (cwd / "runtimes").exists():
            return cwd

        # Fallback: carpeta del archivo
        return here.parent

    def _locate_embedded_java(self):
        """
        Busca un JDK embebido en runtimes/<os>/jdk y devuelve rutas.
        Estructuras esperadas:
          - Windows/Linux: runtimes/<os>/jdk/bin/{java,javac}
          - macOS:         runtimes/mac/jdk/Contents/Home/bin/{java,javac}
        """
        base_dir = self._find_base_with_runtimes()

        platform = "win" if os.name == "nt" else ("mac" if sys.platform == "darwin" else "linux")
        if platform == "mac":
            jdk_home = base_dir / "runtimes" / platform / "jdk" / "Contents" / "Home"
        else:
            jdk_home = base_dir / "runtimes" / platform / "jdk"

        bin_dir = jdk_home / "bin"
        java_exe = "java.exe" if os.name == "nt" else "java"
        javac_exe = "javac.exe" if os.name == "nt" else "javac"

        java_path = bin_dir / java_exe
        javac_path = bin_dir / javac_exe

        # Debug opcional para ver por dónde busca (te ayuda ahora)
        try:
            self.output.emit(f"[DEBUG] runtimes base: {base_dir}")
            self.output.emit(f"[DEBUG] JAVA_HOME: {jdk_home}")
            self.output.emit(f"[DEBUG] java: {java_path} | javac: {javac_path}")
        except Exception:
            pass

        return {
            "JAVA_HOME": str(jdk_home) if jdk_home.exists() else None,
            "java": str(java_path) if java_path.exists() else None,
            "javac": str(javac_path) if javac_path.exists() else None,
        }

    def _make_env_with_embedded_java(self):
        """
        Crea un entorno para QProcess que antepone el JDK embebido al PATH
        y define JAVA_HOME (si existe).
        """
        env = QtCore.QProcessEnvironment.systemEnvironment()
        java_home = self._java_paths.get("JAVA_HOME")
        if java_home:
            env.insert("JAVA_HOME", java_home)
            bin_dir = str(Path(java_home) / "bin")
            sep = ";" if os.name == "nt" else ":"
            current_path = env.value("PATH", "")
            env.insert("PATH", bin_dir + (sep + current_path if current_path else ""))
        return env

    # ===============================
    # Compilación / Ejecución
    # ===============================
    def _compile(self, java_path: str):
        """Compila usando solo el JDK embebido; si no existe, error."""
        emb_javac = self._java_paths.get("javac")

        if not (emb_javac and Path(emb_javac).exists()):
            self.error.emit("No se encontró 'javac' en runtimes/<os>/jdk. No se usará el del sistema.")
            self.finished.emit(1)
            return

        self.started.emit("compile")

        self._proc = QtCore.QProcess(self)
        self._proc.setProgram(emb_javac)
        self._proc.setArguments(["-d", self._tmpdir, java_path])
        self._proc.setProcessEnvironment(self._make_env_with_embedded_java())
        self._wire_process(step="compile")
        self._proc.start()

    def _run(self):
        """Ejecuta usando solo el JDK embebido; si no existe, error."""
        emb_java = self._java_paths.get("java")

        if not (emb_java and Path(emb_java).exists()):
            self.error.emit("No se encontró 'java' en runtimes/<os>/jdk. No se usará el del sistema.")
            self.finished.emit(1)
            return

        self.started.emit("run")

        self._proc = QtCore.QProcess(self)
        self._proc.setProgram(emb_java)
        self._proc.setArguments(["-cp", self._tmpdir, self._class_name])
        self._proc.setProcessEnvironment(self._make_env_with_embedded_java())
        self._wire_process(step="run")
        self._proc.start()

    # ===============================
    # Señales QProcess
    # ===============================
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

    # ===============================
    # Limpieza
    # ===============================
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
