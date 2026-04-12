import os
import subprocess

from PySide6.QtCore import Qt, QRectF, QTimer
from PySide6.QtGui import QLinearGradient
from PySide6.QtWidgets import QMessageBox, QDialog, QVBoxLayout, QHBoxLayout, QApplication, QLabel

from UI.UI_Tools import is_wayland


def get_monitor_geometries(self):
    """Return a dict {screen_name: (x, y, w, h)} by probing available tools (xrandr/wlr-randr/swaymsg) or QGuiApplication as fallback."""
    geometries = {}
    # Try xrandr first
    try:
        r = subprocess.run(["xrandr", "--query"], capture_output=True, text=True)
        for line in r.stdout.splitlines():
            if " connected" in line:
                parts = line.split()
                name = parts[0]
                import re

                m = re.search(r"(\d+)x(\d+)\+(\d+)\+(\d+)", line)
                if m:
                    w, h, x, y = map(int, m.groups())
                    geometries[name] = (x, y, w, h)
        if geometries:
            print(f"get_monitor_geometries: using xrandr -> {geometries}")
            return geometries
    except Exception:
        pass

    # Try wlr-randr
    try:
        r = subprocess.run(["wlr-randr"], capture_output=True, text=True)
        for line in r.stdout.splitlines():
            if " connected" in line or line.startswith("Output "):
                parts = line.split()
                # wlr-randr has different format; try to extract name and resolution if present
                name = parts[1] if len(parts) > 1 else parts[0]
                import re

                m = re.search(r"(\d+)x(\d+).*(\+\d+\+\d+)", line)
                if m:
                    w = int(m.group(1))
                    h = int(m.group(2))
                    pos = re.search(r"(\+\d+\+\d+)", line)
                    if pos:
                        xy = pos.group(1).lstrip("+").split("+")
                        x = int(xy[0])
                        y = int(xy[1])
                    else:
                        x = 0
                        y = 0
                    geometries[name] = (x, y, w, h)
        if geometries:
            print(f"get_monitor_geometries: using wlr-randr -> {geometries}")
            return geometries
    except Exception:
        pass

    # Try swaymsg
    try:
        r = subprocess.run(
            ["swaymsg", "-t", "get_outputs"], capture_output=True, text=True
        )
        import json

        outputs = json.loads(r.stdout)
        for out in outputs:
            if out.get("active"):
                name = out.get("name")
                x = int(out.get("rect", {}).get("x", 0))
                y = int(out.get("rect", {}).get("y", 0))
                w = int(out.get("rect", {}).get("width", 0))
                h = int(out.get("rect", {}).get("height", 0))
                geometries[name] = (x, y, w, h)
        if geometries:
            print(f"get_monitor_geometries: using swaymsg -> {geometries}")
            return geometries
    except Exception:
        pass

    # Fallback: use QGuiApplication.screens()
    try:
        from PySide6.QtGui import QGuiApplication

        screens = QGuiApplication.screens()
        for s in screens:
            try:
                name = s.name()
            except Exception:
                name = str(s.geometry())
            g = s.geometry()
            geometries[name] = (g.x(), g.y(), g.width(), g.height())
        if geometries:
            print(f"get_monitor_geometries: using QGuiApplication -> {geometries}")
            return geometries
    except Exception:
        pass

    print("get_monitor_geometries: no geometries found")
    return geometries

def show_monitor_map(self, duration_ms=3000):
    """Show a dialog that draws a scaled simulation of all monitors based on their coordinates."""
    # Local GUI imports required for drawing
    from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QFont
    from PySide6.QtWidgets import QPushButton, QWidget

    geoms = get_monitor_geometries(self)
    if not geoms:
        print("show_monitor_map: no geometries to show")
        QMessageBox.information(
            self, "Monitor Map", "No monitor geometry information available."
        )
        return

    # Create the dialog and widget
    class MonitorMapWidget(QWidget):
        def __init__(self, geometries, parent=None):
            super().__init__(parent)
            self.geometries = geometries  # dict name: (x,y,w,h)
            # compute bounds
            xs = [x for (x, y, w, h) in geometries.values()] + [
                x + w for (x, y, w, h) in geometries.values()
            ]
            ys = [y for (x, y, w, h) in geometries.values()] + [
                y + h for (x, y, w, h) in geometries.values()
            ]
            self.min_x = min(xs)
            self.min_y = min(ys)
            self.max_x = max(xs)
            self.max_y = max(ys)
            self.margin = 20

        def paintEvent(self, event):
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            rect = self.rect()

            # Background gradient
            grad = QLinearGradient(rect.topLeft(), rect.bottomRight())
            grad.setColorAt(0.0, QColor(55, 55, 60))
            grad.setColorAt(1.0, QColor(35, 35, 40))
            painter.fillRect(rect, grad)

            total_w = self.max_x - self.min_x
            total_h = self.max_y - self.min_y
            if total_w == 0 or total_h == 0:
                return
            scale = min(
                (rect.width() - 2 * self.margin) / total_w,
                (rect.height() - 2 * self.margin) / total_h,
            )

            # Pens and fonts
            pen_border = QPen(QColor(200, 200, 200, 180))
            pen_border.setWidth(2)
            painter.setFont(QFont("Sans", 10))

            for idx, (name, (x, y, w, h)) in enumerate(self.geometries.items(), 1):
                sx = int((x - self.min_x) * scale) + self.margin
                sy = int((y - self.min_y) * scale) + self.margin
                sw = max(6, int(w * scale))
                sh = max(6, int(h * scale))

                # Shadow
                shadow_color = QColor(0, 0, 0, 100)
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(QBrush(shadow_color))
                painter.drawRoundedRect(QRectF(sx + 6, sy + 6, sw, sh), 8, 8)

                # Monitor fill gradient
                mg = QLinearGradient(sx, sy, sx, sy + h)
                if os.getenv("WALLPAPER_OVERLAY_DEBUG"):
                    mg.setColorAt(0.0, QColor(255, 95, 95))
                    mg.setColorAt(1.0, QColor(200, 40, 40))
                else:
                    mg.setColorAt(0.0, QColor(60, 60, 65))
                    mg.setColorAt(1.0, QColor(40, 40, 45))
                painter.setBrush(QBrush(mg))
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawRoundedRect(QRectF(sx, sy, sw, sh), 8, 8)

                # Border
                painter.setPen(pen_border)
                painter.setBrush(Qt.BrushStyle.NoBrush)
                painter.drawRoundedRect(QRectF(sx, sy, sw, sh), 8, 8)

                # Label band
                band_h = min(28, max(18, sh // 6))
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(QBrush(QColor(0, 0, 0, 140)))
                painter.drawRoundedRect(
                    QRectF(sx + 6, sy + 6, sw - 12, band_h), 6, 6
                )

                painter.setPen(QColor(235, 235, 235))
                painter.setFont(QFont("Sans", 10))
                painter.drawText(sx + 12, sy + band_h - 6, f"{idx}  {name}")

                # Index badge
                badge_r = 18
                badge_x = sx + sw - badge_r - 10
                badge_y = sy + 10
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(QBrush(QColor(220, 80, 80)))
                painter.drawEllipse(QRectF(badge_x, badge_y, badge_r, badge_r))
                painter.setPen(QColor(255, 255, 255))
                painter.setFont(QFont("Sans", 9, QFont.Weight.Bold))
                painter.drawText(badge_x + 5, badge_y + 13, str(idx))

            # footer hint
            painter.setPen(QColor(160, 160, 160))
            painter.setFont(QFont("Sans", 9))
            painter.drawText(
                rect.left() + 10,
                rect.bottom() - 10,
                "Simulation: positions and sizes are approximate",
            )

    # Build dialog
    dlg = QDialog(self)
    dlg.setWindowTitle("Monitor Map")
    dlg.resize(900, 600)
    layout = QVBoxLayout(dlg)
    widget = MonitorMapWidget(geoms, dlg)
    layout.addWidget(widget)
    btn_layout = QHBoxLayout()
    btn_close = QPushButton("Close")
    btn_close.clicked.connect(dlg.accept)
    btn_layout.addStretch()
    btn_layout.addWidget(btn_close)
    layout.addLayout(btn_layout)

    print(f"Showing monitor map with geometries: {geoms}")
    # Show dialog until the user closes it with the Close button
    dlg.show()

def identify_monitor(self, screen_name, duration_ms=2000):
    """Show overlay only for a single Screen and log diagnostics."""
    print(f"identify_monitor: requested for {screen_name}")
    # If overlays exist, show only that one
    ov = None
    if hasattr(self, "_screen_overlays"):
        ov = self._screen_overlays.get(screen_name)
    if ov:
        try:
            # Try re-asserting assigned Screen
            assigned = getattr(ov, "_assigned_qscreen", None)
            if assigned and ov.windowHandle():
                try:
                    ov.windowHandle().setScreen(assigned)
                except Exception as e:
                    print(
                        f"Warning: could not setScreen on single show for {screen_name}: {e}"
                    )
            ov.show()
            ov.raise_()
            QApplication.processEvents()
            try:
                handle = ov.windowHandle()
                mapped = None
                if handle and handle.screen():
                    try:
                        mapped = handle.screen().name()
                    except Exception:
                        mapped = str(handle.screen().geometry())
                print(
                    f"Single overlay shown for {screen_name}: visible={ov.isVisible()}, mapped_screen={mapped}, geom={ov.geometry()}"
                )
            except Exception as e:
                print(f"Diagnostic error for single overlay {screen_name}: {e}")
            QTimer.singleShot(duration_ms, ov.hide)
            return
        except Exception as e:
            print(f"Error showing single overlay for {screen_name}: {e}")
    # if no overlay exists or it failed, try fallback
    print(f"identify_monitor: fallback for {screen_name}")
    if is_wayland(self):
        QMessageBox.information(
            self,
            "Identify Monitors",
            "Wayland compositor detected. Overlays may be restricted to the Screen containing the application.\nUse the 'Identify' button while the app is on the target monitor, or move the app to that monitor and retry.",
        )
    # Fallback minimal visible dialog
    try:
        tmp = QDialog(self)
        tmp.setWindowTitle(f"{screen_name}")
        tmp.setModal(False)
        tmp_label = QLabel(screen_name)
        tmp_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tmp_layout = QVBoxLayout(tmp)
        tmp_layout.addWidget(tmp_label)
        tmp.setFixedSize(300, 150)
        tmp.show()
        QTimer.singleShot(2000, tmp.close)
    except Exception as e:
        print(f"identify_monitor fallback dialog error: {e}")

def identify_monitors(self):
    """Show overlay labels on each Screen to identify them (persistent-overlay method)."""
    # If Wayland, show a monitor map simulation (Wayland may restrict real overlays)
    if is_wayland(self):
        print("Wayland detected: showing monitor map simulation")
        show_monitor_map(self, 3000)
        return

    # Inform Wayland users about possible compositor restrictions
    if is_wayland(self):
        QMessageBox.information(
            self,
            "Identify Monitors",
            "Wayland compositor detected: some compositors restrict showing windows on outputs other than the one containing the app.\nIf overlays don't appear on other monitors, move the app to that monitor or use the per-Screen 'Identify' buttons.",
        )
    print("Showing persistent overlays for identify_monitors")
    try:
        self.show_overlays(2000)
    except Exception as e:
        print(
            f"Fallback: overlays failed with {e}, falling back to transient popups"
        )
        # If overlays fail, try the previous transient approach (best-effort)
        try:
            for idx, screen in enumerate(self.detected_screens):
                QMessageBox.information(self, "Screen", f"{idx + 1} - {screen}")
        except Exception as e2:
            print(f"Fallback fallback failed: {e2}")
