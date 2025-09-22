# -*- coding: utf-8 -*-
import os
import sys
import shutil
import re
import tempfile
from pathlib import Path
from PyQt5 import QtCore


class JavaBytecodeDisassembler(QtCore.QObject):
    """
    SOLO ASM REAL (sin simulaciones):
      Java -> (javac) -> .class
           -> (GraalVM native-image embebido) -> binario nativo
           -> (dumpbin/objdump/otool) -> ASM real (CPU)

    Requisitos embebidos:
      - JDK embebido (java/javac/javap NO es necesario para ASM, pero javac sí).
      - GraalVM native-image embebido (busca: runtimes/win/graavlm/..., runtimes/win/graalvm/..., etc.)
      - Desensamblador del SO:
          Windows: dumpbin (VS Build Tools) en PATH
          Linux:   objdump (binutils) en PATH
          macOS:   otool (Xcode CLT) en PATH
    """

    # Señales
    started  = QtCore.pyqtSignal(str)  # "compile", "native-image", "disasm"
    output   = QtCore.pyqtSignal(str)  # salida incremental
    result   = QtCore.pyqtSignal(str)  # ASM final
    finished = QtCore.pyqtSignal(int)  # 0 OK
    error    = QtCore.pyqtSignal(str)  # mensaje error

    def __init__(self, parent=None, show_headers: bool = False):
        super().__init__(parent)
        self._tmpdir = None
        self._class_name = None
        self._proc = None
        self._phase = None
        self._buf = []
        self._java_paths = self._locate_embedded_java()
        self._native_image_path = self._find_native_image()  # obligatorio
        self._show_headers = show_headers  # <<< NUEVO

    # ===============================
    # API
    # ===============================
    def disassemble(self, source_code: str):
        self._cleanup()
        if not source_code.strip():
            self._fail("No hay código para desensamblar.")
            return

        self._class_name = self._extract_public_class(source_code) or "Main"
        self._tmpdir = tempfile.mkdtemp(prefix="java_native_asm_")
        java_path = os.path.join(self._tmpdir, f"{self._class_name}.java")

        try:
            with open(java_path, "w", encoding="utf-8") as f:
                f.write(source_code)
        except Exception as e:
            self._fail(f"Error escribiendo archivo: {e}")
            return

        self._start_compile(java_path)

    def stop(self):
        if self._proc and self._proc.state() != QtCore.QProcess.NotRunning:
            self._proc.kill()

    # ===============================
    # Fases asíncronas
    # ===============================
    def _start_compile(self, java_path: str):
        javac = self._java_paths.get("javac")
        if not (javac and Path(javac).exists()):
            self._fail("No se encontró 'javac' embebido en runtimes. (Se requiere para compilar).")
            return

        self._phase = "compile"
        self.started.emit("compile")
        self._buf = []

        self._proc = QtCore.QProcess(self)
        self._hook_io(self._proc)
        self._proc.setWorkingDirectory(self._tmpdir)
        self._proc.start(javac, ["-g", "-d", self._tmpdir, java_path])

    def _start_native_image(self):
        exe_native = self._native_image_path
        if not exe_native or not Path(exe_native).exists():
            self._fail("No se encontró 'native-image' embebido. Revisa runtimes/win/graavlm o runtimes/win/graalvm.")
            return

        self._phase = "native-image"
        self.started.emit("native-image")
        self._buf = []

        base_args = [
            "--no-fallback",
            "-g",
            "-o", "program",
            "-cp", self._tmpdir,
            self._class_name,
        ]

        self._proc = QtCore.QProcess(self)
        self._hook_io(self._proc)
        self._proc.setProcessChannelMode(QtCore.QProcess.MergedChannels)
        self._proc.setWorkingDirectory(self._tmpdir)

        if os.name == "nt" and exe_native.lower().endswith(".cmd"):
            program = "cmd.exe"
            args = ["/c", exe_native] + base_args
        else:
            program = exe_native
            args = base_args

        self._proc.start(program, args)

    def _start_disasm(self):
        exe = os.path.join(self._tmpdir, "program.exe" if os.name == "nt" else "program")
        if not Path(exe).exists():
            self._fail("No se generó el binario nativo. native-image falló o cambió el nombre de salida.")
            return
        try:
            tool_name, argv = self._find_disassembler(exe)
        except Exception as e:
            # Resultado minimalista sin encabezados ruidosos
            texto = (
                f"; No se encontró desensamblador: {e}\n"
                "; Instala uno:\n"
                ";   Windows: dumpbin (VS Build Tools) o llvm-objdump\n"
                ";   Linux:   objdump (binutils)\n"
                ";   macOS:   otool (Xcode CLT)\n"
            )
            self.result.emit(texto)
            return

        self._phase = "disasm"
        self.started.emit("disasm")
        self._buf = []
        self._proc = QtCore.QProcess(self)
        self._hook_io(self._proc)
        self._proc.setProcessChannelMode(QtCore.QProcess.MergedChannels)
        self._proc.setWorkingDirectory(self._tmpdir)
        self._proc.start(argv[0], argv[1:])

    # ===============================
    # I/O de procesos
    # ===============================
    def _hook_io(self, proc: QtCore.QProcess):
        proc.readyReadStandardOutput.connect(self._on_stdout)
        proc.readyReadStandardError.connect(self._on_stderr)
        proc.finished.connect(self._on_finished)

    def _on_stdout(self):
        data = bytes(self._proc.readAllStandardOutput()).decode("utf-8", errors="ignore")
        if data:
            self._buf.append(data)
            self.output.emit(data)

    def _on_stderr(self):
        data = bytes(self._proc.readAllStandardError()).decode("utf-8", errors="ignore")
        if data:
            self._buf.append(data)
            self.output.emit(data)

    def _on_finished(self, exit_code, _status):
        text = "".join(self._buf)

        if self._phase == "compile":
            if exit_code != 0:
                self._fail(f"Error de compilación:\n{text}")
                return
            self._start_native_image()
            return

        if self._phase == "native-image":
            if exit_code != 0:
                self._fail(f"native-image falló:\n{text or '(sin salida)'}")
                return
            self._start_disasm()
            return

        if self._phase == "disasm":
            if exit_code != 0 and not text.strip():
                self._fail("Fallo al desensamblar: herramienta devolvió error sin salida.")
                return

            if self._show_headers:
                header = [
                    f"; Clase fuente: {self._class_name}",
                    f"; Herramienta: {'dumpbin' if os.name=='nt' else ('otool' if sys.platform=='darwin' else 'objdump')}",
                    "",
                ]
                payload = "\n".join(header) + text
            else:
                # Sin encabezados: solo la salida cruda del desensamblador
                payload = text

            self.result.emit(payload)
            self.finished.emit(0)
            return

    # ===============================
    # Descubrimiento de runtimes embebidos
    # ===============================
    def _find_base_with_runtimes(self) -> Path:
        meipass = getattr(sys, "_MEIPASS", None)
        if meipass:
            p = Path(meipass)
            if (p / "runtimes").exists():
                return p

        here = Path(__file__).resolve()
        for p in [here.parent, *here.parents]:
            if (p / "runtimes").exists():
                return p

        cwd = Path.cwd()
        if (cwd / "runtimes").exists():
            return cwd

        return here.parent

    def _locate_embedded_java(self):
        base_dir = self._find_base_with_runtimes()

        is_win = (os.name == "nt")
        is_mac = (sys.platform == "darwin")

        java_name = "java.exe" if is_win else "java"
        javac_name = "javac.exe" if is_win else "javac"
        javap_name = "javap.exe" if is_win else "javap"

        candidates = []
        if is_win:
            candidates = [
                base_dir / "runtimes" / "win" / "jdk" / "bin",
                base_dir / "runtimes" / "win" / "graalvm" / "bin",
                base_dir / "runtimes" / "win" / "graavlm" / "bin",
            ]
        elif is_mac:
            candidates = [
                base_dir / "runtimes" / "mac" / "jdk" / "Contents" / "Home" / "bin",
                base_dir / "runtimes" / "mac" / "graalvm" / "Contents" / "Home" / "bin",
            ]
        else:
            candidates = [
                base_dir / "runtimes" / "linux" / "jdk" / "bin",
                base_dir / "runtimes" / "linux" / "graalvm" / "bin",
            ]

        try:
            self.output.emit(f"[DEBUG] Buscando JDK embebido en: {base_dir}")
            for c in candidates:
                self.output.emit(f"[DEBUG] candidato bin: {c}")
        except Exception:
            pass

        for bindir in candidates:
            java_path = bindir / java_name
            javac_path = bindir / javac_name
            javap_path = bindir / javap_name
            if java_path.exists() and javac_path.exists():
                try:
                    self.output.emit(f"[DEBUG] Usando JDK embebido: {bindir.parent}")
                    self.output.emit(f"[DEBUG] java={java_path}  javac={javac_path}  javap={javap_path}")
                except Exception:
                    pass
                return {
                    "JAVA_HOME": str(bindir.parent),
                    "java": str(java_path),
                    "javac": str(javac_path),
                    "javap": str(javap_path) if javap_path.exists() else None,
                }

        java_on_path = shutil.which(java_name)
        javac_on_path = shutil.which(javac_name)
        javap_on_path = shutil.which(javap_name)

        if java_on_path and javac_on_path:
            try:
                self.output.emit("[DEBUG] No se halló JDK embebido; usando herramientas del PATH.")
                self.output.emit(f"[DEBUG] java={java_on_path}  javac={javac_on_path}  javap={javap_on_path}")
            except Exception:
                pass
            return {
                "JAVA_HOME": None,
                "java": java_on_path,
                "javac": javac_on_path,
                "javap": javap_on_path,
            }

        try:
            self.output.emit("[DEBUG] No se encontró JDK embebido ni herramientas en PATH.")
        except Exception:
            pass
        return {
            "JAVA_HOME": None,
            "java": None,
            "javac": None,
            "javap": None,
        }

    def _find_native_image(self) -> str:
        base = self._find_base_with_runtimes()
        is_win = (os.name == "nt")
        is_mac = (sys.platform == "darwin")

        names = ["native-image"]
        if is_win:
            names = ["native-image.cmd", "native-image.exe"]

        if is_win:
            cand_dirs = [
                base / "runtimes" / "win" / "graalvm" / "bin",
                base / "runtimes" / "win" / "graavlm" / "bin",
                base / "runtimes" / "win" / "jdk" / "bin",
            ]
        elif is_mac:
            cand_dirs = [
                base / "runtimes" / "mac" / "graalvm" / "Contents" / "Home" / "bin",
                base / "runtimes" / "mac" / "jdk" / "Contents" / "Home" / "bin",
            ]
        else:
            cand_dirs = [
                base / "runtimes" / "linux" / "graalvm" / "bin",
                base / "runtimes" / "linux" / "jdk" / "bin",
            ]

        try:
            self.output.emit(f"[DEBUG] Buscando native-image en base: {base}")
            for d in cand_dirs:
                self.output.emit(f"[DEBUG] candidato: {d}")
        except Exception:
            pass

        for d in cand_dirs:
            for nm in names:
                p = d / nm
                if p.exists():
                    try:
                        self.output.emit(f"[DEBUG] native-image encontrado: {p}")
                    except Exception:
                        pass
                    return str(p)

        from shutil import which
        for nm in names:
            w = which(nm)
            if w:
                try:
                    self.output.emit(f"[DEBUG] native-image en PATH: {w}")
                except Exception:
                    pass
                return w

        raise RuntimeError(
            "No se encontró 'native-image' embebido. Revisa runtimes/win/graavlm o runtimes/win/graalvm.")

    def _run_native_image(self, native_image_path: str, args: list, cwd: str, timeout: int = 600):
        import subprocess

        if os.name == "nt" and native_image_path.lower().endswith(".cmd"):
            argv = ["cmd.exe", "/c", native_image_path] + args
            p = subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=cwd)
        else:
            argv = [native_image_path] + args
            p = subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=cwd)

        out, err = p.communicate(timeout=timeout)
        return p.returncode, out.decode("utf-8", errors="ignore"), err.decode("utf-8", errors="ignore")

    def _find_disassembler(self, exe_path: str):
        base = self._find_base_with_runtimes()

        if os.name == "nt":
            embedded = [
                base / "runtimes" / "win" / "llvm" / "bin" / "llvm-objdump.exe",
                base / "runtimes" / "win" / "binutils" / "bin" / "objdump.exe",
                base / "runtimes" / "win" / "dumpbin" / "bin" / "dumpbin.exe",
            ]
            for e in embedded:
                if e.exists():
                    e_str = str(e)
                    if e.name.lower().startswith("dumpbin"):
                        return ("dumpbin", [e_str, "/DISASM", exe_path])
                    elif "objdump" in e.name.lower():
                        return (e.name, [e_str, "-d", "--no-show-raw-insn", exe_path])

            dumpbin = shutil.which("dumpbin")
            if dumpbin:
                return ("dumpbin", [dumpbin, "/DISASM", exe_path])
            llvm = shutil.which("llvm-objdump")
            if llvm:
                return ("llvm-objdump", [llvm, "-d", "--no-show-raw-insn", exe_path])
            objd = shutil.which("objdump")
            if objd:
                return ("objdump", [objd, "-d", "--no-show-raw-insn", exe_path])

            raise RuntimeError("dumpbin/llvm-objdump/objdump no disponible en el sistema.")

        elif sys.platform == "darwin":
            embedded = base / "runtimes" / "mac" / "llvm" / "bin" / "otool"
            if embedded.exists():
                return ("otool", [str(embedded), "-tV", exe_path])
            tool = shutil.which("otool")
            if tool:
                return ("otool", [tool, "-tV", exe_path])
            raise RuntimeError("Instala Xcode Command Line Tools: xcode-select --install")

        else:
            embedded = base / "runtimes" / "linux" / "binutils" / "bin" / "objdump"
            if embedded.exists():
                return ("objdump", [str(embedded), "-d", "--demangle", "--no-show-raw-insn", exe_path])
            tool = shutil.which("objdump")
            if tool:
                return ("objdump", [tool, "-d", "--demangle", "--no-show-raw-insn", exe_path])
            raise RuntimeError("Instala binutils para obtener 'objdump'.")

    # ===============================
    # Utilidades
    # ===============================
    def _extract_public_class(self, src: str):
        if not isinstance(src, str) or not src.strip():
            return None
        m = re.search(r'^\s*public\s+(?:\w+\s+)*class\s+([A-Za-z_]\w*)', src, re.MULTILINE)
        return m.group(1) if m else None

    def _fail(self, msg: str):
        self.error.emit(msg)

    def _cleanup(self):
        if self._proc and self._proc.state() != QtCore.QProcess.NotRunning:
            self._proc.kill()
        self._proc = None
        if self._tmpdir and os.path.isdir(self._tmpdir):
            try:
                shutil.rmtree(self._tmpdir, ignore_errors=True)
            except Exception:
                pass
        self._tmpdir = None
        self._class_name = None
        self._phase = None
        self._buf = []
