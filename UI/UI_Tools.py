import os
import subprocess

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QDialog, QLabel, QVBoxLayout, QApplication


def is_wayland(self):
    """Return True if running under Wayland (likely compositor restrictions apply)."""
    return bool(os.environ.get("WAYLAND_DISPLAY"))


def qt_to_we_color(self, color):
    """Convierte QColor a string 'R.rr,G.gg,B.bb' (0.0 a 1.0) - Sin espacios para evitar errores de shell"""
    return f"{color.redF():.6f},{color.greenF():.6f},{color.blueF():.6f}"


def we_to_qt_color(self, we_str):
    """Convierte string '0.1, 0.2, 0.3' o '0.1 0.2 0.3' a un objeto QColor de Qt"""
    from PySide6.QtGui import QColor
    try:
        # Reemplazar comas por espacios y luego dividir por espacios para manejar ambos formatos
        clean_str = we_str.replace(",", " ")
        parts = [float(x) for x in clean_str.split()]
        if len(parts) >= 3:
            return QColor.fromRgbF(min(1.0, max(0.0, parts[0])),
                                   min(1.0, max(0.0, parts[1])),
                                   min(1.0, max(0.0, parts[2])))
    except:
        return QColor("white")
    return QColor("white")


def normalize_text(text):
    """
    Normalize text for display, ensuring it is a string and stripping problematic characters.
    """
    if not isinstance(text, str):
        try:
            text = str(text)
        except Exception:
            return ""
    # Optionally, strip null bytes and control characters
    return text.replace("\x00", "").strip()


def create_overlays(self):
    """Create persistent per-Screen overlay widgets and keep them hidden.
    These persistent windows are more likely to be accepted by Wayland compositors
    than ephemeral transient popups created on demand.
    """
    from PySide6.QtGui import QGuiApplication

    self._screen_overlays = {}
    popup_w, popup_h = 300, 150

    # Gather xrandr geometries as a primary source
    geometries = {}
    try:
        result = subprocess.run(
            ["xrandr", "--query"], capture_output=True, text=True
        )
        for line in result.stdout.splitlines():
            if " connected" in line:
                parts = line.split()
                screen_name = parts[0]
                import re

                m = re.search(r"(\d+)x(\d+)\+(\d+)\+(\d+)", line)
                if m:
                    w, h, x, y = map(int, m.groups())
                    geometries[screen_name] = (x, y, w, h)
    except Exception:
        pass

    screens = QGuiApplication.screens()
    assigned_qscreen = None

    for idx, screen in enumerate(self.detected_screens):
        # Prefer xrandr geometry, fallback to QScreen lookup
        geom = geometries.get(screen)
        if geom is None:
            found_qs = None
            for s in screens:
                try:
                    if s.name() == screen:
                        found_qs = s
                        break
                except Exception:
                    continue
            if found_qs:
                sgeom = found_qs.geometry()
                x, y, w, h = sgeom.x(), sgeom.y(), sgeom.width(), sgeom.height()
            else:
                print(f"Warning: Could not determine geometry for overlay {screen}")
                continue
        else:
            x, y, w, h = geom

        overlay = QDialog(None)
        flags = (
                Qt.WindowType.Window
                | Qt.WindowType.FramelessWindowHint
                | Qt.WindowType.WindowStaysOnTopHint
                | Qt.WindowType.Tool
        )
        overlay.setWindowFlags(flags)
        # Use an opaque background (more compatible) but keep style consistent
        try:
            overlay.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)
            overlay.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)
        except Exception:
            pass

        overlay.setModal(False)
        overlay.setFixedSize(popup_w, popup_h)
        target_x = x + (w - popup_w) // 2
        target_y = y + (h - popup_h) // 2
        overlay.move(target_x, target_y)

        label = QLabel(f"{idx + 1}\n{screen}")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # If debug env var is set, use a highly visible opaque style for diagnostics
        if os.getenv("WALLPAPER_OVERLAY_DEBUG"):
            label.setStyleSheet(
                "background:#ff1744;color:white;font-size:36px;padding:30px;border-radius:6px;box-shadow:0 0 0 5px rgba(255,23,68,0.8);"
            )
            try:
                overlay.setStyleSheet(
                    "background:rgba(255,23,68,0.95);border:5px solid #ff1744;"
                )
            except Exception:
                pass
        else:
            label.setStyleSheet(
                "background:#222;color:white;font-size:36px;padding:30px;border-radius:6px;"
            )

        layout = QVBoxLayout(overlay)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(label)

        # Attempt to associate overlay with QScreen (best-effort)
        try:
            # Request a native window handle so we can call setScreen reliably
            try:
                overlay.setAttribute(Qt.WidgetAttribute.WA_NativeWindow, True)
            except Exception:
                pass

            assigned_qscreen = None
            # Ensure a windowHandle exists by briefly showing the window
            try:
                overlay.show()
                QApplication.processEvents()
            except Exception:
                pass

            if overlay.windowHandle():
                for s in screens:
                    sgeom = s.geometry()
                    if (
                            sgeom.x() <= target_x < sgeom.x() + sgeom.width()
                            and sgeom.y() <= target_y < sgeom.y() + sgeom.height()
                    ):
                        try:
                            overlay.windowHandle().setScreen(s)
                            assigned_qscreen = s
                            try:
                                name = s.name()
                            except Exception:
                                name = str(sgeom)
                            print(
                                f"Overlay for {screen}: assigned to: {name} x:({sgeom.x()}, y:{sgeom.y()}, w:{sgeom.width()}, h:{sgeom.height()})"
                            )
                        except Exception as e:
                            print(f"Overlay setScreen error for {screen}: {e}")
                        break

            # Hide after assignment; will show later via show_overlays
            try:
                overlay.hide()
                QApplication.processEvents()
            except Exception:
                pass
        except Exception as e:
            print(f"Overlay windowHandle/setup error for {screen}: {e}")

        # Remember the assigned qscreen for later reuse when showing
        overlay.setProperty("_assigned_qscreen", assigned_qscreen)
        self._screen_overlays[screen] = overlay.property("_assigned_qscreen")

def show_overlays(self, duration_ms=2000):
    """Show the persistent overlays for duration_ms milliseconds and hide them."""
    if not hasattr(self, "_screen_overlays") or not self._screen_overlays:
        # Lazy-create if needed
        try:
            self.create_overlays()
        except Exception as e:
            print(f"Error creating overlays on demand: {e}")
            return

    for screen, overlay in list(self._screen_overlays.items()):
        try:
            # Re-assert assigned Screen (some compositors only honor setScreen when mapping)
            try:
                assigned = getattr(overlay, "_assigned_qscreen", None)
                if assigned and overlay.windowHandle():
                    try:
                        overlay.windowHandle().setScreen(assigned)
                    except Exception as e:
                        print(
                            f"Warning: could not setScreen on show for {screen}: {e}"
                        )
            except Exception:
                pass

            # Show overlay and force a short repaint; then log diagnostic info
            overlay.show()
            overlay.raise_()
            QApplication.processEvents()
            try:
                handle = overlay.windowHandle()
                mapped_screen = None
                if handle and handle.screen():
                    try:
                        mapped_screen = handle.screen().name()
                    except Exception:
                        mapped_screen = str(handle.screen().geometry())
                print(
                    f"Shown overlay for {screen}: visible={overlay.isVisible()}, mapped_screen={mapped_screen}, geom={overlay.geometry()}"
                )
            except Exception as e:
                print(f"Overlay diagnostic error for {screen}: {e}")

            # schedule hide
            QTimer.singleShot(duration_ms, overlay.hide)
        except Exception as e:
            print(f"Error showing overlay for {screen}: {e}")
