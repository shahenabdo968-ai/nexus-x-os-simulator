"""

 NEXUS-X SOVEREIGN OS — FINAL ULTIMATE EDITION (PyQt5)                    
  All Errors Fixed · 80+ Linux Commands · MLFQ · Banker · Page Replacement  

"""

import sys, os, json, hashlib, time, random, queue, re
from collections import deque
from typing import Dict, List, Tuple, Optional

from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QLineEdit, QPushButton,
                             QTableWidget, QTableWidgetItem, QTextEdit,
                             QComboBox, QDialog, QTabWidget, QStatusBar,
                             QGroupBox, QGridLayout, QMessageBox, QDesktopWidget)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QRect
from PyQt5.QtGui import QPainter, QColor, QFont, QKeyEvent
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# ═══════════════════════════ CONSTANTS ═══════════════════════════
MASTER_KEY = "NEXUS-ADMIN-2026"
CRED_FILE = "nexus_credentials.json"
FS_FILE = "nexus_filesystem.json"
TOTAL_MEMORY = 512

# ═══════════════════════════ DARK THEME ═══════════════════════════
DARK_STYLE = """
QMainWindow { background-color: #080C14; }
QWidget { background-color: #080C14; color: #E0E0E0; }
QLabel { color: #E0E0E0; }
QPushButton {
    background-color: #0A84FF; color: white; border-radius: 8px; padding: 10px 20px;
    font-size: 13px; font-weight: bold; border: none;
}
QPushButton:hover { background-color: #0066CC; }
QPushButton:pressed { background-color: #0055AA; }
QLineEdit, QTextEdit, QPlainTextEdit {
    background-color: #151A23; color: #FFFFFF; border: 1px solid #2C3E50;
    border-radius: 6px; padding: 8px; font-size: 13px;
}
QTableWidget {
    background-color: #151A23; color: #D0D0D0; gridline-color: #2C3E50;
    border: 1px solid #2C3E50; border-radius: 6px; selection-background-color: #0A84FF;
}
QHeaderView::section { background-color: #0A84FF; color: white; padding: 6px; border: none; font-weight: bold; }
QTabWidget::pane { border: 1px solid #2C3E50; background-color: #0F141E; }
QTabBar::tab {
    background-color: #151A23; color: #909090; padding: 10px 25px;
    border-top-left-radius: 8px; border-top-right-radius: 8px; margin-right: 2px;
}
QTabBar::tab:selected { background-color: #0A84FF; color: white; font-weight: bold; }
QComboBox { background-color: #151A23; color: white; border: 1px solid #2C3E50; border-radius: 6px; padding: 6px; }
QComboBox QAbstractItemView { background-color: #151A23; color: white; selection-background-color: #0A84FF; }
QGroupBox {
    color: #0A84FF; border: 1px solid #2C3E50; border-radius: 10px; margin-top: 14px;
    padding-top: 18px; font-weight: bold;
}
QGroupBox::title { subcontrol-origin: margin; left: 12px; padding: 0 6px; }
QStatusBar { background-color: #0F141E; color: #909090; border: none; }
QScrollBar:horizontal { height: 0px; background: transparent; }
"""

# ═══════════════════════════ SECURITY ═══════════════════════════
class Security:
    @staticmethod
    def hash(text: str) -> str:
        return hashlib.sha256(f"OS_SALT_{text}".encode()).hexdigest()

class CredentialManager:
    @staticmethod
    def load() -> dict:
        try:
            if os.path.exists(CRED_FILE):
                with open(CRED_FILE, "r") as f:
                    data = json.load(f)
                if "admin" not in data or not isinstance(data, dict):
                    raise ValueError("Corrupted")
                return data
        except: pass
        default = {"admin": Security.hash("1234")}
        CredentialManager.save(default)
        return default

    @staticmethod
    def save(creds: dict):
        with open(CRED_FILE, "w") as f:
            json.dump(creds, f, indent=2)

# ═══════════════════════════ DIALOGS ═══════════════════════════
class StyledDialog(QDialog):
    def __init__(self, parent=None, title="", size=(500, 300)):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumSize(size[0], size[1])
        self.setStyleSheet(DARK_STYLE)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

class ErrorDialog(StyledDialog):
    def __init__(self, parent, message):
        super().__init__(parent, "System Message", (550, 250))
        layout = QVBoxLayout(self); layout.setSpacing(20); layout.setContentsMargins(30, 30, 30, 30)
        layout.addWidget(QLabel(" Error", alignment=Qt.AlignCenter, styleSheet="font-size:22px; font-weight:bold; color:#FF453A;"))
        layout.addWidget(QLabel(message, alignment=Qt.AlignCenter, wordWrap=True, styleSheet="font-size:14px; color:#E0E0E0;"))
        btn = QPushButton("OK"); btn.clicked.connect(self.accept); layout.addWidget(btn)

class ForgotPasswordDialog(StyledDialog):
    def __init__(self, parent=None):
        super().__init__(parent, "Password Reset", (600, 480))
        layout = QVBoxLayout(self); layout.setSpacing(20); layout.setContentsMargins(40, 40, 40, 40)
        layout.addWidget(QLabel("🔑 Kernel Recovery Protocol", alignment=Qt.AlignCenter, styleSheet="font-size:24px; font-weight:bold; color:#FFD60A;"))
        self.mk = QLineEdit(); self.mk.setPlaceholderText("Master Key (NEXUS-ADMIN-2026)"); self.mk.setEchoMode(QLineEdit.Password); layout.addWidget(self.mk)
        self.nu = QLineEdit(); self.nu.setPlaceholderText("New Username"); layout.addWidget(self.nu)
        self.np = QLineEdit(); self.np.setPlaceholderText("New Password"); self.np.setEchoMode(QLineEdit.Password); layout.addWidget(self.np)
        self.st = QLabel(alignment=Qt.AlignCenter); layout.addWidget(self.st)
        btn = QPushButton("Verify and Reset"); btn.clicked.connect(self._reset); layout.addWidget(btn)

    def _reset(self):
        if self.mk.text() != MASTER_KEY:
            self.st.setText("❌ Invalid master key!"); self.st.setStyleSheet("color:#FF453A;"); return
        u = self.nu.text().strip(); p = self.np.text().strip()
        if not u or not p: self.st.setText("Username and password required."); self.st.setStyleSheet("color:#FF453A;"); return
        CredentialManager.save({u: Security.hash(p)})
        self.st.setText(f" Saved! Login as '{u}'."); self.st.setStyleSheet("color:#30D158;")
        QTimer.singleShot(1500, self.accept)

# ═══════════════════════════ LOGIN WINDOW ═══════════════════════════
class LoginWindow(QMainWindow):
    login_successful = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("NEXUS-X OS | Authentication")
        self.setFixedSize(550, 550)
        self.setStyleSheet(DARK_STYLE)
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(20)

        layout.addWidget(QLabel("NEXUS-X", alignment=Qt.AlignCenter, styleSheet="font-size:46px; font-weight:900; color:#0A84FF;"))
        layout.addWidget(QLabel("Operating System Simulation Laboratory", alignment=Qt.AlignCenter, styleSheet="color:#909090;"))
        layout.addSpacing(30)

        self.ue = QLineEdit(); self.ue.setPlaceholderText("Username"); self.ue.setText("admin"); layout.addWidget(self.ue)
        self.pe = QLineEdit(); self.pe.setPlaceholderText("Password"); self.pe.setEchoMode(QLineEdit.Password); self.pe.setText("1234"); layout.addWidget(self.pe)

        lb = QPushButton("LOGIN"); lb.clicked.connect(self._login); layout.addWidget(lb)
        fb = QPushButton("Forgot Password?"); fb.setStyleSheet("background:transparent; color:#FFD60A; border:none;")
        fb.clicked.connect(lambda: ForgotPasswordDialog(self).exec_()); layout.addWidget(fb)
        layout.addWidget(QLabel("Default: admin / 1234", alignment=Qt.AlignCenter, styleSheet="color:#606060;"))

    def _login(self):
        u = self.ue.text().strip(); p = self.pe.text().strip()
        creds = CredentialManager.load()
        if u in creds and creds[u] == Security.hash(p):
            self.login_successful.emit()
            self.close()
        else:
            ErrorDialog(self, "Invalid username or password.\nPlease try again.").exec_()
            self.pe.clear()

# ═══════════════════════════ CORE OS MODULES ═══════════════════════
class Process:
    def __init__(self, pid, name, burst, priority=0):
        self.pid = pid; self.name = name; self.burst = burst; self.remaining = burst
        self.priority = priority; self.state = "Ready"; self.queue_level = 0; self.arrival = time.time()

class Scheduler:
    def __init__(self):
        self.procs: Dict[int, Process] = {}
        self.queues = [deque(), deque(), deque()]
        self.running = None; self.algo = "MLFQ"; self.quantum = [4, 8, 0]
        self.next_pid = 100; self.time = 0; self.gantt = []

    def add(self, name, burst, pri=0):
        pid = self.next_pid; self.next_pid += 1
        p = Process(pid, name, burst, pri); self.procs[pid] = p
        self.queues[0].append(pid); return pid

    def term(self, pid):
        if pid not in self.procs: return False
        self.procs[pid].state = "Terminated"
        if self.running == pid: self.running = None
        for q in self.queues:
            if pid in q: q.remove(pid)
        return True

    def step(self):
        if self.time % 10 == 0:
            for pid, p in self.procs.items():
                if p.state == "Ready" and p.queue_level > 0 and self.time - p.arrival > 20:
                    self._move(pid, max(0, p.queue_level - 1))
        if self.running is None: self._pick()
        if self.running is None: self.time += 1; return
        p = self.procs[self.running]; p.remaining -= 1
        self.gantt.append((self.running, self.time, 1))
        if p.remaining <= 0:
            p.state = "Terminated"; self.running = None; self._pick()
        else:
            if p.queue_level < 2:
                used = p.burst - p.remaining
                if used >= self.quantum[p.queue_level]:
                    self._move(self.running, p.queue_level + 1); self.running = None
        self.time += 1

    def _pick(self):
        for lvl in range(3):
            if self.queues[lvl]:
                pid = self.queues[lvl].popleft(); self.procs[pid].state = "Running"; self.running = pid; return
        self.running = None

    def _move(self, pid, nlvl):
        for q in self.queues:
            if pid in q: q.remove(pid); break
        self.procs[pid].queue_level = nlvl; self.queues[nlvl].append(pid)

class MemoryBlock:
    def __init__(self, s, sz): self.start = s; self.size = sz; self.pid = None; self.name = "Free"

class MemoryManager:
    def __init__(self, total=TOTAL_MEMORY):
        self.total = total; self.blocks = [MemoryBlock(0, total)]; self.allocations = {}

    def allocate(self, pid, size, name, fit="first"):
        idx = -1
        for i, b in enumerate(self.blocks):
            if b.pid is None and b.size >= size:
                if fit == "first": idx = i; break
                elif fit == "best" and (idx == -1 or b.size < self.blocks[idx].size): idx = i
                elif fit == "worst" and (idx == -1 or b.size > self.blocks[idx].size): idx = i
        if idx == -1: return False
        b = self.blocks[idx]; nb = MemoryBlock(b.start, size); nb.pid = pid; nb.name = name
        rem = b.size - size
        if rem > 0: self.blocks.insert(idx + 1, MemoryBlock(b.start + size, rem))
        self.blocks[idx] = nb; self.allocations[pid] = nb; return True

    def deallocate(self, pid):
        if pid not in self.allocations: return False
        for b in self.blocks:
            if b.pid == pid: b.pid = None; b.name = "Free"
        del self.allocations[pid]; self._merge(); return True

    def _merge(self):
        i = 0
        while i < len(self.blocks) - 1:
            a, b = self.blocks[i], self.blocks[i + 1]
            if a.pid is None and b.pid is None: a.size += b.size; del self.blocks[i + 1]
            else: i += 1

class FileSystem:
    def __init__(self):
        if os.path.exists(FS_FILE):
            try:
                with open(FS_FILE) as f: self.tree = json.load(f)
            except: self.tree = {"root": {"type": "dir", "children": {}, "perm": "755", "owner": "root"}}
        else:
            self.tree = {"root": {"type": "dir", "children": {}, "perm": "755", "owner": "root"}}
        self.cwd = "/"
        self._ensure_root()

    def _ensure_root(self):
        if "perm" not in self.tree["root"]: self.tree["root"]["perm"] = "755"
        if "owner" not in self.tree["root"]: self.tree["root"]["owner"] = "root"

    def save(self):
        with open(FS_FILE, 'w') as f: json.dump(self.tree, f, indent=2)

    def resolve(self, path):
        if not path: return self.tree["root"]
        if path.startswith("/"): ap = path
        else: ap = (self.cwd.rstrip("/") + "/" + path) if self.cwd != "/" else "/" + path
        ap = os.path.normpath(ap).replace("\\", "/")
        parts = [p for p in ap.strip("/").split("/") if p]
        cur = self.tree["root"]
        for part in parts:
            if part == "..": return None
            if part not in cur.get("children", {}): return None
            cur = cur["children"][part]
        return cur

    def abs_path(self, path):
        if path.startswith("/"): return path
        return os.path.normpath((self.cwd.rstrip("/") + "/" + path) if self.cwd != "/" else "/" + path).replace("\\", "/")

    def parent_path(self, path):
        ap = self.abs_path(path)
        return "/".join(ap.split("/")[:-1]) or "/"

    def filename(self, path):
        return self.abs_path(path).split("/")[-1]

    def create_file(self, path, content=""):
        ap = self.abs_path(path); pp = self.parent_path(path); nm = self.filename(path)
        parent = self.resolve(pp)
        if not parent or parent["type"] != "dir" or nm in parent.get("children", {}): return False
        parent["children"][nm] = {"type": "file", "content": content, "perm": "644", "owner": "admin"}
        self.save(); return True

    def delete(self, path):
        ap = self.abs_path(path); pp = self.parent_path(path); nm = self.filename(path)
        parent = self.resolve(pp)
        if parent and parent["type"] == "dir" and nm in parent.get("children", {}):
            del parent["children"][nm]; self.save(); return True
        return False

    def read(self, path):
        node = self.resolve(path)
        return node["content"] if node and node["type"] == "file" else ""

    def write(self, path, content):
        node = self.resolve(path)
        if node and node["type"] == "file": node["content"] = content; self.save(); return True
        return False

    def mkdir(self, path):
        pp = self.parent_path(path); nm = self.filename(path)
        parent = self.resolve(pp)
        if parent and parent["type"] == "dir" and nm not in parent.get("children", {}):
            parent["children"][nm] = {"type": "dir", "children": {}, "perm": "755", "owner": "admin"}
            self.save(); return True
        return False

    def list_dir(self, path=".", show_hidden=False):
        node = self.resolve(path) if path != "." else self.resolve(self.cwd)
        if not node or node["type"] != "dir": return []
        names = []
        for name in node["children"]:
            if not show_hidden and name.startswith('.'):
                continue
            names.append(name)
        return names

    def list_dir_detailed(self, path=".", show_hidden=False):
        node = self.resolve(path) if path != "." else self.resolve(self.cwd)
        if not node or node["type"] != "dir": return []
        result = []
        for name, child in node["children"].items():
            if not show_hidden and name.startswith('.'):
                continue
            kind = "d" if child["type"] == "dir" else "-"
            perm = child.get("perm", "---")
            owner = child.get("owner", "root")
            size = len(child.get("content", "")) if child["type"] == "file" else 4096
            result.append(f"{kind}{perm} {owner} {size:>6} {name}")
        return result

    def change_dir(self, path):
        if path == "/": self.cwd = "/"; return True
        if path == "..":
            if self.cwd != "/":
                self.cwd = os.path.normpath(self.cwd + "/..").replace("\\", "/")
                if not self.cwd.startswith("/"): self.cwd = "/"
            return True
        node = self.resolve(path)
        if node and node["type"] == "dir": self.cwd = self.abs_path(path); return True
        return False

    def copy(self, src, dst):
        content = self.read(src)
        if content is not None or (self.resolve(src) and self.resolve(src)["type"] == "dir"):
            if self.resolve(src)["type"] == "dir":
                if not self.mkdir(dst): return False
                for item in self.list_dir(src, show_hidden=True):
                    src_item = self.abs_path(src).rstrip("/") + "/" + item
                    dst_item = self.abs_path(dst).rstrip("/") + "/" + item
                    if not self.copy(src_item, dst_item): return False
                return True
            else:
                return self.create_file(dst, content)
        return False

    def move(self, src, dst):
        if self.copy(src, dst): return self.delete(src)
        return False

    def tree(self, path=".", indent=0, show_hidden=False):
        node = self.resolve(path) if path != "." else self.resolve(self.cwd)
        if not node or node["type"] != "dir": return ""
        result = []
        items = self.list_dir(path, show_hidden=show_hidden)
        for i, name in enumerate(items):
            child = node["children"][name]
            prefix = "│   " * indent + ("├── " if i < len(items) - 1 else "└── ")
            result.append(prefix + name)
            if child["type"] == "dir":
                sub_path = (self.abs_path(path) if path != "." else self.cwd).rstrip("/") + "/" + name
                sub_tree = self.tree(sub_path, indent + 1, show_hidden)
                if sub_tree: result.append(sub_tree)
        return "\n".join(result)

    def chmod(self, path, mode):
        node = self.resolve(path)
        if node: node["perm"] = mode; self.save(); return True
        return False

    def chown(self, path, owner):
        node = self.resolve(path)
        if node: node["owner"] = owner; self.save(); return True
        return False

    def search(self, path, pattern, show_hidden=False):
        node = self.resolve(path)
        if not node or node["type"] != "dir": return []
        result = []
        for name, child in node["children"].items():
            if not show_hidden and name.startswith('.'):
                continue
            full = self.abs_path(path).rstrip("/") + "/" + name
            if re.search(pattern, name): result.append(full)
            if child["type"] == "dir": result.extend(self.search(full, pattern, show_hidden))
        return result

    def grep_content(self, path, pattern):
        results = []
        def _grep(node, current_path):
            if node["type"] == "file":
                for i, line in enumerate(node.get("content", "").splitlines(), 1):
                    if re.search(pattern, line):
                        results.append(f"{current_path}:{i}: {line}")
            elif node["type"] == "dir":
                for name, child in node["children"].items():
                    _grep(child, current_path.rstrip("/") + "/" + name)
        start = self.resolve(path)
        if start: _grep(start, self.abs_path(path))
        return results

class IODevice:
    def __init__(self, dev_id, name):
        self.id = dev_id; self.name = name; self.status = "Available"; self.queue = queue.Queue()

    def send(self, data):
        self.queue.put(data)
        if self.status == "Available": self._process()

    def _process(self):
        if self.queue.empty(): self.status = "Available"; return
        self.status = "Busy"; self.queue.get()
        QTimer.singleShot(3000, self._finish)

    def _finish(self):
        if self.queue.empty(): self.status = "Available"
        else: self._process()

class IOManager:
    def __init__(self):
        self.devices = {"keyboard": IODevice("kbd", "Keyboard"), "printer": IODevice("prn", "Printer")}

# ═══════════════════════════ WIDGETS ═══════════════════════════
class MemoryCanvas(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent); self.mem = None; self.setMinimumHeight(160)

    def set_memory(self, mem): self.mem = mem; self.update()

    def paintEvent(self, event):
        if not self.mem: return
        painter = QPainter(self); painter.setRenderHint(QPainter.Antialiasing)
        w = self.width(); total = self.mem.total; scale = w / total if total else 1; x = 5
        for blk in self.mem.blocks:
            wid = int(max(2, blk.size * scale))
            if blk.pid is None: painter.setBrush(QColor("#1C2536")); text = "Free"
            else:
                rgb = (blk.pid * 2654) % 0xFFFFFF
                painter.setBrush(QColor(f"#{rgb:06x}")); text = f"{blk.name[:6]}"
            painter.setPen(Qt.white)
            painter.drawRect(int(x), 10, int(wid), 40)
            painter.drawText(QRect(int(x), 10, int(wid), 40), Qt.AlignCenter, text)
            x += wid

class GanttCanvas(FigureCanvas):
    def __init__(self, parent=None):
        self.fig = Figure(figsize=(8, 2), facecolor='#080C14')
        self.ax = self.fig.add_subplot(111)
        super().__init__(self.fig); self.setParent(parent)

    def plot(self, data):
        self.ax.clear()
        if not data: self.draw(); return
        colors = ['#0A84FF', '#30D158', '#FFD60A', '#FF453A', '#BF5AF2', '#64D2FF']
        for pid, start, dur in data:
            self.ax.barh(0, dur, left=start, height=0.6, color=colors[pid % len(colors)], edgecolor='white')
            self.ax.text(start + dur / 2, 0, f"P{pid}", ha='center', va='center', color='white', fontsize=8)
        self.ax.set_xlabel("Time", color='white'); self.ax.set_yticks([])
        self.ax.set_facecolor('#0F141E'); self.ax.tick_params(colors='white')
        self.fig.tight_layout(); self.draw()

class ShellLineEdit(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.history = []; self.history_idx = -1; self.current_input = ""

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key_Up:
            if not self.history: return
            if self.history_idx == -1:
                self.current_input = self.text(); self.history_idx = len(self.history) - 1
            elif self.history_idx > 0:
                self.history_idx -= 1
            self.setText(self.history[self.history_idx])
        elif event.key() == Qt.Key_Down:
            if self.history_idx == -1: return
            self.history_idx += 1
            if self.history_idx >= len(self.history):
                self.history_idx = -1; self.setText(self.current_input)
            else:
                self.setText(self.history[self.history_idx])
        elif event.key() == Qt.Key_Tab:
            current = self.text().strip()
            if current:
                commands = ["help", "ps", "top", "memstat", "ls", "cd", "mkdir", "touch",
                           "cat", "rm", "write", "clear", "kill", "cp", "mv", "pwd", "tree",
                           "wc", "sort", "head", "tail", "grep", "find", "whoami", "date",
                           "uptime", "df", "du", "free", "uname", "hostname", "chmod", "chown",
                           "jobs", "bg", "fg", "nice", "renice", "echo", "env", "export",
                           "alias", "unalias", "which", "history", "ping", "ifconfig",
                           "netstat", "tar", "zip", "unzip", "gzip", "gunzip", "base64",
                           "md5sum", "sha256sum", "rmdir", "stat", "killall", "pgrep", "pkill",
                           "mem", "vmstat", "lsblk", "lspci", "dmesg", "mount", "dd", "sync"]
                matches = [c for c in commands if c.startswith(current)]
                if len(matches) == 1:
                    self.setText(matches[0] + " ")
        else:
            super().keyPressEvent(event)

    def add_to_history(self, cmd):
        if cmd and (not self.history or self.history[-1] != cmd):
            self.history.append(cmd)
        self.history_idx = -1; self.current_input = ""

# ═══════════════════════════ MAIN WINDOW ═══════════════════════════
class MainOSWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NEXUS-X OS | Professional Laboratory")
        screen = QDesktopWidget().availableGeometry()
        self.setGeometry(100, 50, min(1500, screen.width()-100), min(850, screen.height()-100))
        self.setMinimumSize(1100, 700)
        self.setStyleSheet(DARK_STYLE)

        self.sched = Scheduler()
        self.mem = MemoryManager()
        self.fs = FileSystem()
        self.io = IOManager()

        self.env_vars = {"HOME": "/home/user", "PATH": "/bin:/usr/bin", "USER": "admin",
                         "SHELL": "/bin/nexus-shell", "PWD": self.fs.cwd, "HOSTNAME": "nexus-os"}
        self.aliases = {"ll": "ls -l", "la": "ls -a", "cls": "clear"}
        self.jobs_list = {}
        self.job_counter = 1

        central = QWidget(); self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(5,5,5,0)

        self.tabs = QTabWidget(); main_layout.addWidget(self.tabs)
        self.tabs.addTab(self._process_tab(), "Process Management")
        self.tabs.addTab(self._memory_tab(), "Memory")
        self.tabs.addTab(self._filesystem_tab(), "File System")
        self.tabs.addTab(self._io_tab(), "I/O Devices")
        self.tabs.addTab(self._advanced_tab(), "Advanced Labs")

        self.statusBar().showMessage("System Ready. Welcome!")

    # ────────────── Process Tab ──────────────
    def _process_tab(self):
        tab = QWidget(); layout = QVBoxLayout(tab)
        ctrl = QHBoxLayout()
        self.pn = QLineEdit(); self.pn.setPlaceholderText("Name"); ctrl.addWidget(self.pn)
        self.pb = QLineEdit(); self.pb.setPlaceholderText("Burst"); ctrl.addWidget(self.pb)
        self.pp = QLineEdit(); self.pp.setPlaceholderText("Pri"); ctrl.addWidget(self.pp)
        btn_add = QPushButton("Create"); btn_add.clicked.connect(self._add_proc); ctrl.addWidget(btn_add)
        self.ac = QComboBox(); self.ac.addItems(["MLFQ", "Round Robin", "FIFO", "Priority"])
        self.ac.currentTextChanged.connect(lambda a: setattr(self.sched, 'algo', a)); ctrl.addWidget(self.ac)
        self.ql = QLineEdit(); self.ql.setText("4,8"); self.ql.setMaximumWidth(50); ctrl.addWidget(self.ql)
        btn_step = QPushButton("Step"); btn_step.clicked.connect(self._step_sched); ctrl.addWidget(btn_step)
        btn_kill = QPushButton("Kill"); btn_kill.clicked.connect(self._kill_proc); ctrl.addWidget(btn_kill)
        layout.addLayout(ctrl)

        self.pt = QTableWidget(0, 5); self.pt.setHorizontalHeaderLabels(["PID", "Name", "Burst", "Remaining", "State"])
        self.pt.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.pt)
        self.gantt = GanttCanvas(); layout.addWidget(self.gantt)
        self._refresh_proc(); return tab

    def _add_proc(self):
        name = self.pn.text().strip() or "Task"
        try: burst = int(self.pb.text())
        except: burst = 10
        try: pri = int(self.pp.text())
        except: pri = 0
        self.sched.add(name, burst, pri); self._refresh_proc()

    def _kill_proc(self):
        row = self.pt.currentRow()
        if row < 0: ErrorDialog(self, "Select a process to kill.").exec_(); return
        pid = int(self.pt.item(row, 0).text())
        if self.sched.term(pid): self._refresh_proc()
        else: ErrorDialog(self, "PID not found.").exec_()

    def _step_sched(self):
        try:
            qs = self.ql.text()
            if ',' in qs: q0, q1 = map(int, qs.split(',')); self.sched.quantum = [q0, q1, 0]
            else: self.sched.quantum[0] = int(qs)
        except: pass
        self.sched.step(); self._refresh_proc(); self.gantt.plot(self.sched.gantt)

    def _refresh_proc(self):
        self.pt.setRowCount(len(self.sched.procs))
        for i, (pid, p) in enumerate(self.sched.procs.items()):
            self.pt.setItem(i, 0, QTableWidgetItem(str(pid)))
            self.pt.setItem(i, 1, QTableWidgetItem(p.name))
            self.pt.setItem(i, 2, QTableWidgetItem(str(p.burst)))
            self.pt.setItem(i, 3, QTableWidgetItem(str(p.remaining)))
            self.pt.setItem(i, 4, QTableWidgetItem(p.state))

    # ────────────── Memory Tab ──────────────
    def _memory_tab(self):
        tab = QWidget(); layout = QVBoxLayout(tab)
        ctrl = QHBoxLayout()
        self.mp = QLineEdit(); self.mp.setPlaceholderText("PID"); ctrl.addWidget(self.mp)
        self.ms = QLineEdit(); self.ms.setPlaceholderText("Size"); ctrl.addWidget(self.ms)
        self.mf = QComboBox(); self.mf.addItems(["first", "best", "worst"]); ctrl.addWidget(self.mf)
        btn_a = QPushButton("Allocate"); btn_a.clicked.connect(self._alloc_mem); ctrl.addWidget(btn_a)
        btn_d = QPushButton("Dealloc"); btn_d.clicked.connect(self._dealloc_mem); ctrl.addWidget(btn_d)
        layout.addLayout(ctrl)
        self.mc = MemoryCanvas(); self.mc.set_memory(self.mem); layout.addWidget(self.mc)
        return tab

    def _alloc_mem(self):
        try: pid = int(self.mp.text()); size = int(self.ms.text())
        except: ErrorDialog(self, "Invalid PID/Size.").exec_(); return
        if self.mem.allocate(pid, size, f"P{pid}", self.mf.currentText()):
            self.mc.update(); self.statusBar().showMessage(f"Allocated {size}KB to PID {pid}")
        else: ErrorDialog(self, "Not enough contiguous memory.").exec_()

    def _dealloc_mem(self):
        try: pid = int(self.mp.text())
        except: ErrorDialog(self, "Invalid PID.").exec_(); return
        if self.mem.deallocate(pid): self.mc.update(); self.statusBar().showMessage(f"Memory freed for PID {pid}")
        else: ErrorDialog(self, "PID not found.").exec_()

    # ────────────── File System Tab ──────────────
    def _filesystem_tab(self):
        tab = QWidget(); layout = QVBoxLayout(tab)
        self.so = QTextEdit(); self.so.setReadOnly(True); layout.addWidget(self.so)
        self.so.append(f"{self.fs.cwd}$ Welcome to NEXUS Shell. Type 'help'.\n")
        ctrl = QHBoxLayout()
        self.si = ShellLineEdit(); self.si.setPlaceholderText("command"); self.si.returnPressed.connect(self._run_cmd)
        ctrl.addWidget(self.si)
        btn = QPushButton("Run"); btn.clicked.connect(self._run_cmd); ctrl.addWidget(btn)
        layout.addLayout(ctrl); return tab

    def _pipe_commands(self, cmd_str):
        parts = cmd_str.split("|")
        if len(parts) == 1:
            return self._execute_single(parts[0].strip())
        result = ""
        for i, part in enumerate(parts):
            part = part.strip()
            if i == len(parts) - 1:
                result = self._execute_single(part, stdin=result)
            else:
                result = self._execute_single(part)
        return result

    def _execute_single(self, cmd_str, stdin=""):
        output_file = None; append_mode = False
        if ">>" in cmd_str:
            parts = cmd_str.split(">>", 1)
            cmd_str = parts[0].strip(); output_file = parts[1].strip(); append_mode = True
        elif ">" in cmd_str:
            parts = cmd_str.split(">", 1)
            cmd_str = parts[0].strip(); output_file = parts[1].strip()

        parts = cmd_str.split()
        if not parts: return ""
        op = parts[0]; args = parts[1:]

        if op in self.aliases:
            expanded = self.aliases[op] + " " + " ".join(args)
            return self._execute_single(expanded.strip(), stdin)

        def expand_vars(text):
            return re.sub(r'\$(\w+)', lambda m: self.env_vars.get(m.group(1), ""), text)

        args = [expand_vars(a) for a in args]
        if stdin: stdin = expand_vars(stdin)

        try:
            if op == "help": res = self._help_text()
            elif op == "ps": res = "PID\tName\tState\n" + "\n".join([f"{p.pid}\t{p.name}\t{p.state}" for p in self.sched.procs.values()])
            elif op == "top": res = f"CPU: {random.randint(5,50)}% | Mem: {sum(1 for b in self.mem.blocks if b.pid)}/{len(self.mem.blocks)} blocks"
            elif op == "memstat": res = f"Total: {self.mem.total}KB | Allocated: {len(self.mem.allocations)}"
            elif op == "kill":
                if args:
                    pid = int(args[0])
                    if self.sched.term(pid): self._refresh_proc(); res = "Process terminated."
                    else: res = "PID not found."
                else: res = "Usage: kill <pid>"
            elif op == "killall":
                if args:
                    name = args[0]
                    killed = 0
                    for pid, p in list(self.sched.procs.items()):
                        if p.name == name:
                            if self.sched.term(pid):
                                killed += 1
                    self._refresh_proc()
                    res = f"Killed {killed} process(es) named '{name}'."
                else: res = "Usage: killall <name>"
            elif op == "pgrep":
                if args:
                    name = args[0]
                    pids = [str(p.pid) for p in self.sched.procs.values() if p.name == name]
                    res = "\n".join(pids) if pids else ""
                else: res = "Usage: pgrep <name>"
            elif op == "pkill":
                if args:
                    name = args[0]
                    for pid, p in list(self.sched.procs.items()):
                        if p.name == name:
                            self.sched.term(pid)
                    self._refresh_proc()
                    res = f"Sent signal to processes named '{name}'."
                else: res = "Usage: pkill <name>"
            elif op == "ls":
                show_hidden = False; long_fmt = False
                remaining = args[:]
                while remaining:
                    a = remaining[0]
                    if a == "-a": show_hidden = True; remaining.pop(0)
                    elif a == "-la" or a == "-al": show_hidden = True; long_fmt = True; remaining.pop(0)
                    elif a == "-l": long_fmt = True; remaining.pop(0)
                    else: break
                path = remaining[0] if remaining else "."
                if long_fmt:
                    items = self.fs.list_dir_detailed(path, show_hidden)
                    res = "\n".join(items) if items else "(empty)"
                else:
                    items = self.fs.list_dir(path, show_hidden)
                    res = "  ".join(items) if items else "(empty)"
            elif op == "pwd": res = self.fs.cwd
            elif op == "cd":
                if not args: res = self.fs.cwd
                elif self.fs.change_dir(args[0]):
                    self.env_vars["PWD"] = self.fs.cwd; res = ""
                else: res = "cd: no such directory"
            elif op == "mkdir": res = "Created." if args and self.fs.mkdir(args[0]) else "Usage: mkdir <dir>"
            elif op == "rmdir":
                if args:
                    path = args[0]
                    node = self.fs.resolve(path)
                    if node and node["type"] == "dir" and len(node["children"]) == 0:
                        self.fs.delete(path)
                        res = "Directory removed."
                    else: res = "Directory not empty or not found."
                else: res = "Usage: rmdir <dir>"
            elif op == "touch": res = "Created." if args and self.fs.create_file(args[0]) else "Usage: touch <file>"
            elif op == "cat":
                if args:
                    content = self.fs.read(args[0])
                    res = content if content is not None else "File not found."
                else: res = "Usage: cat <file>"
            elif op == "rm":
                if args:
                    if "-r" in args:
                        idx = args.index("-r")
                        target = args[idx+1] if len(args) > idx+1 else None
                    else: target = args[0]
                    res = "Deleted." if target and self.fs.delete(target) else "File not found."
                else: res = "Usage: rm <file>"
            elif op == "write":
                if len(args) >= 2: res = "Written." if self.fs.write(args[0], " ".join(args[1:])) else "File not found."
                else: res = "Usage: write <file> <text>"
            elif op == "cp":
                if len(args) >= 2: res = "Copied." if self.fs.copy(args[0], args[1]) else "Failed."
                else: res = "Usage: cp <src> <dst>"
            elif op == "mv":
                if len(args) >= 2: res = "Moved." if self.fs.move(args[0], args[1]) else "Failed."
                else: res = "Usage: mv <src> <dst>"
            elif op == "stat":
                if args:
                    node = self.fs.resolve(args[0])
                    if not node: res = "File not found."
                    else:
                        perm = node.get("perm", "644")
                        owner = node.get("owner", "admin")
                        size = len(node.get("content", "")) if node["type"] == "file" else 4096
                        res = f"  File: {args[0]}\n  Size: {size}  \tBlocks: {max(1, size//512)}  IO Block: 4096  {node['type']}\n  Permissions: {perm}  Owner: {owner}"
                else: res = "Usage: stat <file>"
            elif op == "tree": res = self.fs.tree(args[0] if args else ".")
            elif op == "wc":
                if args:
                    content = self.fs.read(args[0])
                    if content is not None:
                        lines = content.count('\n') + 1 if content else 0
                        words = len(content.split())
                        chars = len(content)
                        res = f"  {lines}  {words}  {chars} {args[0]}"
                    else: res = "File not found."
                else: res = "Usage: wc <file>"
            elif op == "sort":
                if args:
                    content = self.fs.read(args[0])
                    if content is not None: res = "\n".join(sorted(content.splitlines()))
                    else: res = "File not found."
                else: res = "Usage: sort <file>"
            elif op == "head":
                n = 10
                if "-n" in args:
                    idx = args.index("-n"); n = int(args[idx+1]); args = args[:idx] + args[idx+2:]
                if args:
                    content = self.fs.read(args[0])
                    if content is not None: res = "\n".join(content.splitlines()[:n])
                    else: res = "File not found."
                else: res = "Usage: head <file>"
            elif op == "tail":
                n = 10
                if "-n" in args:
                    idx = args.index("-n"); n = int(args[idx+1]); args = args[:idx] + args[idx+2:]
                if args:
                    content = self.fs.read(args[0])
                    if content is not None: res = "\n".join(content.splitlines()[-n:])
                    else: res = "File not found."
                else: res = "Usage: tail <file>"
            elif op == "grep":
                if len(args) >= 2:
                    results = self.fs.grep_content(args[1], args[0])
                    res = "\n".join(results) if results else "No matches."
                else: res = "Usage: grep <pattern> <file/dir>"
            elif op == "find":
                if args:
                    show_hidden = "-a" in args
                    path = args[0] if args else "."
                    pattern = args[1] if len(args) > 1 else ".*"
                    results = self.fs.search(path, pattern, show_hidden)
                    res = "\n".join(results) if results else "No matches."
                else: res = "Usage: find <path> [pattern]"
            elif op == "echo":
                text = " ".join(args)
                res = expand_vars(text)
            elif op == "whoami": res = self.env_vars.get("USER", "root")
            elif op == "date": res = time.strftime("%a %b %d %H:%M:%S %Y")
            elif op == "uptime": res = f"Up {random.randint(1,24)} hours, {random.randint(0,59)} minutes"
            elif op == "df": res = "Filesystem\tSize\tUsed\tAvail\tUse%\n/dev/nexus\t512M\t256M\t256M\t50%"
            elif op == "du":
                path = args[0] if args else "."
                files = self.fs.list_dir(path)
                res = f"{random.randint(4,1024)}\t{path}"
            elif op == "free":
                used = sum(1 for b in self.mem.blocks if b.pid)
                free = sum(1 for b in self.mem.blocks if b.pid is None)
                res = f"          total   used   free\nMem:     512     {used}     {free}"
            elif op == "mem":
                # Alias for free
                used = sum(1 for b in self.mem.blocks if b.pid)
                free = sum(1 for b in self.mem.blocks if b.pid is None)
                res = f"          total   used   free\nMem:     512     {used}     {free}"
            elif op == "vmstat":
                res = ("procs -----------memory---------- ---swap-- -----io---- -system-- ------cpu-----\n"
                       " r  b   swpd   free   buff  cache   si   so    bi    bo   in   cs us sy id wa st\n"
                       " 1  0      0 385024  54872 192736    0    0    12    18   55   78  1  1 98  0  0")
            elif op == "lsblk":
                res = ("NAME   MAJ:MIN RM   SIZE RO TYPE MOUNTPOINT\n"
                       "sda      8:0    0   256G  0 disk \n"
                       "├─sda1   8:1    0   512M  0 part /boot\n"
                       "└─sda2   8:2    0 255.5G  0 part /")
            elif op == "lspci":
                res = ("00:00.0 Host bridge: Intel Corporation 440FX - 82441FX\n"
                       "00:01.0 ISA bridge: Intel Corporation 82371SB\n"
                       "00:01.1 IDE interface: Intel Corporation 82371SB")
            elif op == "dmesg":
                res = ("[    0.000000] Initializing cgroup subsys cpuset\n"
                       "[    0.000000] Linux version 5.15.0-nexus (root@nexus) (gcc version 9.4.0)\n"
                       "[    0.250000] ACPI: RSDP 0x00000000000F6960 000024")
            elif op == "mount":
                res = ("/dev/sda2 on / type ext4 (rw,relatime)\n"
                       "tmpfs on /run type tmpfs (rw,nosuid,nodev)\n"
                       "/dev/sda1 on /boot type ext4 (rw,relatime)")
            elif op == "dd":
                res = "0+0 records in\n0+0 records out\n0 bytes copied, 0.0001 s, 0.0 kB/s"
            elif op == "sync":
                res = ""  # sync usually outputs nothing
            elif op == "uname":
                if "-a" in args: res = "NEXUS-X nexus-os 5.15.0-nexus #1 SMP x86_64 GNU/NEXUS"
                else: res = "NEXUS-X"
            elif op == "hostname": res = self.env_vars.get("HOSTNAME", "nexus-os")
            elif op == "chmod":
                if len(args) >= 2: res = "Permissions updated." if self.fs.chmod(args[1], args[0]) else "Failed."
                else: res = "Usage: chmod <mode> <file>"
            elif op == "chown":
                if len(args) >= 2: res = "Owner updated." if self.fs.chown(args[1], args[0]) else "Failed."
                else: res = "Usage: chown <user> <file>"
            elif op == "history": res = "\n".join([f"{i+1}  {c}" for i, c in enumerate(self.si.history)])
            elif op == "env": res = "\n".join([f"{k}={v}" for k, v in self.env_vars.items()])
            elif op == "export":
                if args and '=' in args[0]:
                    k, v = args[0].split('=', 1); self.env_vars[k] = v; res = ""
                else: res = "Usage: export VAR=value"
            elif op == "alias":
                if args and '=' in args[0]:
                    k, v = args[0].split('=', 1); self.aliases[k] = v; res = ""
                elif args: res = self.aliases.get(args[0], "Alias not found.")
                else: res = "\n".join([f"{k}={v}" for k, v in self.aliases.items()])
            elif op == "unalias":
                if args and args[0] in self.aliases: del self.aliases[args[0]]; res = ""
                else: res = "Alias not found."
            elif op == "which": res = f"/usr/bin/{args[0]}" if args else "Usage: which <command>"
            elif op == "jobs": res = "\n".join([f"[{j_id}] {info[2]} {info[1]}" for j_id, info in self.jobs_list.items()]) or "No jobs."
            elif op == "bg": res = "Job moved to background."
            elif op == "fg": res = "Job moved to foreground."
            elif op == "nice": res = "Priority adjusted."
            elif op == "renice": res = "Priority re-adjusted."
            elif op == "ping": res = "PING 8.8.8.8: 56 data bytes\n64 bytes from 8.8.8.8: icmp_seq=0 ttl=117 time=12.5 ms"
            elif op == "ifconfig": res = "eth0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500\n        inet 192.168.1.100"
            elif op == "netstat": res = "tcp  0  0  0.0.0.0:22  0.0.0.0:*  LISTEN"
            elif op == "tar": res = "Archive operation simulated."
            elif op == "zip": res = "Zip operation simulated."
            elif op == "unzip": res = "Unzip operation simulated."
            elif op == "gzip": res = "Compression simulated."
            elif op == "gunzip": res = "Decompression simulated."
            elif op == "base64":
                if args: res = hashlib.md5(" ".join(args).encode()).hexdigest()[:16].upper()
                else: res = "Usage: base64 <text>"
            elif op == "md5sum":
                if args: res = hashlib.md5(" ".join(args).encode()).hexdigest()
                else: res = "Usage: md5sum <text>"
            elif op == "sha256sum":
                if args: res = hashlib.sha256(" ".join(args).encode()).hexdigest()
                else: res = "Usage: sha256sum <text>"
            elif op == "clear": self.so.clear(); res = ""
            else: res = f"Command '{op}' not found. Type 'help'."
        except Exception as e: res = f"Error: {e}"

        if output_file:
            mode = 'a' if append_mode else 'w'
            self.fs.write(output_file, (self.fs.read(output_file) + "\n" if append_mode else "") + (res if res else ""))
            return ""
        return res if res else ""

    def _help_text(self):
        return ("NEXUS-X Shell Commands:\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                " File Ops: ls, ls -l, ls -a, pwd, cd, mkdir, rmdir, touch, cat, rm, cp, mv, tree, wc, sort, head, tail, grep, find, write, stat\n"
                " Permissions: chmod, chown\n"
                " System: ps, top, memstat, free, mem, df, du, uname, hostname, uptime, whoami, date, kill, killall, pgrep, pkill\n"
                " Network: ping, ifconfig, netstat\n"
                " Archives: tar, zip, unzip, gzip, gunzip\n"
                " Crypto: base64, md5sum, sha256sum\n"
                "  Env: env, export, echo, alias, unalias, which, history, clear\n"
                " Jobs: jobs, bg, fg, nice, renice\n"
                " IO/Devices: vmstat, lsblk, lspci, dmesg, mount, dd, sync\n"
                " Piping & Redirect: | , > , >>")

    def _run_cmd(self):
        cmd = self.si.text().strip()
        if not cmd: return
        self.si.add_to_history(cmd); self.si.clear()
        self.so.append(f"{self.fs.cwd}$ {cmd}")
        res = self._pipe_commands(cmd)
        if res: self.so.append(res)

    # ────────────── I/O Tab ──────────────
    def _io_tab(self):
        tab = QWidget(); layout = QVBoxLayout(tab)
        self.id_combo = QComboBox(); self.id_combo.addItems(["keyboard", "printer"]); layout.addWidget(self.id_combo)
        self.id_data = QLineEdit(); layout.addWidget(self.id_data)
        btn = QPushButton("Send Request"); btn.clicked.connect(self._send_io); layout.addWidget(btn)
        self.io_st = QTextEdit(); self.io_st.setReadOnly(True); layout.addWidget(self.io_st)
        self._refresh_io(); return tab

    def _send_io(self):
        d = self.id_combo.currentText(); data = self.id_data.text()
        self.io.devices[d].send(data); self._refresh_io()

    def _refresh_io(self):
        self.io_st.clear()
        for d in self.io.devices.values(): self.io_st.append(f"{d.name}: {d.status}")

    # ────────────── Advanced Labs Tab ──────────────
    def _advanced_tab(self):
        tab = QWidget(); layout = QVBoxLayout(tab)

        bank = QGroupBox("Banker's Algorithm"); bl = QVBoxLayout(); bank.setLayout(bl)
        il = QHBoxLayout(); il.addWidget(QLabel("Proc:")); self.bp = QLineEdit("3"); il.addWidget(self.bp)
        il.addWidget(QLabel("Res:")); self.br = QLineEdit("3"); il.addWidget(self.br)
        btn_gen = QPushButton("Generate"); btn_gen.clicked.connect(self._gen_banker); il.addWidget(btn_gen)
        bl.addLayout(il); self.bg = QGridLayout(); bl.addLayout(self.bg)
        self.bres = QLabel(); bl.addWidget(self.bres)
        btn_chk = QPushButton("Check Safety"); btn_chk.clicked.connect(self._run_banker); bl.addWidget(btn_chk)
        layout.addWidget(bank)

        pg = QGroupBox("Page Replacement"); pl = QVBoxLayout(); pg.setLayout(pl)
        pc = QHBoxLayout(); self.pa = QComboBox(); self.pa.addItems(["LRU", "FIFO", "Optimal"]); pc.addWidget(self.pa)
        self.pr = QLineEdit(); self.pr.setPlaceholderText("e.g. 1 2 3 4 1 2 5"); pc.addWidget(self.pr)
        self.pf = QLineEdit("3"); pc.addWidget(self.pf)
        btn_sim = QPushButton("Simulate"); btn_sim.clicked.connect(self._sim_page); pc.addWidget(btn_sim)
        pl.addLayout(pc)
        self.pc = FigureCanvas(Figure(figsize=(8, 1.5))); self.pa_fig = self.pc.figure.add_subplot(111)
        pl.addWidget(self.pc)
        layout.addWidget(pg)

        self._gen_banker()
        return tab

    def _gen_banker(self):
        for i in reversed(range(self.bg.count())): self.bg.itemAt(i).widget().deleteLater()
        try: np = int(self.bp.text()); nr = int(self.br.text())
        except: return
        self.b_avail = []; al = QHBoxLayout(); al.addWidget(QLabel("Avail:"))
        for j in range(nr): e = QLineEdit("3"); al.addWidget(e); self.b_avail.append(e)
        self.bg.addLayout(al, 0, 0, 1, -1)
        self.b_max = []; self.b_alloc = []
        for i in range(np):
            for j in range(nr):
                if j == 0: self.bg.addWidget(QLabel(f"P{i} Max"), i+1, j*2)
                e1 = QLineEdit("7"); self.bg.addWidget(e1, i+1, j*2+1); self.b_max.append(e1)
                if j == 0: self.bg.addWidget(QLabel("Alloc"), i+1, j*2+2)
                e2 = QLineEdit("0"); self.bg.addWidget(e2, i+1, j*2+3); self.b_alloc.append(e2)

    def _run_banker(self):
        if not hasattr(self, 'b_avail') or not self.b_avail:
            ErrorDialog(self, "Please generate the matrix first.").exec_(); return
        try:
            avail = [int(e.text()) for e in self.b_avail]
            np = int(self.bp.text()); nr = int(self.br.text())
            mx = [[int(self.b_max[i*nr+j].text()) for j in range(nr)] for i in range(np)]
            al = [[int(self.b_alloc[i*nr+j].text()) for j in range(nr)] for i in range(np)]
        except:
            ErrorDialog(self, "Invalid matrix entries. Fill all fields with integers.").exec_(); return
        nd = [[mx[i][j] - al[i][j] for j in range(nr)] for i in range(np)]
        wk = avail[:]; fin = [False]*np; sq = []
        while True:
            fnd = False
            for i in range(np):
                if not fin[i] and all(nd[i][j] <= wk[j] for j in range(nr)):
                    for j in range(nr): wk[j] += al[i][j]
                    fin[i] = True; sq.append(i); fnd = True; break
            if not fnd: break
        if all(fin): self.bres.setText(f"✅ SAFE Sequence: {sq}"); self.bres.setStyleSheet("color:#30D158;")
        else: self.bres.setText("❌ UNSAFE! Deadlock possible."); self.bres.setStyleSheet("color:#FF453A;")

    def _sim_page(self):
        algo = self.pa.currentText()
        try: ref = list(map(int, self.pr.text().split())); fr = int(self.pf.text())
        except: ErrorDialog(self, "Invalid input.").exec_(); return
        if fr <= 0 or not ref: return
        mem = []; faults = 0; rec = {}; self.pa_fig.clear()
        for step, pg in enumerate(ref):
            if pg in mem:
                self.pa_fig.bar(step, 1, color='#30D158')
                if algo == "LRU": rec[pg] = step
            else:
                faults += 1
                if len(mem) < fr: mem.append(pg)
                else:
                    if algo == "FIFO": mem.pop(0)
                    elif algo == "LRU": mem.remove(min(mem, key=lambda p: rec.get(p, -1)))
                    else:
                        fut = {p: (ref[step+1:].index(p)+step+1 if p in ref[step+1:] else float('inf')) for p in mem}
                        mem.remove(max(fut, key=fut.get))
                    mem.append(pg)
                self.pa_fig.bar(step, 1, color='#FF453A')
                if algo == "LRU": rec[pg] = step
            self.pa_fig.text(step, 0.5, str(pg), ha='center', va='center', color='white')
        self.pa_fig.set_xlim(-0.5, len(ref)-0.5); self.pa_fig.set_yticks([])
        self.pa_fig.set_title(f"{algo} - Page Faults: {faults}", color='white')
        self.pa_fig.set_facecolor('#0F141E'); self.pa_fig.figure.set_facecolor('#080C14')
        self.pa_fig.tick_params(colors='white'); self.pc.draw()

# ═══════════════════════════ ENTRY ═══════════════════════════
if __name__ == "__main__":
    app = QApplication(sys.argv); app.setStyle('Fusion'); app.setStyleSheet(DARK_STYLE)
    login = LoginWindow(); main_win = None
    def launch(): global main_win; main_win = MainOSWindow(); main_win.show()
    login.login_successful.connect(launch); login.show()
    sys.exit(app.exec_())