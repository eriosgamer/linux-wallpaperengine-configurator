import os
import subprocess

from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QMessageBox

def insert_text_to_log(self, text):
    log_file = "/tmp/wallpaper-engine.log"
    from datetime import datetime

    # Get current local date and time
    now = datetime.now()

    # Format as DD-MM-YYYY HH:MM:SS AM/PM
    date = now.strftime("%d-%m-%Y %I:%M:%S %p")
    with open(log_file, "a", encoding="utf-8") as file:
        file.write(f"\n[{date}] {text}")


def clear_log(self):
    """ Clears the log file """
    log_file = "/tmp/wallpaper-engine.log"
    try:
        if not os.path.exists(log_file):
            QMessageBox.information(self, "Logs", "No log file found yet.")
            return
        open(log_file, "w").close()
        QMessageBox.information(self, "Logs", "Log file cleared.")
        insert_text_to_log(self, "Log was cleared")

    except Exception as e:
        QMessageBox.critical(self, "Error", f"Error reading log: {e}")


def view_logs(self):
    """
    Show the content of the wallpaper engine log file in a popup window.
    """
    log_file = "/tmp/wallpaper-engine.log"
    try:
        if not os.path.exists(log_file):
            QMessageBox.information(self, "Logs", "No log file found yet.")
            return

        # Use PySide6 widgets for the log window
        from PySide6.QtWidgets import (
            QDialog,
            QVBoxLayout,
            QHBoxLayout,
            QTextEdit,
            QCheckBox,
            QPushButton,
        )

        log_window = QDialog(self)
        log_window.setWindowTitle("Wallpaper Engine Logs")
        log_window.resize(800, 600)

        layout = QVBoxLayout(log_window)

        # Checkboxes for auto-refresh and auto-follow
        check_box_layout = QHBoxLayout()
        auto_refresh_check = QCheckBox("Auto-refresh")
        auto_follow_check = QCheckBox("Auto-follow")
        auto_refresh_check.setChecked(True)
        auto_follow_check.setChecked(True)
        check_box_layout.addWidget(auto_refresh_check)
        check_box_layout.addWidget(auto_follow_check)
        check_box_layout.addStretch()
        layout.addLayout(check_box_layout)

        # Text area to show logs
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setFont(QFont("Monaco", 10))
        layout.addWidget(self.text_edit)

        # Clear Logs Button
        btnc_layout = QHBoxLayout()
        clear_btn = QPushButton("Clear Logs")
        clear_btn.clicked.connect(lambda checked: clear_log(self))
        btnc_layout.addStretch()
        btnc_layout.addWidget(clear_btn)
        layout.addLayout(btnc_layout)

        # Close button
        btn_layout = QHBoxLayout()
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(log_window.accept)
        btn_layout.addStretch()
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)

        def read_last_lines(file_path, max_bytes=200 * 1024, max_lines=2000):
            """Read only the last part of a large file efficiently."""
            try:
                with open(file_path, "rb") as f:
                    f.seek(0, os.SEEK_END)
                    file_size = f.tell()
                    seek_pos = max(0, file_size - max_bytes)
                    f.seek(seek_pos)
                    data = f.read().decode("utf-8", errors="replace")
                    lines = data.splitlines()
                    # If not at start, skip possibly incomplete first line
                    if seek_pos > 0 and lines:
                        lines = lines[1:]
                    if len(lines) > max_lines:
                        lines = lines[-max_lines:]
                    return "\n".join(lines)
            except Exception as e:
                return f"Error reading log: {e}"

        def refresh_log_content():
            # Stop accessing the widget if it was destroyed or window is closing
            if not log_window.isVisible():
                return
            
            try:
                content = read_last_lines(log_file)
                self.text_edit.setPlainText(content)
                if auto_follow_check.isChecked():
                    from PySide6.QtGui import QTextCursor
                    self.text_edit.moveCursor(QTextCursor.MoveOperation.End)
            except Exception as e:
                print(f"Error in refresh_log_content: {e}")

            # Schedule next refresh if checkbox is checked
            if auto_refresh_check.isChecked():
                QTimer.singleShot(2000, refresh_log_content)

        # Connect checkbox to refresh logic
        auto_refresh_check.stateChanged.connect(
            lambda state: refresh_log_content() if state == Qt.CheckState.Checked.value else None
        )

        # Initial call to start the loop
        # We use a short singleShot to ensure the window is visible/ready
        QTimer.singleShot(100, refresh_log_content)

        log_window.exec()

    except Exception as e:
        QMessageBox.critical(self, "Error", f"Error reading log: {e}")
