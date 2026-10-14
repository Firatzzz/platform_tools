import sys
import os
import subprocess
import threading
import json
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTextEdit, QLineEdit, QTabWidget, QFrame,
    QFileDialog, QScrollArea, QGridLayout, QSpacerItem, QSizePolicy,
    QProgressBar, QComboBox, QGroupBox, QSplitter, QListWidget, QListWidgetItem,
    QMessageBox, QCheckBox, QSpinBox, QDialog, QDialogButtonBox
)
from PyQt6.QtCore import (
    Qt, QThread, pyqtSignal, QTimer, QPropertyAnimation,
    QEasingCurve, QRect, QSize
)
from PyQt6.QtGui import (
    QFont, QColor, QPalette, QIcon, QPixmap, QPainter,
    QLinearGradient, QBrush, QPen, QTextCursor, QRadialGradient
)

# ─── CONSTANTS ───────────────────────────────────────────────────────────────

APP_NAME    = "ADB Platform Tools"
APP_VERSION = "1.0.0"
APP_AUTHOR  = "Platform Tools GUI"

# Locate platform-tools folder next to this script
BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
PT_DIR      = os.path.join(BASE_DIR, "platform-tools")
ADB_PATH    = os.path.join(PT_DIR, "adb.exe")
FASTBOOT_PATH = os.path.join(PT_DIR, "fastboot.exe")

# ─── COLOUR PALETTE ──────────────────────────────────────────────────────────

COLORS = {
    "bg_dark":      "#0D1117",
    "bg_medium":    "#161B22",
    "bg_light":     "#21262D",
    "bg_card":      "#1C2128",
    "accent":       "#00E676",
    "accent2":      "#00BCD4",
    "accent_hover": "#69F0AE",
    "danger":       "#FF5252",
    "warning":      "#FFB300",
    "text":         "#E6EDF3",
    "text_dim":     "#8B949E",
    "border":       "#30363D",
    "success":      "#00E676",
}

# ─── STYLESHEET ──────────────────────────────────────────────────────────────

STYLESHEET = f"""
QMainWindow, QWidget {{
    background-color: {COLORS['bg_dark']};
    color: {COLORS['text']};
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 13px;
}}

QTabWidget::pane {{
    border: 1px solid {COLORS['border']};
    background-color: {COLORS['bg_medium']};
    border-radius: 8px;
}}

QTabBar::tab {{
    background-color: {COLORS['bg_light']};
    color: {COLORS['text_dim']};
    padding: 10px 20px;
    margin-right: 2px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    font-weight: 600;
    font-size: 12px;
    min-width: 100px;
}}

QTabBar::tab:selected {{
    background-color: {COLORS['bg_medium']};
    color: {COLORS['accent']};
    border-bottom: 2px solid {COLORS['accent']};
}}

QTabBar::tab:hover {{
    background-color: {COLORS['bg_card']};
    color: {COLORS['text']};
}}

QPushButton {{
    background-color: {COLORS['bg_light']};
    color: {COLORS['text']};
    border: 1px solid {COLORS['border']};
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: 600;
    font-size: 12px;
    min-height: 32px;
}}

QPushButton:hover {{
    background-color: {COLORS['accent']};
    color: {COLORS['bg_dark']};
    border-color: {COLORS['accent']};
}}

QPushButton:pressed {{
    background-color: {COLORS['accent_hover']};
}}

QPushButton:disabled {{
    background-color: {COLORS['bg_light']};
    color: {COLORS['text_dim']};
    border-color: {COLORS['border']};
}}

QPushButton#danger_btn {{
    border-color: {COLORS['danger']};
    color: {COLORS['danger']};
}}
QPushButton#danger_btn:hover {{
    background-color: {COLORS['danger']};
    color: white;
}}

QPushButton#accent_btn {{
    background-color: {COLORS['accent']};
    color: {COLORS['bg_dark']};
    border-color: {COLORS['accent']};
    font-weight: 700;
}}
QPushButton#accent_btn:hover {{
    background-color: {COLORS['accent_hover']};
}}

QLineEdit, QComboBox, QSpinBox {{
    background-color: {COLORS['bg_light']};
    color: {COLORS['text']};
    border: 1px solid {COLORS['border']};
    border-radius: 6px;
    padding: 8px 12px;
    font-size: 12px;
    min-height: 32px;
}}

QLineEdit:focus, QComboBox:focus, QSpinBox:focus {{
    border-color: {COLORS['accent']};
}}

QComboBox::drop-down {{
    border: none;
    padding-right: 8px;
}}

QComboBox::down-arrow {{
    width: 12px;
    height: 12px;
}}

QComboBox QAbstractItemView {{
    background-color: {COLORS['bg_light']};
    color: {COLORS['text']};
    border: 1px solid {COLORS['border']};
    selection-background-color: {COLORS['accent']};
    selection-color: {COLORS['bg_dark']};
}}

QTextEdit {{
    background-color: {COLORS['bg_dark']};
    color: #A8FF78;
    border: 1px solid {COLORS['border']};
    border-radius: 8px;
    padding: 12px;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 12px;
    line-height: 1.5;
}}

QGroupBox {{
    border: 1px solid {COLORS['border']};
    border-radius: 8px;
    margin-top: 12px;
    padding-top: 8px;
    font-weight: 700;
    font-size: 12px;
    color: {COLORS['accent2']};
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 8px;
    left: 12px;
}}

QLabel {{
    color: {COLORS['text']};
    font-size: 12px;
}}

QLabel#title_label {{
    font-size: 22px;
    font-weight: 700;
    color: {COLORS['accent']};
}}

QLabel#subtitle_label {{
    font-size: 12px;
    color: {COLORS['text_dim']};
}}

QLabel#section_label {{
    font-size: 13px;
    font-weight: 700;
    color: {COLORS['accent2']};
}}

QLabel#status_connected {{
    color: {COLORS['success']};
    font-weight: 700;
}}

QLabel#status_disconnected {{
    color: {COLORS['danger']};
    font-weight: 700;
}}

QFrame#card_frame {{
    background-color: {COLORS['bg_card']};
    border: 1px solid {COLORS['border']};
    border-radius: 10px;
    padding: 8px;
}}

QFrame#header_frame {{
    background-color: {COLORS['bg_medium']};
    border-bottom: 1px solid {COLORS['border']};
    border-radius: 0px;
    padding: 4px;
}}

QProgressBar {{
    background-color: {COLORS['bg_light']};
    border: 1px solid {COLORS['border']};
    border-radius: 6px;
    height: 10px;
    text-align: center;
    color: {COLORS['text']};
}}

QProgressBar::chunk {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 {COLORS['accent']}, stop:1 {COLORS['accent2']});
    border-radius: 6px;
}}

QScrollBar:vertical {{
    background-color: {COLORS['bg_light']};
    width: 8px;
    border-radius: 4px;
}}
QScrollBar::handle:vertical {{
    background-color: {COLORS['border']};
    border-radius: 4px;
    min-height: 30px;
}}
QScrollBar::handle:vertical:hover {{
    background-color: {COLORS['accent']};
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}

QListWidget {{
    background-color: {COLORS['bg_dark']};
    color: {COLORS['text']};
    border: 1px solid {COLORS['border']};
    border-radius: 8px;
    padding: 4px;
    font-family: 'Consolas', monospace;
    font-size: 12px;
}}
QListWidget::item {{
    padding: 6px 8px;
    border-bottom: 1px solid {COLORS['border']};
}}
QListWidget::item:selected {{
    background-color: {COLORS['accent']};
    color: {COLORS['bg_dark']};
    border-radius: 4px;
}}
QListWidget::item:hover {{
    background-color: {COLORS['bg_light']};
}}

QCheckBox {{
    color: {COLORS['text']};
    spacing: 8px;
}}
QCheckBox::indicator {{
    width: 16px;
    height: 16px;
    border: 1px solid {COLORS['border']};
    border-radius: 3px;
    background-color: {COLORS['bg_light']};
}}
QCheckBox::indicator:checked {{
    background-color: {COLORS['accent']};
    border-color: {COLORS['accent']};
}}

QSplitter::handle {{
    background-color: {COLORS['border']};
    width: 2px;
}}

QMessageBox {{
    background-color: {COLORS['bg_medium']};
    color: {COLORS['text']};
}}
"""

# ─── WORKER THREAD ────────────────────────────────────────────────────────────

class CommandWorker(QThread):
    output_signal  = pyqtSignal(str)
    finished_signal = pyqtSignal(int)

    def __init__(self, cmd: list, cwd: str = None):
        super().__init__()
        self.cmd = cmd
        self.cwd = cwd or PT_DIR
        self._running = True

    def run(self):
        try:
            proc = subprocess.Popen(
                self.cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                cwd=self.cwd,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            for line in proc.stdout:
                if not self._running:
                    proc.kill()
                    break
                self.output_signal.emit(line.rstrip())
            proc.wait()
            self.finished_signal.emit(proc.returncode)
        except Exception as e:
            self.output_signal.emit(f"[ERROR] {e}")
            self.finished_signal.emit(-1)

    def stop(self):
        self._running = False


# ─── DEVICE STATUS BAR ───────────────────────────────────────────────────────

class DeviceStatusBar(QFrame):
    refresh_requested = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setObjectName("card_frame")
        self.setMaximumHeight(70)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 8, 16, 8)
        layout.setSpacing(16)

        icon_lbl = QLabel("📱")
        icon_lbl.setFont(QFont("Segoe UI Emoji", 20))
        layout.addWidget(icon_lbl)

        info_col = QVBoxLayout()
        info_col.setSpacing(2)
        self.device_label = QLabel("No device connected")
        self.device_label.setObjectName("status_disconnected")
        self.device_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self.serial_label = QLabel("Serial: —")
        self.serial_label.setObjectName("subtitle_label")
        info_col.addWidget(self.device_label)
        info_col.addWidget(self.serial_label)
        layout.addLayout(info_col)

        layout.addStretch()

        self.status_dot = QLabel("●")
        self.status_dot.setFont(QFont("Segoe UI", 18))
        self.status_dot.setStyleSheet(f"color: {COLORS['danger']};")
        layout.addWidget(self.status_dot)

        refresh_btn = QPushButton("⟳  Refresh")
        refresh_btn.setFixedWidth(110)
        refresh_btn.clicked.connect(self.refresh_requested.emit)
        layout.addWidget(refresh_btn)

    def set_device(self, serial: str, state: str):
        if serial and state in ("device", "recovery", "sideload", "fastboot"):
            self.device_label.setText(f"Device Connected  [{state.upper()}]")
            self.device_label.setObjectName("status_connected")
            self.serial_label.setText(f"Serial: {serial}")
            self.status_dot.setStyleSheet(f"color: {COLORS['success']};")
        else:
            self.device_label.setText("No device connected")
            self.device_label.setObjectName("status_disconnected")
            self.serial_label.setText("Serial: —")
            self.status_dot.setStyleSheet(f"color: {COLORS['danger']};")

        self.device_label.style().unpolish(self.device_label)
        self.device_label.style().polish(self.device_label)


# ─── OUTPUT CONSOLE ───────────────────────────────────────────────────────────

class OutputConsole(QFrame):
    def __init__(self, title="Output Console"):
        super().__init__()
        self.setObjectName("card_frame")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 12)
        layout.setSpacing(8)

        header = QHBoxLayout()
        lbl = QLabel(f"⚡  {title}")
        lbl.setObjectName("section_label")
        header.addWidget(lbl)
        header.addStretch()

        clear_btn = QPushButton("🗑  Clear")
        clear_btn.setFixedWidth(90)
        clear_btn.clicked.connect(self.clear)
        header.addWidget(clear_btn)
        layout.addLayout(header)

        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setMinimumHeight(180)
        layout.addWidget(self.text_edit)

    def append(self, text: str):
        ts = datetime.now().strftime("%H:%M:%S")
        self.text_edit.append(f'<span style="color:{COLORS["text_dim"]};">[{ts}]</span> {text}')
        cursor = self.text_edit.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.text_edit.setTextCursor(cursor)

    def append_success(self, text: str):
        ts = datetime.now().strftime("%H:%M:%S")
        self.text_edit.append(
            f'<span style="color:{COLORS["text_dim"]};">[{ts}]</span> '
            f'<span style="color:{COLORS["success"]};">{text}</span>'
        )

    def append_error(self, text: str):
        ts = datetime.now().strftime("%H:%M:%S")
        self.text_edit.append(
            f'<span style="color:{COLORS["text_dim"]};">[{ts}]</span> '
            f'<span style="color:{COLORS["danger"]};">{text}</span>'
        )

    def clear(self):
        self.text_edit.clear()


# ─── TAB: DEVICE INFO ────────────────────────────────────────────────────────

class DeviceInfoTab(QWidget):
    def __init__(self, console):
        super().__init__()
        self.console = console
        self.worker  = None
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(16, 16, 16, 16)

        info_group = QGroupBox("📋  Device Properties")
        info_grid  = QGridLayout(info_group)
        info_grid.setSpacing(10)

        self.info_labels = {}
        props = [
            ("Model",       "ro.product.model"),
            ("Brand",       "ro.product.brand"),
            ("Android",     "ro.build.version.release"),
            ("SDK",         "ro.build.version.sdk"),
            ("Build",       "ro.build.id"),
            ("Fingerprint", "ro.build.fingerprint"),
            ("Serial",      "ro.serialno"),
            ("IMEI",        "gsm.imei"),
        ]
        for i, (name, prop) in enumerate(props):
            lbl = QLabel(f"{name}:")
            lbl.setStyleSheet(f"color:{COLORS['text_dim']}; font-weight:600;")
            lbl.setFixedWidth(100)
            val = QLabel("—")
            val.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            val.setWordWrap(True)
            info_grid.addWidget(lbl, i, 0)
            info_grid.addWidget(val, i, 1)
            self.info_labels[prop] = val

        layout.addWidget(info_group)

        detail_group = QGroupBox("🔋  Live Status")
        detail_grid  = QGridLayout(detail_group)
        detail_grid.setSpacing(10)

        self.battery_bar = QProgressBar()
        self.battery_bar.setRange(0, 100)
        self.battery_bar.setValue(0)

        detail_grid.addWidget(QLabel("Battery Level:"), 0, 0)
        detail_grid.addWidget(self.battery_bar, 0, 1)

        self.screen_label = QLabel("—")
        detail_grid.addWidget(QLabel("Screen State:"), 1, 0)
        detail_grid.addWidget(self.screen_label, 1, 1)

        layout.addWidget(detail_group)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        fetch_btn = QPushButton("🔍  Fetch Device Info")
        fetch_btn.setObjectName("accent_btn")
        fetch_btn.clicked.connect(self.fetch_info)
        btn_row.addWidget(fetch_btn)

        reboot_btn = QPushButton("↩  Reboot Normal")
        reboot_btn.clicked.connect(lambda: self._adb(["reboot"]))
        btn_row.addWidget(reboot_btn)

        recovery_btn = QPushButton("🛠  Reboot Recovery")
        recovery_btn.clicked.connect(lambda: self._adb(["reboot", "recovery"]))
        btn_row.addWidget(recovery_btn)

        bootloader_btn = QPushButton("⚡  Reboot Bootloader")
        bootloader_btn.clicked.connect(lambda: self._adb(["reboot", "bootloader"]))
        btn_row.addWidget(bootloader_btn)

        layout.addLayout(btn_row)
        layout.addStretch()

    def _adb(self, args):
        cmd = [ADB_PATH] + args
        self.console.append(f"$ {' '.join(cmd)}")
        self.worker = CommandWorker(cmd)
        self.worker.output_signal.connect(self.console.append)
        self.worker.finished_signal.connect(lambda rc: self.console.append_success("Done.") if rc == 0 else self.console.append_error(f"Exit code {rc}"))
        self.worker.start()

    def fetch_info(self):
        self.console.append("Fetching device properties…")
        for prop, lbl in self.info_labels.items():
            lbl.setText("…")

        worker = CommandWorker([ADB_PATH, "shell", "getprop"])
        worker.output_signal.connect(self._parse_getprop)
        worker.finished_signal.connect(lambda rc: (
            self.console.append_success("Properties loaded.") if rc == 0
            else self.console.append_error("Failed to get properties.")
        ))
        worker.start()
        self._prop_worker = worker

        bat_worker = CommandWorker([ADB_PATH, "shell", "dumpsys", "battery"])
        bat_worker.output_signal.connect(self._parse_battery)
        bat_worker.start()
        self._bat_worker = bat_worker

    def _parse_getprop(self, line: str):
        for prop, lbl in self.info_labels.items():
            if f"[{prop}]" in line:
                val = line.split("]:")[-1].strip().strip("[").strip("]")
                lbl.setText(val or "—")

    def _parse_battery(self, line: str):
        line = line.strip()
        if "level:" in line:
            try:
                val = int(line.split(":")[-1].strip())
                self.battery_bar.setValue(val)
                if val <= 20:
                    self.battery_bar.setStyleSheet("QProgressBar::chunk { background: #FF5252; }")
                elif val <= 50:
                    self.battery_bar.setStyleSheet("QProgressBar::chunk { background: #FFB300; }")
                else:
                    self.battery_bar.setStyleSheet("")
            except ValueError:
                pass
        if "screen on" in line.lower():
            self.screen_label.setText("🟢 On")
        elif "screen off" in line.lower():
            self.screen_label.setText("⚫ Off")


# ─── TAB: FILE MANAGER ───────────────────────────────────────────────────────

class FileManagerTab(QWidget):
    def __init__(self, console):
        super().__init__()
        self.console = console
        self.worker  = None
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)

        push_group = QGroupBox("⬆  Push File to Device")
        push_layout = QGridLayout(push_group)
        push_layout.setSpacing(10)

        push_layout.addWidget(QLabel("Local File:"), 0, 0)
        self.push_src = QLineEdit()
        self.push_src.setPlaceholderText("Select or type local file path…")
        push_layout.addWidget(self.push_src, 0, 1)
        browse_push = QPushButton("Browse")
        browse_push.setFixedWidth(90)
        browse_push.clicked.connect(self._browse_push_src)
        push_layout.addWidget(browse_push, 0, 2)

        push_layout.addWidget(QLabel("Device Path:"), 1, 0)
        self.push_dst = QLineEdit("/sdcard/")
        push_layout.addWidget(self.push_dst, 1, 1)

        push_btn = QPushButton("⬆  Push to Device")
        push_btn.setObjectName("accent_btn")
        push_btn.clicked.connect(self._push_file)
        push_layout.addWidget(push_btn, 1, 2)
        layout.addWidget(push_group)

        pull_group = QGroupBox("⬇  Pull File from Device")
        pull_layout = QGridLayout(pull_group)
        pull_layout.setSpacing(10)

        pull_layout.addWidget(QLabel("Device Path:"), 0, 0)
        self.pull_src = QLineEdit("/sdcard/")
        pull_layout.addWidget(self.pull_src, 0, 1)

        pull_layout.addWidget(QLabel("Save To:"), 1, 0)
        self.pull_dst = QLineEdit()
        self.pull_dst.setPlaceholderText("Select destination folder…")
        pull_layout.addWidget(self.pull_dst, 1, 1)
        browse_pull = QPushButton("Browse")
        browse_pull.setFixedWidth(90)
        browse_pull.clicked.connect(self._browse_pull_dst)
        pull_layout.addWidget(browse_pull, 0, 2)

        pull_btn = QPushButton("⬇  Pull from Device")
        pull_btn.setObjectName("accent_btn")
        pull_btn.clicked.connect(self._pull_file)
        pull_layout.addWidget(pull_btn, 1, 2)
        layout.addWidget(pull_group)

        browser_group = QGroupBox("📂  Device File Browser")
        browser_layout = QVBoxLayout(browser_group)

        path_row = QHBoxLayout()
        self.browse_path = QLineEdit("/sdcard/")
        path_row.addWidget(self.browse_path)
        list_btn = QPushButton("List Files")
        list_btn.setFixedWidth(100)
        list_btn.clicked.connect(self._list_files)
        path_row.addWidget(list_btn)
        browser_layout.addLayout(path_row)

        self.file_list = QListWidget()
        self.file_list.setMinimumHeight(120)
        browser_layout.addWidget(self.file_list)
        layout.addWidget(browser_group)
        layout.addStretch()

    def _browse_push_src(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select File")
        if path:
            self.push_src.setText(path)

    def _browse_pull_dst(self):
        path = QFileDialog.getExistingDirectory(self, "Select Destination Folder")
        if path:
            self.pull_dst.setText(path)

    def _push_file(self):
        src = self.push_src.text().strip()
        dst = self.push_dst.text().strip()
        if not src:
            self.console.append_error("Please select a local file to push.")
            return
        cmd = [ADB_PATH, "push", src, dst]
        self.console.append(f"$ {' '.join(cmd)}")
        self.worker = CommandWorker(cmd)
        self.worker.output_signal.connect(self.console.append)
        self.worker.finished_signal.connect(lambda rc: self.console.append_success("Push complete!") if rc == 0 else self.console.append_error("Push failed."))
        self.worker.start()

    def _pull_file(self):
        src = self.pull_src.text().strip()
        dst = self.pull_dst.text().strip() or "."
        cmd = [ADB_PATH, "pull", src, dst]
        self.console.append(f"$ {' '.join(cmd)}")
        self.worker = CommandWorker(cmd)
        self.worker.output_signal.connect(self.console.append)
        self.worker.finished_signal.connect(lambda rc: self.console.append_success("Pull complete!") if rc == 0 else self.console.append_error("Pull failed."))
        self.worker.start()

    def _list_files(self):
        path = self.browse_path.text().strip()
        self.file_list.clear()
        cmd = [ADB_PATH, "shell", "ls", "-la", path]
        self.console.append(f"$ {' '.join(cmd)}")
        self.worker = CommandWorker(cmd)
        self.worker.output_signal.connect(self._add_file_item)
        self.worker.start()

    def _add_file_item(self, line: str):
        if line:
            item = QListWidgetItem(line)
            if line.startswith("d"):
                item.setForeground(QColor(COLORS["accent2"]))
            self.file_list.addItem(item)


# ─── TAB: APP MANAGER ────────────────────────────────────────────────────────

class AppManagerTab(QWidget):
    def __init__(self, console):
        super().__init__()
        self.console = console
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)

        install_group = QGroupBox("📦  Install APK")
        install_layout = QGridLayout(install_group)
        install_layout.setSpacing(10)

        install_layout.addWidget(QLabel("APK File:"), 0, 0)
        self.apk_path = QLineEdit()
        self.apk_path.setPlaceholderText("Select APK file…")
        install_layout.addWidget(self.apk_path, 0, 1)
        browse_btn = QPushButton("Browse")
        browse_btn.setFixedWidth(90)
        browse_btn.clicked.connect(self._browse_apk)
        install_layout.addWidget(browse_btn, 0, 2)

        options_row = QHBoxLayout()
        self.replace_check = QCheckBox("Replace existing (-r)")
        self.replace_check.setChecked(True)
        self.downgrade_check = QCheckBox("Allow downgrade (-d)")
        self.test_check = QCheckBox("Allow test apps (-t)")
        options_row.addWidget(self.replace_check)
        options_row.addWidget(self.downgrade_check)
        options_row.addWidget(self.test_check)
        options_row.addStretch()
        install_layout.addLayout(options_row, 1, 0, 1, 3)

        install_btn = QPushButton("📦  Install APK")
        install_btn.setObjectName("accent_btn")
        install_btn.clicked.connect(self._install_apk)
        install_layout.addWidget(install_btn, 2, 2)
        layout.addWidget(install_group)

        uninstall_group = QGroupBox("🗑  Uninstall Package")
        uninstall_layout = QGridLayout(uninstall_group)
        uninstall_layout.setSpacing(10)

        uninstall_layout.addWidget(QLabel("Package Name:"), 0, 0)
        self.pkg_name = QLineEdit()
        self.pkg_name.setPlaceholderText("com.example.app")
        uninstall_layout.addWidget(self.pkg_name, 0, 1)
        self.keep_data_check = QCheckBox("Keep data (-k)")
        uninstall_layout.addWidget(self.keep_data_check, 0, 2)

        uninstall_btn = QPushButton("🗑  Uninstall")
        uninstall_btn.setObjectName("danger_btn")
        uninstall_btn.clicked.connect(self._uninstall)
        uninstall_layout.addWidget(uninstall_btn, 1, 2)
        layout.addWidget(uninstall_group)

        pkg_group = QGroupBox("📋  Installed Packages")
        pkg_layout = QVBoxLayout(pkg_group)

        filter_row = QHBoxLayout()
        self.pkg_filter = QComboBox()
        self.pkg_filter.addItems(["All packages", "User packages (-3)", "System packages (-s)", "Disabled packages (-d)"])
        filter_row.addWidget(self.pkg_filter)
        list_btn = QPushButton("Refresh List")
        list_btn.setFixedWidth(110)
        list_btn.clicked.connect(self._list_packages)
        filter_row.addWidget(list_btn)
        pkg_layout.addLayout(filter_row)

        self.pkg_list = QListWidget()
        self.pkg_list.setMinimumHeight(120)
        self.pkg_list.itemDoubleClicked.connect(self._copy_pkg_name)
        pkg_layout.addWidget(self.pkg_list)

        pkg_layout.addWidget(QLabel("💡 Double-click a package to copy its name"))
        layout.addWidget(pkg_group)
        layout.addStretch()

    def _browse_apk(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select APK", filter="APK files (*.apk)")
        if path:
            self.apk_path.setText(path)

    def _install_apk(self):
        apk = self.apk_path.text().strip()
        if not apk:
            self.console.append_error("Please select an APK file.")
            return
        args = [ADB_PATH, "install"]
        if self.replace_check.isChecked():   args.append("-r")
        if self.downgrade_check.isChecked(): args.append("-d")
        if self.test_check.isChecked():      args.append("-t")
        args.append(apk)
        self.console.append(f"$ {' '.join(args)}")
        w = CommandWorker(args)
        w.output_signal.connect(self.console.append)
        w.finished_signal.connect(lambda rc: self.console.append_success("APK installed!") if rc == 0 else self.console.append_error("Install failed."))
        w.start()
        self._worker = w

    def _uninstall(self):
        pkg = self.pkg_name.text().strip()
        if not pkg:
            self.console.append_error("Please enter a package name.")
            return
        args = [ADB_PATH, "uninstall"]
        if self.keep_data_check.isChecked(): args.append("-k")
        args.append(pkg)
        self.console.append(f"$ {' '.join(args)}")
        w = CommandWorker(args)
        w.output_signal.connect(self.console.append)
        w.finished_signal.connect(lambda rc: self.console.append_success("Uninstalled!") if rc == 0 else self.console.append_error("Failed."))
        w.start()
        self._worker = w

    def _list_packages(self):
        self.pkg_list.clear()
        opts = {
            "All packages":         [],
            "User packages (-3)":   ["-3"],
            "System packages (-s)": ["-s"],
            "Disabled packages (-d)": ["-d"],
        }
        flag = opts.get(self.pkg_filter.currentText(), [])
        cmd = [ADB_PATH, "shell", "pm", "list", "packages"] + flag
        self.console.append(f"$ {' '.join(cmd)}")
        w = CommandWorker(cmd)
        w.output_signal.connect(self._add_pkg)
        w.start()
        self._pkg_worker = w

    def _add_pkg(self, line: str):
        if line.startswith("package:"):
            pkg = line.replace("package:", "").strip()
            self.pkg_list.addItem(pkg)

    def _copy_pkg_name(self, item):
        QApplication.clipboard().setText(item.text())
        self.console.append(f"📋 Copied: {item.text()}")


# ─── TAB: LOGCAT ─────────────────────────────────────────────────────────────

class LogcatTab(QWidget):
    def __init__(self, console):
        super().__init__()
        self.console = console
        self.worker  = None
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)

        ctrl_group = QGroupBox("⚙  Logcat Controls")
        ctrl_layout = QGridLayout(ctrl_group)
        ctrl_layout.setSpacing(10)

        ctrl_layout.addWidget(QLabel("Level:"), 0, 0)
        self.level_combo = QComboBox()
        self.level_combo.addItems(["Verbose (V)", "Debug (D)", "Info (I)", "Warning (W)", "Error (E)", "Fatal (F)"])
        self.level_combo.setCurrentText("Debug (D)")
        ctrl_layout.addWidget(self.level_combo, 0, 1)

        ctrl_layout.addWidget(QLabel("Tag Filter:"), 0, 2)
        self.tag_filter = QLineEdit()
        self.tag_filter.setPlaceholderText("e.g. MyApp (leave blank for all)")
        ctrl_layout.addWidget(self.tag_filter, 0, 3)

        ctrl_layout.addWidget(QLabel("Grep:"), 1, 0)
        self.grep_input = QLineEdit()
        self.grep_input.setPlaceholderText("Filter output (case-insensitive)")
        ctrl_layout.addWidget(self.grep_input, 1, 1)

        self.max_lines = QSpinBox()
        self.max_lines.setRange(100, 50000)
        self.max_lines.setValue(2000)
        self.max_lines.setSuffix(" lines")
        ctrl_layout.addWidget(QLabel("Max lines:"), 1, 2)
        ctrl_layout.addWidget(self.max_lines, 1, 3)

        layout.addWidget(ctrl_group)

        log_label = QLabel("📋  Live Logcat Output")
        log_label.setObjectName("section_label")
        layout.addWidget(log_label)

        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setFont(QFont("Consolas", 10))
        self.log_output.setMinimumHeight(300)
        layout.addWidget(self.log_output)

        btn_row = QHBoxLayout()
        self.start_btn = QPushButton("▶  Start Logcat")
        self.start_btn.setObjectName("accent_btn")
        self.start_btn.clicked.connect(self._start)
        btn_row.addWidget(self.start_btn)

        self.stop_btn = QPushButton("⏹  Stop")
        self.stop_btn.setObjectName("danger_btn")
        self.stop_btn.clicked.connect(self._stop)
        self.stop_btn.setEnabled(False)
        btn_row.addWidget(self.stop_btn)

        clear_btn = QPushButton("🗑  Clear")
        clear_btn.clicked.connect(self.log_output.clear)
        btn_row.addWidget(clear_btn)

        save_btn = QPushButton("💾  Save Log")
        save_btn.clicked.connect(self._save_log)
        btn_row.addWidget(save_btn)

        layout.addLayout(btn_row)
        self._line_count = 0

    def _level_char(self):
        return self.level_combo.currentText().split("(")[1].rstrip(")")

    def _start(self):
        if self.worker and self.worker.isRunning():
            return
        self.log_output.clear()
        self._line_count = 0

        args = [ADB_PATH, "logcat", "-v", "time"]
        tag = self.tag_filter.text().strip()
        if tag:
            args += [f"{tag}:{self._level_char()}", "*:S"]
        else:
            args += [f"*:{self._level_char()}"]

        self.console.append(f"$ {' '.join(args)}")
        self.worker = CommandWorker(args)
        self.worker.output_signal.connect(self._append_log)
        self.worker.finished_signal.connect(self._on_stop)
        self.worker.start()

        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)

    def _append_log(self, line: str):
        grep = self.grep_input.text().strip().lower()
        if grep and grep not in line.lower():
            return

        max_lines = self.max_lines.value()
        if self._line_count > max_lines:
            return

        color = COLORS["text"]
        if " E/" in line or " E " in line:   color = COLORS["danger"]
        elif " W/" in line or " W " in line: color = COLORS["warning"]
        elif " I/" in line or " I " in line: color = "#64B5F6"
        elif " D/" in line or " D " in line: color = COLORS["accent2"]

        self.log_output.append(f'<span style="color:{color};">{line}</span>')
        self._line_count += 1

        if self._line_count >= max_lines:
            self._stop()
            self.log_output.append(f'<span style="color:{COLORS["warning"]};">Max lines reached. Stopped.</span>')

    def _stop(self):
        if self.worker:
            self.worker.stop()

    def _on_stop(self, _):
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.console.append("Logcat stopped.")

    def _save_log(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save Log", "logcat.txt", "Text (*.txt)")
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self.log_output.toPlainText())
            self.console.append_success(f"Log saved to: {path}")


# ─── TAB: FASTBOOT ───────────────────────────────────────────────────────────

class FastbootTab(QWidget):
    def __init__(self, console):
        super().__init__()
        self.console = console
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)

        warn = QLabel("⚠  WARNING: Fastboot operations can BRICK your device. Use with caution!")
        warn.setStyleSheet(f"color:{COLORS['warning']}; font-weight:600; padding:8px; background:{COLORS['bg_card']}; border-radius:6px;")
        warn.setWordWrap(True)
        layout.addWidget(warn)

        flash_group = QGroupBox("⚡  Flash Partition")
        flash_layout = QGridLayout(flash_group)
        flash_layout.setSpacing(10)

        flash_layout.addWidget(QLabel("Partition:"), 0, 0)
        self.partition_combo = QComboBox()
        self.partition_combo.addItems([
            "boot", "recovery", "system", "vendor", "vbmeta",
            "dtbo", "super", "userdata", "cache", "persist"
        ])
        self.partition_combo.setEditable(True)
        flash_layout.addWidget(self.partition_combo, 0, 1)

        flash_layout.addWidget(QLabel("Image File:"), 1, 0)
        self.img_path = QLineEdit()
        self.img_path.setPlaceholderText("Select .img file…")
        flash_layout.addWidget(self.img_path, 1, 1)
        browse_btn = QPushButton("Browse")
        browse_btn.setFixedWidth(90)
        browse_btn.clicked.connect(self._browse_img)
        flash_layout.addWidget(browse_btn, 0, 2)

        flash_btn = QPushButton("⚡  Flash")
        flash_btn.setObjectName("danger_btn")
        flash_btn.clicked.connect(self._flash)
        flash_layout.addWidget(flash_btn, 1, 2)
        layout.addWidget(flash_group)

        quick_group = QGroupBox("🚀  Quick Actions")
        quick_layout = QGridLayout(quick_group)
        quick_layout.setSpacing(10)

        actions = [
            ("Get Bootloader State",  self._get_unlock_state),
            ("OEM Unlock",            self._oem_unlock),
            ("OEM Lock",              self._oem_lock),
            ("Erase Userdata",        self._erase_userdata),
            ("Reboot System",         lambda: self._fastboot(["reboot"])),
            ("Reboot Recovery",       lambda: self._fastboot(["reboot", "recovery"])),
            ("Reboot Bootloader",     lambda: self._fastboot(["reboot-bootloader"])),
            ("Fastboot Devices",      lambda: self._fastboot(["devices"])),
        ]
        for i, (label, fn) in enumerate(actions):
            btn = QPushButton(label)
            if "Unlock" in label or "Erase" in label:
                btn.setObjectName("danger_btn")
            btn.clicked.connect(fn)
            quick_layout.addWidget(btn, i // 2, i % 2)

        layout.addWidget(quick_group)
        layout.addStretch()

    def _browse_img(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Image", filter="Image files (*.img);;All files (*)")
        if path:
            self.img_path.setText(path)

    def _fastboot(self, args):
        cmd = [FASTBOOT_PATH] + args
        self.console.append(f"$ {' '.join(cmd)}")
        w = CommandWorker(cmd)
        w.output_signal.connect(self.console.append)
        w.finished_signal.connect(lambda rc: self.console.append_success("Done.") if rc == 0 else self.console.append_error(f"Exit {rc}"))
        w.start()
        self._worker = w

    def _flash(self):
        part = self.partition_combo.currentText().strip()
        img  = self.img_path.text().strip()
        if not img:
            self.console.append_error("Please select an image file.")
            return
        reply = QMessageBox.warning(
            self, "Confirm Flash",
            f"Flash '{img}' to partition '{part}'?\n\nThis may brick your device!",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel
        )
        if reply == QMessageBox.StandardButton.Yes:
            self._fastboot(["flash", part, img])

    def _get_unlock_state(self):
        self._fastboot(["getvar", "unlocked"])

    def _oem_unlock(self):
        reply = QMessageBox.warning(
            self, "OEM Unlock",
            "OEM Unlock will WIPE all data on your device!\nAre you sure?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel
        )
        if reply == QMessageBox.StandardButton.Yes:
            self._fastboot(["flashing", "unlock"])

    def _oem_lock(self):
        self._fastboot(["flashing", "lock"])

    def _erase_userdata(self):
        reply = QMessageBox.warning(
            self, "Erase Userdata",
            "This will ERASE ALL DATA on your device!\nAre you absolutely sure?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel
        )
        if reply == QMessageBox.StandardButton.Yes:
            self._fastboot(["erase", "userdata"])


# ─── TAB: SIDELOAD ───────────────────────────────────────────────────────────

class SideloadTab(QWidget):
    def __init__(self, console):
        super().__init__()
        self.console = console
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)

        info = QLabel(
            "ℹ  ADB Sideload is used to install OTA packages from recovery mode.\n"
            "Your device must be in Recovery mode and sideload mode enabled."
        )
        info.setStyleSheet(f"color:{COLORS['accent2']}; padding:10px; background:{COLORS['bg_card']}; border-radius:6px;")
        info.setWordWrap(True)
        layout.addWidget(info)

        sideload_group = QGroupBox("📦  Sideload OTA / ZIP Package")
        sl_layout = QGridLayout(sideload_group)
        sl_layout.setSpacing(10)

        sl_layout.addWidget(QLabel("Package File:"), 0, 0)
        self.sl_path = QLineEdit()
        self.sl_path.setPlaceholderText("Select .zip or .apks file…")
        sl_layout.addWidget(self.sl_path, 0, 1)
        browse_btn = QPushButton("Browse")
        browse_btn.setFixedWidth(90)
        browse_btn.clicked.connect(self._browse)
        sl_layout.addWidget(browse_btn, 0, 2)

        self.auto_reboot = QCheckBox("Auto reboot after sideload")
        self.auto_reboot.setChecked(True)
        sl_layout.addWidget(self.auto_reboot, 1, 1)

        sl_btn = QPushButton("📦  Start Sideload")
        sl_btn.setObjectName("accent_btn")
        sl_btn.clicked.connect(self._sideload)
        sl_layout.addWidget(sl_btn, 1, 2)
        layout.addWidget(sideload_group)

        prog_group = QGroupBox("📊  Progress")
        prog_layout = QVBoxLayout(prog_group)
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        prog_layout.addWidget(self.progress)
        self.prog_label = QLabel("Ready")
        self.prog_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        prog_layout.addWidget(self.prog_label)
        layout.addWidget(prog_group)

        guide_group = QGroupBox("📖  How to Sideload")
        guide_layout = QVBoxLayout(guide_group)
        steps = [
            "1. Boot your device into Recovery mode",
            "2. Navigate to 'Apply update from ADB'",
            "3. Connect device via USB",
            "4. Select your OTA/ZIP file above",
            "5. Click 'Start Sideload'",
            "6. Wait for the process to complete",
        ]
        for step in steps:
            lbl = QLabel(step)
            lbl.setStyleSheet(f"color:{COLORS['text']}; padding:3px;")
            guide_layout.addWidget(lbl)
        layout.addWidget(guide_group)
        layout.addStretch()

    def _browse(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Package",
            filter="Zip/APKS files (*.zip *.apks);;All files (*)"
        )
        if path:
            self.sl_path.setText(path)

    def _sideload(self):
        path = self.sl_path.text().strip()
        if not path:
            self.console.append_error("Please select a package file.")
            return
        self.progress.setValue(0)
        self.prog_label.setText("Sideloading…")
        cmd = [ADB_PATH, "sideload", path]
        self.console.append(f"$ {' '.join(cmd)}")
        w = CommandWorker(cmd)
        w.output_signal.connect(self._on_output)
        w.finished_signal.connect(self._on_done)
        w.start()
        self._worker = w

    def _on_output(self, line: str):
        self.console.append(line)
        if "%" in line:
            try:
                pct = int(line.strip().rstrip("%").split()[-1])
                self.progress.setValue(pct)
                self.prog_label.setText(f"{pct}%")
            except ValueError:
                pass

    def _on_done(self, rc: int):
        if rc == 0:
            self.progress.setValue(100)
            self.prog_label.setText("✅ Sideload complete!")
            self.console.append_success("Sideload complete!")
            if self.auto_reboot.isChecked():
                w = CommandWorker([ADB_PATH, "reboot"])
                w.start()
        else:
            self.prog_label.setText("❌ Sideload failed")
            self.console.append_error("Sideload failed.")


# ─── TAB: TERMINAL ───────────────────────────────────────────────────────────

class TerminalTab(QWidget):
    def __init__(self, console):
        super().__init__()
        self.console = console
        self.history = []
        self.hist_idx = -1
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(16, 16, 16, 16)

        lbl = QLabel("🖥  ADB Shell / Custom Command Terminal")
        lbl.setObjectName("section_label")
        layout.addWidget(lbl)

        quick_group = QGroupBox("⚡  Quick Commands")
        quick_layout = QGridLayout(quick_group)
        quick_layout.setSpacing(8)

        quick_cmds = [
            ("Device Info",       "adb shell getprop ro.product.model"),
            ("IP Address",        "adb shell ip route"),
            ("Disk Usage",        "adb shell df -h"),
            ("CPU Info",          "adb shell cat /proc/cpuinfo | head -20"),
            ("Memory Info",       "adb shell cat /proc/meminfo | head -10"),
            ("Running Processes", "adb shell ps -A | head -30"),
            ("Screen Size",       "adb shell wm size"),
            ("Screen Density",    "adb shell wm density"),
        ]
        for i, (label, cmd) in enumerate(quick_cmds):
            btn = QPushButton(label)
            btn.clicked.connect(lambda checked, c=cmd: self._run_quick(c))
            quick_layout.addWidget(btn, i // 4, i % 4)
        layout.addWidget(quick_group)

        self.terminal = QTextEdit()
        self.terminal.setReadOnly(True)
        self.terminal.setFont(QFont("Consolas", 11))
        self.terminal.setMinimumHeight(200)
        layout.addWidget(self.terminal)

        input_row = QHBoxLayout()
        prompt_lbl = QLabel("$")
        prompt_lbl.setStyleSheet(f"color:{COLORS['accent']}; font-family:Consolas; font-weight:700; font-size:14px;")
        prompt_lbl.setFixedWidth(16)
        input_row.addWidget(prompt_lbl)

        self.cmd_input = QLineEdit()
        self.cmd_input.setPlaceholderText("Enter ADB command (e.g. adb shell ls /sdcard/)…")
        self.cmd_input.returnPressed.connect(self._run)
        self.cmd_input.installEventFilter(self)
        input_row.addWidget(self.cmd_input)

        run_btn = QPushButton("Run  ▶")
        run_btn.setObjectName("accent_btn")
        run_btn.setFixedWidth(90)
        run_btn.clicked.connect(self._run)
        input_row.addWidget(run_btn)

        clear_btn = QPushButton("Clear")
        clear_btn.setFixedWidth(70)
        clear_btn.clicked.connect(self.terminal.clear)
        input_row.addWidget(clear_btn)
        layout.addLayout(input_row)

        hint = QLabel("💡 Use ↑↓ arrow keys to navigate command history")
        hint.setStyleSheet(f"color:{COLORS['text_dim']}; font-size:11px;")
        layout.addWidget(hint)

    def eventFilter(self, obj, event):
        from PyQt6.QtCore import QEvent
        if obj == self.cmd_input and event.type() == QEvent.Type.KeyPress:
            key = event.key()
            if key == Qt.Key.Key_Up and self.history:
                self.hist_idx = max(0, self.hist_idx - 1)
                self.cmd_input.setText(self.history[self.hist_idx])
            elif key == Qt.Key.Key_Down and self.history:
                self.hist_idx = min(len(self.history), self.hist_idx + 1)
                if self.hist_idx < len(self.history):
                    self.cmd_input.setText(self.history[self.hist_idx])
                else:
                    self.cmd_input.clear()
        return super().eventFilter(obj, event)

    def _run_quick(self, cmd: str):
        self.cmd_input.setText(cmd)
        self._run()

    def _run(self):
        raw = self.cmd_input.text().strip()
        if not raw:
            return

        self.history.append(raw)
        self.hist_idx = len(self.history)
        self.cmd_input.clear()

        parts = raw.split()
        if parts[0].lower() == "adb":
            cmd = [ADB_PATH] + parts[1:]
        elif parts[0].lower() == "fastboot":
            cmd = [FASTBOOT_PATH] + parts[1:]
        else:
            cmd = parts

        self.terminal.append(f'<span style="color:{COLORS["accent"]};">$ {raw}</span>')

        w = CommandWorker(cmd)
        w.output_signal.connect(lambda line: self.terminal.append(line))
        w.finished_signal.connect(lambda rc: self.terminal.append(
            f'<span style="color:{COLORS["success"]};">[OK]</span>' if rc == 0
            else f'<span style="color:{COLORS["danger"]};">[ERR {rc}]</span>'
        ))
        w.start()
        self._worker = w


# ─── HEADER ───────────────────────────────────────────────────────────────────

class AppHeader(QFrame):
    def __init__(self):
        super().__init__()
        self.setObjectName("header_frame")
        self.setFixedHeight(72)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 8, 20, 8)
        layout.setSpacing(16)

        logo_frame = QFrame()
        logo_frame.setFixedSize(44, 44)
        logo_frame.setStyleSheet(
            f"background: qlineargradient(x1:0,y1:0,x2:1,y2:1,"
            f"stop:0 {COLORS['accent']}, stop:1 {COLORS['accent2']});"
            f"border-radius: 10px;"
        )
        logo_lbl = QLabel("⚡", logo_frame)
        logo_lbl.setFont(QFont("Segoe UI Emoji", 20))
        logo_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_lbl.setGeometry(0, 0, 44, 44)
        logo_lbl.setStyleSheet("background:transparent; color:#0D1117;")
        layout.addWidget(logo_frame)

        title_col = QVBoxLayout()
        title_col.setSpacing(2)
        title_lbl = QLabel(APP_NAME)
        title_lbl.setObjectName("title_label")
        title_lbl.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        sub_lbl = QLabel(f"v{APP_VERSION}  •  Android Debug Bridge GUI  •  ADB + Fastboot + Sideload")
        sub_lbl.setObjectName("subtitle_label")
        title_col.addWidget(title_lbl)
        title_col.addWidget(sub_lbl)
        layout.addLayout(title_col)
        layout.addStretch()

        self.adb_ver_lbl = QLabel("ADB: checking…")
        self.adb_ver_lbl.setStyleSheet(f"color:{COLORS['text_dim']}; font-size:11px;")
        layout.addWidget(self.adb_ver_lbl)

        self.start_server_btn = QPushButton("▶  Start ADB Server")
        self.start_server_btn.setFixedWidth(160)
        layout.addWidget(self.start_server_btn)

        self.kill_server_btn = QPushButton("⏹  Kill ADB Server")
        self.kill_server_btn.setObjectName("danger_btn")
        self.kill_server_btn.setFixedWidth(160)
        layout.addWidget(self.kill_server_btn)

    def set_adb_version(self, version: str):
        self.adb_ver_lbl.setText(f"ADB: {version}")


# ─── MAIN WINDOW ─────────────────────────────────────────────────────────────

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{APP_NAME}  v{APP_VERSION}")
        self.setMinimumSize(1100, 760)
        self.resize(1200, 820)
        self._set_taskbar_icon()
        self._build_ui()
        self._check_adb()
        self._start_device_poll()

    def _set_taskbar_icon(self):
        pix = QPixmap(64, 64)
        pix.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pix)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        grad = QRadialGradient(32, 32, 32)
        grad.setColorAt(0.0, QColor(COLORS["accent"]))
        grad.setColorAt(1.0, QColor(COLORS["accent2"]))
        painter.setBrush(QBrush(grad))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(4, 4, 56, 56, 14, 14)
        painter.setFont(QFont("Segoe UI Emoji", 28))
        painter.setPen(QPen(QColor("#0D1117")))
        painter.drawText(pix.rect(), Qt.AlignmentFlag.AlignCenter, "⚡")
        painter.end()
        self.setWindowIcon(QIcon(pix))

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self.header = AppHeader()
        self.header.start_server_btn.clicked.connect(self._start_server)
        self.header.kill_server_btn.clicked.connect(self._kill_server)
        root.addWidget(self.header)

        self.device_bar = DeviceStatusBar()
        self.device_bar.refresh_requested.connect(self._refresh_devices)
        root.addWidget(self.device_bar)

        splitter = QSplitter(Qt.Orientation.Vertical)

        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(8, 8, 8, 0)
        content_layout.setSpacing(8)

        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.TabPosition.North)

        self.console = OutputConsole()

        self.device_tab   = DeviceInfoTab(self.console)
        self.file_tab     = FileManagerTab(self.console)
        self.app_tab      = AppManagerTab(self.console)
        self.logcat_tab   = LogcatTab(self.console)
        self.fastboot_tab = FastbootTab(self.console)
        self.sideload_tab = SideloadTab(self.console)
        self.terminal_tab = TerminalTab(self.console)

        tab_defs = [
            ("📱  Device",    self.device_tab),
            ("📂  Files",     self.file_tab),
            ("📦  Apps",      self.app_tab),
            ("📋  Logcat",    self.logcat_tab),
            ("⚡  Fastboot",  self.fastboot_tab),
            ("📦  Sideload",  self.sideload_tab),
            ("🖥  Terminal",  self.terminal_tab),
        ]
        for tab_name, widget in tab_defs:
            self.tabs.addTab(widget, tab_name)

        content_layout.addWidget(self.tabs)
        splitter.addWidget(content_widget)

        console_widget = QWidget()
        console_layout = QVBoxLayout(console_widget)
        console_layout.setContentsMargins(8, 0, 8, 8)
        console_layout.addWidget(self.console)
        splitter.addWidget(console_widget)

        splitter.setSizes([550, 220])
        root.addWidget(splitter)

        self.statusBar().setStyleSheet(
            f"background:{COLORS['bg_medium']}; color:{COLORS['text_dim']}; font-size:11px;"
        )
        self.statusBar().showMessage(f"  {APP_NAME}  |  Ready")

    def _check_adb(self):
        if not os.path.exists(ADB_PATH):
            self.console.append_error(f"ADB not found at: {ADB_PATH}")
            return
        w = CommandWorker([ADB_PATH, "version"])
        w.output_signal.connect(lambda line: self.header.set_adb_version(line) if "Android Debug Bridge" in line else None)
        w.start()
        self._ver_worker = w
        self.console.append_success(f"Platform Tools loaded from: {PT_DIR}")

    def _start_server(self):
        self.console.append("Starting ADB server…")
        w = CommandWorker([ADB_PATH, "start-server"])
        w.output_signal.connect(self.console.append)
        w.finished_signal.connect(lambda rc: self._refresh_devices())
        w.start()
        self._srv_worker = w

    def _kill_server(self):
        self.console.append("Killing ADB server…")
        w = CommandWorker([ADB_PATH, "kill-server"])
        w.output_signal.connect(self.console.append)
        w.start()
        self._kill_worker = w

    def _start_device_poll(self):
        self._poll_timer = QTimer(self)
        self._poll_timer.timeout.connect(self._refresh_devices)
        self._poll_timer.start(5000)
        self._refresh_devices()

    def _refresh_devices(self):
        w = CommandWorker([ADB_PATH, "devices"])
        w.output_signal.connect(self._parse_devices)
        w.start()
        self._dev_worker = w

    def _parse_devices(self, line: str):
        if "\t" in line:
            parts = line.split("\t")
            if len(parts) == 2:
                serial, state = parts[0].strip(), parts[1].strip()
                self.device_bar.set_device(serial, state)
                self.statusBar().showMessage(f"  Device: {serial}  [{state.upper()}]")
                return
        if "List of devices" in line:
            self.device_bar.set_device("", "")


# ─── ENTRY POINT ─────────────────────────────────────────────────────────────

def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLESHEET)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)
    # High-DPI is enabled by default in PyQt6 — no setAttribute needed

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
