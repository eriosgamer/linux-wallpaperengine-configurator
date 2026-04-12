#!/usr/bin/env python3
import json
import keyword
import os
import re
import shutil
import subprocess
import sys

# Force UTF-8
os.environ["PYTHONIOENCODING"] = "utf-8"


# Check dependencies: PySide6 and others
def check_and_install_dependencies():
    missing_packages = []
    try:
        import psutil
    except ImportError:
        print("psutil is not installed. Install it with: pip install --user psutil")
        missing_packages.append("psutil")
    try:
        from PIL import Image
    except ImportError:
        print("Pillow is not installed. Install it with: pip install --user pillow")
        missing_packages.append("pillow")
    try:
        import qdarktheme
    except ImportError:
        print("qdarktheme missing, Install it with pip install --user PyQtDarkTheme")
    try:
        import requests
    except ImportError:
        print("requests is not installed. Install it with: pip install --user requests")
        missing_packages.append("requests")
    try:
        from PySide6.QtWidgets import QApplication
    except ImportError:
        print("PySide6 is not installed. Install it with: pip install --user PySide6")
        missing_packages.append("PySide6")
    # ...linux-wallpaperengine check as before...
    wallpaperengine_path = shutil.which("linux-wallpaperengine")
    wallpaperengine_running = False
    try:
        import psutil

        for proc in psutil.process_iter(["name"]):
            if proc.info["name"] and "linux-wallpaperengine" in proc.info["name"]:
                wallpaperengine_running = True
                break
    except Exception:
        pass
    if (
            not wallpaperengine_path
            and not wallpaperengine_running
            and not os.path.exists("/opt/linux-wallpaperengine")
    ):
        print("Error: Linux Wallpaper Engine is not installed or not in PATH.")
        missing_packages.append("linux-wallpaperengine")
    if missing_packages:
        print("\nMissing dependencies. Install with:")
        for pkg in missing_packages:
            print(f"pip install --user {pkg}")
        if "linux-wallpaperengine" in missing_packages:
            print("https://github.com/Almamu/linux-wallpaperengine")
        sys.exit(1)


check_and_install_dependencies()

from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QLineEdit,
    QMainWindow,
    QSpinBox,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QPushButton,
    QListWidget,
    QListWidgetItem,
    QTextEdit,
    QMessageBox,
    QGroupBox,
    QDialog,
    QScrollArea,
)
from PySide6.QtGui import QPixmap, QFont, QLinearGradient
from PySide6.QtCore import Qt, QTimer, QRectF
from PIL import Image
import psutil
from typing import Optional, Dict
import qdarktheme


class WallpaperConfigQt(QMainWindow):
    def __init__(self):
        self.screen_configs = {}
        qdarktheme.setup_theme("dark")
        super().__init__()
        self.setWindowTitle("Linux-WallpaperEngine Configuration (Qt)")
        self.setGeometry(100, 100, 1200, 800)
        icon_base64 = "iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAA7AAAAOwBeShxvQAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAUmSURBVFiFvZZbbFRVFIa/fS4zZ9q5dtpOx7ZYKlWuJZZLEQPRQFAiRIygcjEkQIwRJBLlogkaolUTwxv1waARLEZACWKlQDSEYAxBimBahEIpAr0IbaedMtO5nuMDUGg7HdpS+ZPzcM7+915f1j577SVIrhzNYquMREJOhKTfw9svGfGoZBj6cKABQEniTbc73JWKImcWzCzB7h3fy6DHIwSaa4jHwncFiHR7BxCAa9gUgm3/cKbi3UC0s+UJ4Ccg0heA3enKrFy7bm3mvvL9BBMYop0+ag+tpCBPw25VQYAi6ciyRKrThCrHwRBEdQlFFqxa0sCP+y/imZqmtrcqX/x9wef3d0SKRIK1LS63p3L58mUjN76/URQWFpFRvAmzLaubqfGvMl4oOsmHGyYkSWLfevuD38Nby85skHp8V1xuz+HOYMeoqupz4uOSj2hr82G2ebqZQv56gk3HGDfKMajgAOPHuM3WFPWxnlswLhDSx+U/uZ7Lego1h2vIGv8qN3cRMHRu1Gyjte4ImhQjzZk7aACXw4yqSJk9MyCZLO6QO/8pXLmT8RYuIb1gbtegv+5nnNIVSj/fQiQSIxyKDRogEo4jSVKfP2FCXaveyeZvvmbBSwvRrBn460NYWgd3Ov0NnYDR3G+AeCSAQOdi7UVcuVPRPBPZuncLUwozyXJbELd2KdWiYlK7JzYciRO8lS1dh8bmIF/urYk1XQ+W9xtAyCb8/nayc3IJ+Wp5aNKbtIWuMOedCjoDN7p8wWAIwzB6zTeZVFRVoaWl3chwa9f0OJuBg/0GkGQVz/ApnKis5Llnp7Nnz1KsrmyQvaj2Oz6HHYSkoNjzyRj9MorZ1m2d9p1L2hr+vTINOA/JK2EvpY9/ndLSNSxe9Apl27eSarUiRO9SEo1GqThwgO071lIwuxQhyX2uOSAAU2oG+c9sofzot3y3ayUdbc0JfYahU/LpJ+Rmuwk012DNHDU0AACq5iSr6I0+xwPN57l24RB7du8GI07LpaNIipmUtPyE/p514L4U9NVxtWINk64fx1vfREFbOxN8lVzc/xYhf0PCOQPOQDIJScUAbsSiyIEoQggMBAYSQkocakgzYHHkkDFtPa3RMPO8eczzPszVUIjcp97DbM38/wEAZEXDZdJ42pvFDK8Xm2ZFUix9+occ4KYEGIlu+gcGAEL0roYPFCBBNX5QAALDMLoqpEFykiE9hgAprjxOdfgoOVsFQnDW72NkksZlyAFMqenkzS3lt6snQAhGTJyMqjnvDSDL6lLFnLI66Kt1/rlrUZchfdhEHp26jGO7VqPrA++AGqu+R9UcZIyYiXfs/MQAmsWxw+EZPqd49mq7LS27m0FLdWDSbHhXfYUe7y+AwS9lG7hef4ZhxSvQbFk0nN4FonfCFWCGxZ4+Z96q7XYpybVpdWb1OdZTtacP0txwDtewYtJHTAcgu2ghDad+6OWVVHPK84XTFtuSBR+o6qqO4B07n5C/kdS0HKzpeeiRG2hWTy+vIiQlTVa1/pWtfkqPRQj6agn5G/lj2xIszhyCrZcYM3szp/a8pgBdPZwS6fSXVx/ft8D6yCzTUAFYsx+n6epORkxfB4CqObBljibQcgHDiLUBjbe9MlBt6LEFvmuXPCZ3ATGhEY7p9/WY0/K5fvYAkiyTUTALiyOH9vqTnP11kz8e7ngRuHwb4HbqzRa757NYJLTc0CNmkPpZSO+SQMCdBtHQYyIeDQkASVbDkmI5Ewv7VwAn7572H1Aa8kcV7uKbAAAAAElFTkSuQmCC"
        # Converts the base64 string to a QIcon
        from PySide6.QtGui import QIcon

        if icon_base64:
            import base64

            icon_data = base64.b64decode(icon_base64)
            icon_image = QPixmap()
            icon_image.loadFromData(icon_data)
            self.setWindowIcon(QIcon(icon_image))

        # Initialization logic as before
        self.wallpaper_base_path = self.find_wallpaper_directory()
        if not self.wallpaper_base_path:
            QMessageBox.critical(
                self,
                "Error",
                "Wallpaper directory not found. Make sure you have Steam Workshop content installed.",
            )
            sys.exit(1)
        self.script_path = self.get_script_path()
        self.desktop_path = self.get_desktop_path()
        self.detected_screens = self.detect_screens()
        self.wallpapers: Dict[str, dict] = {}
        self.selected_wallpapers: Dict[str, Optional[str]] = {}
        self.current_selection: Optional[str] = None
        for screen in self.detected_screens:
            self.selected_wallpapers[screen] = None
        # Create persistent per-screen overlays (used by Identify Monitors)
        # These are created once and then shown/hidden to improve compatibility with Wayland compositors
        try:
            self.create_overlays()
        except Exception as e:
            print(f"Warning: could not create overlays at init: {e}")
        # Main UI
        self.setup_ui()
        self.load_wallpapers()
        self.ensure_required_files()

    def load_wallpapers(self):
        """
        Scan the wallpaper directory and populate self.wallpapers with available wallpapers.
        """
        self.wallpapers.clear()
        if not os.path.exists(self.wallpaper_base_path):
            print(f"Wallpaper directory does not exist: {self.wallpaper_base_path}")
            return
        for wid in os.listdir(self.wallpaper_base_path):
            wpath = os.path.join(self.wallpaper_base_path, wid)
            if os.path.isdir(wpath):
                self.load_wallpaper_info(wid, wpath)
        # Optionally update the UI list if needed
        if hasattr(self, "wallpaper_list"):
            self.wallpaper_list.clear()
            sorted_wallpapers = sorted(
                self.wallpapers.items(), key=lambda x: x[1]["title"].lower()
            )
            for wallpaper_id, info in sorted_wallpapers:
                # Detect CJK characters in the title
                def highlight_cjk(text):
                    # Regex for CJK Unified Ideographs
                    def repl(m):
                        return f'<span style="color:blue;">{m.group(0)}</span>'

                    return re.sub(
                        r"[\u4e00-\u9fff\u3040-\u30ff\u3400-\u4dbf\uac00-\ud7af]+",
                        repl,
                        text,
                    )

                title_html = highlight_cjk(info["title"])
                display_text = f"{title_html} (ID: {wallpaper_id})"
                item = QListWidgetItem()
                if not info.get("supported", True):
                    reason = info.get("unsupported_reason", "")
                    html = (
                        f"{title_html} (ID: {wallpaper_id}) "
                        f'<span style="color:red;">[NOT SUPPORTED:</span> '
                        f'<span style="color:orange;">{reason}</span>'
                        f'<span style="color:red;">]</span>'
                    )
                    item.setData(Qt.ItemDataRole.DisplayRole, "")
                    item.setData(Qt.ItemDataRole.UserRole, html)
                else:
                    item.setData(Qt.ItemDataRole.UserRole, display_text)
                self.wallpaper_list.addItem(item)
            # Set rich text for all items
            for i in range(self.wallpaper_list.count()):
                item = self.wallpaper_list.item(i)
                html = item.data(Qt.ItemDataRole.UserRole)
                if html:
                    label = QLabel()
                    label.setTextFormat(Qt.TextFormat.RichText)
                    label.setText(html)
                    self.wallpaper_list.setItemWidget(item, label)
        # After wallpapers are loaded, load config and update UI
        self.load_current_config()
        self.update_screen_status()

    def load_current_config(self):
        """
        Load the current wallpaper configuration for each screen, if available.
        This method should set self.selected_wallpapers for each detected screen.
        """
        config_path = os.path.expanduser("~/.config/wallpaperengine_config.json")
        if os.path.exists(config_path):
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    config = json.load(f)
                for screen in self.detected_screens:
                    wallpaper_id = config.get(screen)
                    # Only assign if the wallpaper exists in self.wallpapers or is None
                    if wallpaper_id is None or wallpaper_id in self.wallpapers:
                        self.selected_wallpapers[screen] = wallpaper_id
                    else:
                        self.selected_wallpapers[screen] = None
            except Exception as e:
                print(f"Error loading config: {e}")
        else:
            # No config file, set all to None
            for screen in self.detected_screens:
                self.selected_wallpapers[screen] = None

    def find_wallpaper_directory(self):
        """Automatically find the Steam wallpapers directory"""
        possible_paths = [
            f"/home/{os.getenv('USER')}/.local/share/Steam/steamapps/workshop/content/431960",
            f"/home/{os.getenv('USER')}/.steam/steamapps/workshop/content/431960",
            "/usr/share/steam/steamapps/workshop/content/431960",
            "/opt/steam/steamapps/workshop/content/431960",
        ]

        for path in possible_paths:
            if os.path.exists(path) and os.path.isdir(path):
                print(f"Wallpapers directory found: {path}")
                return path

        # If not found, use find as a last resort
        try:
            result = subprocess.run(
                [
                    "find",
                    "/home",
                    "/opt",
                    "/usr",
                    "-name",
                    "431960",
                    "-type",
                    "d",
                    "2>/dev/null",
                ],
                capture_output=True,
                text=True,
                timeout=10,
            )

            for line in result.stdout.strip().split("\n"):
                if line and "workshop/content/431960" in line:
                    if os.path.exists(line) and os.path.isdir(line):
                        print(f"Wallpapers directory found with find: {line}")
                        return line
        except:
            pass

        # Fallback to default path
        default_path = f"/home/{os.getenv('USER')}/.local/share/Steam/steamapps/workshop/content/431960"
        print(f"Using default directory: {default_path}")
        return default_path

    def get_screen_detection_method(self):
        """Detect which monitor listing methods are available on the system"""
        import shutil

        # Priority: xrandr, wlr-randr, swaymsg
        if shutil.which("xrandr"):
            return "xrandr"
        elif shutil.which("wlr-randr"):
            return "wlr-randr"
        elif shutil.which("swaymsg"):
            return "swaymsg"
        else:
            return None

    def detect_screens(self):
        """Automatically detect connected screens using available methods"""
        screens = []
        method = self.get_screen_detection_method()
        print(f"Screen detection method: {method}")

        try:
            if method == "xrandr":
                # Use xrandr to detect connected screens
                result = subprocess.run(
                    ["xrandr", "--listmonitors"], capture_output=True, text=True
                )
                print(f"xrandr --listmonitors output:\n{result.stdout}")
                for line in result.stdout.split("\n"):
                    line = line.strip()
                    if not line or line.startswith("Monitors:"):
                        continue
                    if ":" in line and "+" in line:
                        parts = line.split()
                        if len(parts) >= 2:
                            monitor_name = parts[-1]
                            if (
                                    monitor_name
                                    and not monitor_name.startswith("+")
                                    and monitor_name not in ["Monitors:", ""]
                            ):
                                monitor_name = monitor_name.strip("*+")
                                if monitor_name and monitor_name not in screens:
                                    screens.append(monitor_name)
                                    print(f"Monitor detected: {monitor_name}")
                # Fallback to xrandr --query if none found
                if not screens:
                    print("No screens detected with --listmonitors, trying --query...")
                    result = subprocess.run(
                        ["xrandr", "--query"], capture_output=True, text=True
                    )
                    for line in result.stdout.split("\n"):
                        if " connected" in line:
                            screen_name = line.split()[0]
                            if screen_name and screen_name not in screens:
                                screens.append(screen_name)
                                print(f"Monitor detected with --query: {screen_name}")

            elif method == "wlr-randr":
                # Use wlr-randr to list outputs
                result = subprocess.run(["wlr-randr"], capture_output=True, text=True)
                print(f"wlr-randr output:\n{result.stdout}")
                for line in result.stdout.split("\n"):
                    if " connected" in line or line.startswith("Output "):
                        # Example: Output HDMI-A-1 (connected)
                        parts = line.split()
                        if len(parts) >= 2:
                            screen_name = parts[1]
                            if screen_name and screen_name not in screens:
                                screens.append(screen_name)
                                print(f"Monitor detected with wlr-randr: {screen_name}")

            elif method == "swaymsg":
                # Use swaymsg to list outputs
                result = subprocess.run(
                    ["swaymsg", "-t", "get_outputs"], capture_output=True, text=True
                )
                print(f"swaymsg output:\n{result.stdout}")
                import json

                try:
                    outputs = json.loads(result.stdout)
                    for output in outputs:
                        if output.get("active"):
                            screen_name = output.get("name")
                            if screen_name and screen_name not in screens:
                                screens.append(screen_name)
                                print(f"Monitor detected with swaymsg: {screen_name}")
                except Exception as e:
                    print(f"Error parsing swaymsg output: {e}")

            else:
                print("No supported screen detection method found.")
                sys.exit(1)

            # Filter out virtual or unwanted screens
            original_screens = screens.copy()
            screens = [
                s
                for s in screens
                if not any(
                    x in s.lower()
                    for x in ["virtual", "none", "disconnected", "unknown"]
                )
            ]
            if len(screens) != len(original_screens):
                filtered_out = set(original_screens) - set(screens)

        except Exception as e:
            print(f"Error detecting screens: {e}")
            sys.exit(1)

        if not screens:
            print("No screens detected.")
            sys.exit(1)

        screens.sort()
        print(f"Final detected screens: {screens}")
        return screens

    def get_script_path(self):
        """Get the wallpaper engine script path"""
        # Create .local/bin directory if it doesn't exist
        bin_dir = f"/home/{os.getenv('USER')}/.local/bin"
        os.makedirs(bin_dir, exist_ok=True)
        return os.path.join(bin_dir, "start-wallpaperengine.sh")

    def get_desktop_path(self):
        """Get the .desktop file path for autostart"""
        # Create .config/autostart directory if it doesn't exist
        autostart_dir = f"/home/{os.getenv('USER')}/.config/autostart"
        os.makedirs(autostart_dir, exist_ok=True)
        return os.path.join(autostart_dir, "start-wallpaperengine.sh.desktop")

    def ensure_required_files(self):
        """Check and create required files if they don't exist"""
        files_created = []

        # Always create the script if it does not exist
        if not os.path.exists(self.script_path):
            self.create_wallpaper_script()
            files_created.append("Linux Wallpaper Engine script")

        # Do NOT create the .desktop file automatically
        # Autostart is only created/destroyed from the configuration menu

        # Show info if any file was created
        if files_created:
            files_list = "\n• ".join(files_created)
            # Show an informational dialog using Qt after the event loop starts
            QTimer.singleShot(
                0,
                lambda: QMessageBox.information(
                    self,
                    "Initial Setup",
                    f"The following files have been created:\n\n• {files_list}\n\n"
                    f"Linux Wallpaper Engine script is ready.",
                ),
            )

    def clear_log(self):
        log_file = "/tmp/wallpaper-engine.log"
        try:
            if not os.path.exists(log_file):
                QMessageBox.information(self, "Logs", "No log file found yet.")
                return
            open(log_file, "w").close()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error reading log: {e}")

    def create_wallpaper_script(self):
        """Create the wallpaper engine script dynamically for assigned screens"""
        # Only include screens with assigned wallpapers
        assigned = [
            (screen, self.selected_wallpapers.get(screen))
            for screen in getattr(self, "detected_screens", [])
        ]
        assigned = [(screen, wid) for screen, wid in assigned if wid is not None]

        # If no wallpapers assigned, fallback to all screens with default paths
        if not assigned:
            screens = getattr(self, "detected_screens", ["HDMI-A-1", "DP-1"])
            assigned = [(screen, None) for screen in screens]

        script_content = "#!/bin/bash\n\n"
        script_content += "# Automatically generated file by wallpaper-config.py\n"
        script_content += "# Do not edit manually - changes will be overwritten\n\n"
        script_content += "# Create log file if it doesn't exist\n"
        script_content += 'LOG_FILE="/tmp/wallpaper-engine.log"\ntouch "$LOG_FILE"\n\n'
        script_content += (
            'echo "$(date): Starting Wallpaper Engine..." >> "$LOG_FILE"\n\n'
        )
        script_content += "# Wait for the system to be ready\nsleep 5\n\n"

        # Dynamically define WALLPAPER# variables
        for idx, (screen, wid) in enumerate(assigned, 1):
            if wid is not None:
                wallpaper_path = os.path.join(self.wallpaper_base_path, wid)
            else:
                wallpaper_path = f"/path/to/default/wallpaper{idx}"
            script_content += f'WALLPAPER{idx}="{wallpaper_path}"\n'

        script_content += "\n# Check that wallpapers exist\n"
        for idx, (screen, wid) in enumerate(assigned, 1):
            script_content += f'if [[ ! -d "$WALLPAPER{idx}" ]]; then\n'
            script_content += f'    echo "$(date): Error: Wallpaper for screen not configured yet. Use wallpaper-config.py to configure." >> "$LOG_FILE"\n'
            script_content += f"    exit 1\nfi\n"

        # Clean up previous processes
        script_content += "# Clean up previous processes\npkill -f linux-wallpaperengine 2>/dev/null\n\n"
        script_content += "# Environment variables for stability\n"
        script_content += (
            "export LD_LIBRARY_PATH=/opt/linux-wallpaperengine:$LD_LIBRARY_PATH\n"
        )
        script_content += "export __GL_THREADED_OPTIMIZATIONS=0\n"
        script_content += 'export PULSE_RUNTIME_PATH="/run/user/$(id -u)/pulse"\n\n'
        script_content += 'echo "$(date): Running with wallpapers:" >> "$LOG_FILE"\n'
        for idx, screen in enumerate(self.detected_screens, 1):
            script_content += f'echo "  {screen}: $WALLPAPER{idx}" >> "$LOG_FILE"\n'

        # Build the linux-wallpaperengine command dynamically
        script_content += "\n# Run wallpaper engine\nlinux-wallpaperengine\\\n"
        for idx, (screen, _) in enumerate(assigned, 1):
            cs = self.screen_configs.get(screen, {})
            scaling = cs.get("scaling", "fill")
            script_content += f" --scaling {scaling} \\\n --screen-root {screen} \\\n --bg \"$WALLPAPER{idx}\" \\\n"

        # Use defaults for global options
        base_defaults = {
            "fps": 30,
            "volume": 15,
            "silent": True,
            "noautomute": False,
            "no_audio_proc": False,
            "mouse": True,
            "parallax": True,
            "fs_pause": True,
            "clamp": "border",
        }

        # Try to get config from the first assigned screen if available
        if assigned:
            first_screen = assigned[0][0]
            c = base_defaults.copy()
            c.update(self.screen_configs.get(first_screen, {}))
        else:
            c = base_defaults

        if c["silent"]:
            script_content += " --silent \\\n"
        else:
            script_content += f" --volume {c['volume']} \\\n"

        if c["noautomute"]:
            script_content += " --noautomute \\\n"

        if c["no_audio_proc"]:
            script_content += " --no-audio-processing \\\n"

        if not c["mouse"]:
            script_content += " --disable-mouse \\\n"

        if c.get("clamp"):
            script_content += f" --clamp {c['clamp']} \\\n"

        if not c["parallax"]:
            script_content += " --disable-parallax \\\n"

        if not c["fs_pause"]:
            script_content += " --no-fullscreen-pause \\\n"

        script_content += f" --fps {c['fps']} \\\n"

        script_content += '2>&1 | tee -a "$LOG_FILE"\n'

        try:
            with open(self.script_path, "w") as f:
                f.write(script_content)
            os.chmod(self.script_path, 0o755)
            print(f"Script created: {self.script_path}")
        except Exception as e:
            print(f"Error creating script: {e}")

    def create_desktop_file(self):
        """Create the .desktop file for autostart"""
        desktop_content = f"""[Desktop Entry]
Type=Application
Name=Wallpaper Engine
Comment=Automatically starts Linux-WallpaperEngine at system startup
Exec={self.script_path}
Icon=preferences-desktop-wallpaper
Terminal=false
Hidden=false
X-GNOME-Autostart-enabled=true
StartupNotify=false
Categories=Graphics;Settings;
"""

        try:
            with open(self.desktop_path, "w") as f:
                f.write(desktop_content)

            print(f"Desktop file created: {self.desktop_path}")

        except Exception as e:
            print(f"Error creating desktop file: {e}")

    def setup_fonts(self):
        """Configure fonts that support Unicode/CJK characters in Qt."""
        # List of fonts that typically support CJK
        font_candidates = [
            "Noto Sans CJK SC",  # Specific for Simplified Chinese
            "Noto Sans CJK TC",  # Specific for Traditional Chinese
            "Noto Sans CJK JP",  # Specific for Japanese
            "Noto Sans CJK",
            "Noto Nerd",
            "Source Han Sans",
            "WenQuanYi Micro Hei",
            "DejaVu Sans",
            "Liberation Sans",
            "Arial Unicode MS",
            "Unifont",
            "FreeSans",
            "Arial",
        ]

        from PySide6.QtGui import QFontDatabase

        available_fonts = QFontDatabase().families()
        self.unicode_font = None

        for font_name in font_candidates:
            if font_name in available_fonts:
                self.unicode_font = font_name
                break

        # Fallback: force Unifont if no CJK font found
        if not self.unicode_font:
            print("Available fonts:", available_fonts)
            if "Unifont" in available_fonts:
                self.unicode_font = "Unifont"
            elif "Arial" in available_fonts:
                self.unicode_font = "Arial"
                print("Warning: No CJK font found. Using Arial as fallback.")
            else:
                self.unicode_font = QFontDatabase.systemFont(
                    QFontDatabase.SystemFont.GeneralFont
                ).family()
                print(
                    "Warning: No CJK/Arial/Unifont font found. Using system default font."
                )

        print(f"Using font: {self.unicode_font}")

    def setup_ui(self):
        # Remove previous widgets if they exist
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)

        # Title
        title = QLabel(
            f"Wallpaper Configurator - {len(self.detected_screens)} screen(s) detected"
        )
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        main_layout.addWidget(title)

        # System info
        info_lines = [
            f"Directory: {self.wallpaper_base_path}",
            f"Screens: {', '.join(self.detected_screens)}",
            f"Script: {self.script_path}",
            f"Autostart: {'Configured' if os.path.exists(self.desktop_path) else 'Not configured'}",
        ]
        info_label = QLabel("\n".join(info_lines))
        info_label.setStyleSheet("color: gray; font-size: 10px;")
        main_layout.addWidget(info_label)

        # Top utility panel
        util_layout = QHBoxLayout()
        btn_identify = QPushButton("Identify Monitors")
        btn_identify.clicked.connect(self.identify_monitors)
        util_layout.addWidget(btn_identify)
        btn_refresh = QPushButton("Refresh List")
        btn_refresh.clicked.connect(self.load_wallpapers)
        util_layout.addWidget(btn_refresh)
        btn_script = QPushButton("View Script")
        btn_script.clicked.connect(self.view_script)
        util_layout.addWidget(btn_script)
        btn_autostart = QPushButton("Config Autostart")
        btn_autostart.clicked.connect(self.manage_autostart)
        util_layout.addWidget(btn_autostart)
        btn_logs = QPushButton("View Logs")
        btn_logs.clicked.connect(self.view_logs)
        util_layout.addWidget(btn_logs)
        main_layout.addLayout(util_layout)

        # Central panel (wallpapers and preview)
        content_layout = QHBoxLayout()
        # Wallpaper list
        self.wallpaper_list = QListWidget()
        self.wallpaper_list.itemSelectionChanged.connect(self.on_wallpaper_select)
        content_layout.addWidget(self.wallpaper_list, 2)
        # Right panel: preview and info
        right_panel = QVBoxLayout()
        self.preview_label = QLabel("Select a wallpaper")
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setFixedSize(320, 180)
        right_panel.addWidget(self.preview_label)
        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        right_panel.addWidget(self.info_text)
        content_layout.addLayout(right_panel, 1)
        main_layout.addLayout(content_layout)

        # Bottom panel: assignment and status
        bottom_layout = QHBoxLayout()
        # Assign wallpapers to screens
        assign_group = QGroupBox("Assign to screen")
        assign_layout = QGridLayout()
        for idx, screen in enumerate(self.detected_screens):
            btn_assign = QPushButton(f">> {screen}")
            btn_assign.clicked.connect(
                lambda checked, s=screen: self.assign_and_apply(s)
            )
            assign_layout.addWidget(btn_assign, idx, 0)

            btn_unassign = QPushButton("Unassign")
            btn_unassign.clicked.connect(
                lambda checked, s=screen: self.unassign_wallpaper(s)
            )
            assign_layout.addWidget(btn_unassign, idx, 1)

            btn_config = QPushButton("Config")
            btn_config.clicked.connect(
                lambda checked, s=screen: self.config_wallpaper(s)
            )
            assign_layout.addWidget(btn_config, idx, 2)

            btn_properties = QPushButton("Properties")
            btn_properties.clicked.connect(
                lambda checked, s=screen: self.wallpaper_property_setup(s)
            )
            assign_layout.addWidget(btn_properties, idx, 3)

        assign_group.setLayout(assign_layout)
        bottom_layout.addWidget(assign_group)
        # Current status
        status_group = QGroupBox("Current status")
        self.status_labels = {}
        status_layout = QVBoxLayout()
        for screen in self.detected_screens:
            lbl = QLabel(f"{screen}: Not assigned")
            lbl.setStyleSheet("color: gray;")
            status_layout.addWidget(lbl)
            self.status_labels[screen] = lbl
        status_group.setLayout(status_layout)
        bottom_layout.addWidget(status_group)
        main_layout.addLayout(bottom_layout)

    def on_wallpaper_select(self, event=None):
        """Handle wallpaper selection in the list (Text widget version)"""
        # Get the index of the current selection in the Text widget
        try:
            # Get the current cursor position
            index = self.wallpaper_list.currentRow()
            sorted_wallpapers = sorted(
                self.wallpapers.items(), key=lambda x: x[1]["title"].lower()
            )
            if index >= 0 and index < len(sorted_wallpapers):
                wallpaper_id, wallpaper_info = sorted_wallpapers[index]
                self.current_selection = wallpaper_id
            else:
                self.current_selection = None
                return
        except Exception:
            self.current_selection = None
            return

        # Update preview with larger size
        if wallpaper_info["preview"]:
            try:
                image = Image.open(wallpaper_info["preview"])
                # If GIF, show first frame (Pillow handles animated GIFs)
                if getattr(image, "is_animated", False):
                    image.seek(0)
                image.thumbnail((300, 170), Image.Resampling.LANCZOS)
                from PySide6.QtGui import QImage, QPixmap

                image = image.convert("RGBA")
                data = image.tobytes("raw", "RGBA")
                qimage = QImage(
                    data, image.width, image.height, QImage.Format.Format_RGBA8888
                )
                pixmap = QPixmap.fromImage(qimage)
                self.preview_label.setPixmap(pixmap)
                self.preview_label.setText("")
                self._preview_photo = pixmap
            except Exception as e:
                print(f"Error loading preview image: {e}")
                from PySide6.QtGui import QPixmap

                self.preview_label.setPixmap(QPixmap())
                self.preview_label.setText("No preview")
        else:
            # Try loading preview from Steam Workshop if not found locally
            try:
                import requests

                steam_preview_url = f"https://steamcommunity.com/sharedfiles/filedetails/?id={wallpaper_id}"
                resp = requests.get(steam_preview_url, timeout=5)
                if resp.ok:
                    import re

                    match = re.search(
                        r'<img[^>]+id="previewImageMain"[^>]+src="([^"]+)"', resp.text
                    )
                    if match:
                        img_url = match.group(1)
                        from io import BytesIO

                        img_resp = requests.get(img_url, timeout=5)
                        if img_resp.ok:
                            try:
                                image = Image.open(BytesIO(img_resp.content))
                                # If GIF, show first frame (Pillow handles animated GIFs)
                                if getattr(image, "is_animated", False):
                                    print(
                                        "No local preview found. Loading from Steam workshop."
                                    )
                                    image.seek(0)
                                image.thumbnail((300, 170), Image.Resampling.LANCZOS)
                                from PySide6.QtGui import QImage, QPixmap

                                image = image.convert("RGBA")
                                data = image.tobytes("raw", "RGBA")
                                qimage = QImage(
                                    data,
                                    image.width,
                                    image.height,
                                    QImage.Format.Format_RGBA8888,
                                )
                                pixmap = QPixmap.fromImage(qimage)
                                self.preview_label.setPixmap(pixmap)
                                self.preview_label.setText("")
                                self._preview_photo = pixmap
                            except Exception as e:
                                print(f"Error loading preview image: {e}")
                                from PySide6.QtGui import QPixmap

                                self.preview_label.setPixmap(QPixmap())
                                self.preview_label.setText("No preview")
                        else:
                            from PySide6.QtGui import QPixmap

                            self.preview_label.setPixmap(QPixmap())
                            self.preview_label.setText("No preview")
                    else:
                        from PySide6.QtGui import QPixmap

                        self.preview_label.setPixmap(QPixmap())
                        self.preview_label.setText("No preview")
                else:
                    print(f"Error fetching preview from Steam: {resp.status_code}")
                    from PySide6.QtGui import QPixmap

                    self.preview_label.setPixmap(QPixmap())
                    self.preview_label.setText("No preview")
            except Exception:
                from PySide6.QtGui import QPixmap

                self.preview_label.setPixmap(QPixmap())
                self.preview_label.setText("No preview")

        # Update info WITHOUT processing the text
        title = wallpaper_info["title"]
        info_text = f"Title: {title}\n\nID: {wallpaper_id}"

        # Check wallpaper type
        wallpaper_path = wallpaper_info["path"]
        try:
            if os.path.exists(os.path.join(wallpaper_path, "scene.pkg")):
                info_text += "\n\nType: Animated Wallpaper"
            elif any(
                    f.endswith((".mp4", ".webm", ".avi"))
                    for f in os.listdir(wallpaper_path)
                    if os.path.isfile(os.path.join(wallpaper_path, f))
            ):
                info_text += "\n\nType: Video"
            else:
                info_text += "\n\nType: Static Image"
        except:
            info_text += "\n\nType: Unknown"

        # Add description as is
        if wallpaper_info["description"]:
            description = wallpaper_info["description"]
            if len(description) > 200:
                description = description[:200] + "..."
            info_text += f"\n\nDescription:\n{description}"

        # Use the method to update text
        self.update_info_text(info_text)

    def update_info_text(self, text):
        """
        Update the info_text QTextEdit widget with the provided text.
        """
        if hasattr(self, "info_text"):
            self.info_text.setPlainText(text)

    def is_wallpaper_supported(self, wallpaper_path):
        """
        Analyze the wallpaper and determine if it is suitable for linux-wallpaperengine.
        Based on https://github.com/Almamu/linux-wallpaperengine and common errors.
        """
        project_json = os.path.join(wallpaper_path, "project.json")
        if not os.path.exists(project_json):
            return False, "No project.json"

        try:
            with open(project_json, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            return False, "Error reading project.json"

        wallpaper_type = data.get("type", "").lower()
        # Basic type check
        if wallpaper_type == "scene":
            if not (
                    os.path.exists(os.path.join(wallpaper_path, "scene.json"))
                    or os.path.exists(os.path.join(wallpaper_path, "scene.pkg"))
            ):
                return False, "Missing scene.json/scene.pkg"
        elif wallpaper_type == "video":
            if not any(
                    f.endswith(ext)
                    for ext in (".mp4", ".webm", ".avi")
                    for f in os.listdir(wallpaper_path)
            ):
                return False, "Missing video file"
        elif wallpaper_type == "web":
            if not (
                    os.path.exists(os.path.join(wallpaper_path, "scene.json"))
                    or os.path.exists(os.path.join(wallpaper_path, "scene.pkg"))
            ):
                return False, "Missing scene.json/scene.pkg"
        elif not wallpaper_type:
            return False, "No type specified in project.json"
        else:
            return False, f"Type '{wallpaper_type}' not supported"

        # Advanced check for problematic properties
        general = data.get("general")
        if isinstance(general, dict):
            props = general.get("properties", {})
        else:
            props = {}
        for key, prop in props.items():
            # Detect properties of type scenetexture
            if isinstance(prop, dict) and prop.get("type", "") == "scenetexture":
                return False, f"Property '{key}' type scenetexture not supported"
            # Detect unsupported animations
            if isinstance(prop, dict) and "animation" in prop.get("type", "").lower():
                return False, f"Property '{key}' with unsupported animation"
            # Detect composed materials
            if "material" in key.lower() and "compose" in prop.get("type", "").lower():
                return False, f"Composed material not supported ({key})"

        # Check shader files for common errors
        for fname in os.listdir(wallpaper_path):
            if fname.endswith((".frag", ".vert", ".glsl")):
                shader_path = os.path.join(wallpaper_path, fname)
                try:
                    with open(shader_path, "r", encoding="utf-8", errors="ignore") as f:
                        shader_code = f.read()
                        # Look for common error patterns
                        if (
                                "cannot convert" in shader_code
                                or "syntax error" in shader_code
                        ):
                            return False, f"Incompatible shader: {fname}"
                except Exception:
                    continue

        # Check required keys in particle emitters
        if "scene.json" in os.listdir(wallpaper_path):
            try:
                with open(
                        os.path.join(wallpaper_path, "scene.json"), "r", encoding="utf-8"
                ) as f:
                    scene_data = f.read()
                    if "Particle emitter" in scene_data and "origin" not in scene_data:
                        return (
                            False,
                            "Particle emitter without 'origin' (not supported)",
                        )
            except Exception:
                pass

        # If everything is OK
        return True, ""

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

    def wallpaper_property_setup(self, screen):
        """Open a dialog to configure properties of the assigned wallpaper for a specific screen"""
        wallpaper_id = self.selected_wallpapers.get(screen)
        if not wallpaper_id:
            QMessageBox.warning(self, "No wallpaper assigned",
                                f"No wallpaper assigned to {screen}. Please assign one first.")
            return

        wallpaper_info = self.wallpapers.get(wallpaper_id)
        if not wallpaper_info:
            QMessageBox.warning(self, "Wallpaper not found", f"Wallpaper info not found for ID: {wallpaper_id}")
            return

        # Ensure screen_configs entry exists with defaults
        if screen not in self.screen_configs:
            file_configs = self.load_config_from_script()
            if screen in file_configs:
                self.screen_configs[screen] = file_configs[screen]
            else:
                self.screen_configs[screen] = {
                    "fps": 30,
                    "volume": 15,
                    "silent": True,
                    "scaling": "fill",
                    "noautomute": False,
                    "no_audio_proc": False,
                    "clamp": "border",
                    "mouse": True,
                    "parallax": True,
                    "fs_pause": True,
                }

        base_properties = self.load_wallpaper_properties(wallpaper_id)

        saved_props = self.screen_configs.get(screen, {}).get("properties", {})
        if not isinstance(saved_props, dict):
            saved_props = {}

        # Create a dialog to show properties
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Properties: {wallpaper_info['title']}")
        dialog.resize(600, 700)

        main_vlayout = QVBoxLayout(dialog)

        # Scroll Area Setup
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        form_layout = QFormLayout(scroll_content)
        scroll.setWidget(scroll_content)

        main_vlayout.addWidget(scroll)

        property_widgets = {}

        def safe_float(val, default=0.0):
            """Safely convert any value to float, handling 'None' and other issues."""
            if val is None or str(val).lower() == "none" or str(val).strip() == "":
                return default
            try:
                return float(val)
            except (ValueError, TypeError):
                return default

        for key, prop in base_properties.items():
            # Usar el valor guardado si existe, si no, usar el del motor (base)
            current_val = saved_props.get(key, prop.get("value"))
            p_type = prop["type"].lower()
            label_text = prop.get("text", key)  # Usar el texto descriptivo si existe

            if p_type == "boolean":
                widget = QCheckBox()
                # El motor devuelve "1" para true o "0" para false a veces
                widget.setChecked(str(current_val).lower() in ["true", "1"])
            elif p_type == "int":
                widget = QSpinBox()
                widget.setRange(-10000, 10000)
                widget.setValue(int(safe_float(current_val)))
            elif p_type == "float":
                widget = QDoubleSpinBox()
                widget.setRange(-10000.0, 10000.0)
                widget.setValue(safe_float(current_val))
            elif p_type == "slider":
                # Sliders are usually floats in WE
                widget = QDoubleSpinBox()
                p_min = safe_float(prop.get("min"), 0.0)
                p_max = safe_float(prop.get("max"), 100.0)
                p_step = safe_float(prop.get("step"), 0.1)
                widget.setRange(p_min, p_max)
                widget.setSingleStep(p_step)
                widget.setValue(safe_float(current_val, p_min))
            elif p_type == "color":
                from PySide6.QtWidgets import QPushButton, QColorDialog
                from PySide6.QtGui import QColor

                # Botón que actúa como selector y muestra el color
                color_btn = QPushButton()
                initial_color_str = str(current_val) if current_val and str(current_val).lower() != "none" else "1,1,1"
                initial_color = self.we_to_qt_color(initial_color_str)

                # Estilo para que el botón tenga el color de fondo
                def update_btn_style(btn, color):
                    btn.setStyleSheet(
                        f"background-color: {color.name()}; border: 1px solid #555; height: 25px;"
                    )

                update_btn_style(color_btn, initial_color)

                # Guardamos el valor actual en un atributo del widget para leerlo después
                color_btn.setProperty("we_value", initial_color_str)

                def pick_color(checked_state, btn_obj):  # Ahora acepta dos argumentos
                    current = self.we_to_qt_color(btn_obj.property("we_value"))
                    new_color = QColorDialog.getColor(current, self, "Select Color")
                    if new_color.isValid():
                        update_btn_style(btn_obj, new_color)
                        btn_obj.setProperty("we_value", self.qt_to_we_color(new_color))

                color_btn.clicked.connect(lambda checked_state, b=color_btn: pick_color(checked_state, b))
                widget = color_btn
            else:
                widget = QLineEdit(str(current_val) if current_val is not None else "")

            form_layout.addRow(label_text, widget)
            property_widgets[key] = (widget, p_type)

        # Save button
        btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        btns.accepted.connect(dialog.accept)
        btns.rejected.connect(dialog.reject)
        main_vlayout.addWidget(btns)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_props = {}
            for key, (widget, p_type) in property_widgets.items():
                if p_type == "boolean":
                    val = 1 if widget.isChecked() else 0
                elif p_type in ["int", "float", "slider"]:
                    val = widget.value()
                elif p_type == "color":
                    val = widget.property("we_value")
                else:
                    val = widget.text()

                # Check if it differs from the base (default) value
                base_val_raw = base_properties[key].get("value")
                is_changed = False

                if p_type == "boolean":
                    norm_base = 1 if str(base_val_raw).lower() in ["1", "true"] else 0
                    is_changed = (val != norm_base)
                elif p_type == "int":
                    try:
                        is_changed = (int(safe_float(val)) != int(safe_float(base_val_raw)))
                    except: is_changed = True
                elif p_type in ["float", "slider"]:
                    try:
                        is_changed = abs(safe_float(val) - safe_float(base_val_raw)) > 0.0001
                    except: is_changed = True
                elif p_type == "color":
                    c1 = self.we_to_qt_color(str(val))
                    c2 = self.we_to_qt_color(str(base_val_raw) if base_val_raw and str(base_val_raw).lower() != 'none' else "1,1,1")
                    is_changed = (c1 != c2)
                else:
                    is_changed = (str(val) != str(base_val_raw))

                if is_changed:
                    new_props[key] = val

            # Guardar en el diccionario global del configurador
            if screen not in self.screen_configs:
                self.screen_configs[screen] = {}

            self.screen_configs[screen]["properties"] = new_props

            # Aplicar cambios al script .sh y reiniciar
            self.apply_changes_automatically()

    def load_wallpaper_properties(self, wallpaper_id):
        """Load properties of a specific wallpaper for configuration"""
        # Execute the command and parse the output
        try:
            # Crucial for stand-alone binaries (PyInstaller):
            # PyInstaller modifies LD_LIBRARY_PATH to point to its internal _MEI folder.
            # We need to restore the original system paths AND add the WE path.
            env = os.environ.copy()
            we_path = "/opt/linux-wallpaperengine"

            # 1. Clean LD_LIBRARY_PATH from PyInstaller's influence
            if getattr(sys, 'frozen', False):
                if 'LD_LIBRARY_PATH_ORIG' in env:
                    env['LD_LIBRARY_PATH'] = env['LD_LIBRARY_PATH_ORIG']
                else:
                    env.pop('LD_LIBRARY_PATH', None)

            # 2. Re-construct LD_LIBRARY_PATH carefully
            current_ld = env.get('LD_LIBRARY_PATH', '')
            paths = [
                we_path,
                os.path.join(we_path, "lib"),
                '/usr/lib',
                '/usr/local/lib',
                '/usr/lib/x86_64-linux-gnu',
                '/lib/x86_64-linux-gnu'
            ]
            if current_ld:
                paths.append(current_ld)

            env['LD_LIBRARY_PATH'] = ":".join([p for p in paths if os.path.exists(p)])

            # Check for the binary in common locations
            binary = os.path.join(we_path, "linux-wallpaperengine")
            if not os.path.exists(binary):
                binary = "linux-wallpaperengine"

            result = subprocess.run(
                [binary, "--list-properties", wallpaper_id],
                capture_output=True,
                text=True,
                timeout=5,
                env=env
            )
            if result.returncode != 0:
                print(f"Error listing properties for {wallpaper_id}: {result.stderr}")
                return {}

            properties = {}
            lines = result.stdout.strip().split("\n")
            current_key = None
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                if " - " in line:
                    # New property
                    parts = line.split(" - ", 1)
                    if len(parts) == 2:
                        current_key = parts[0].strip()
                        properties[current_key] = {"type": parts[1].strip()}
                elif current_key:
                    if line.startswith("Text:"):
                        properties[current_key]["text"] = line.split("Text:", 1)[1].strip()
                    elif line.startswith("Value:"):
                        properties[current_key]["value"] = line.split("Value:", 1)[1].strip()
                    elif line.startswith("Min:"):
                        properties[current_key]["min"] = line.split("Min:", 1)[1].strip()
                    elif line.startswith("Max:"):
                        properties[current_key]["max"] = line.split("Max:", 1)[1].strip()
                    elif line.startswith("Step:"):
                        properties[current_key]["step"] = line.split("Step:", 1)[1].strip()

            return properties
        except Exception as e:
            print(f"Error loading properties for {wallpaper_id}: {e}")
            return {}

    def load_wallpaper_info(self, wallpaper_id, wallpaper_path):
        """Load info of a specific wallpaper with better encoding handling"""
        project_json = os.path.join(wallpaper_path, "project.json")
        preview_jpg = os.path.join(wallpaper_path, "preview.jpg")
        preview_gif = os.path.join(wallpaper_path, "preview.gif")

        info = {
            "id": wallpaper_id,
            "path": wallpaper_path,
            "title": wallpaper_id,
            "description": "",
            "preview": None,
            "supported": True,
            "unsupported_reason": "",
        }

        # Read JSON if it exists
        if os.path.exists(project_json):
            try:
                # Read with UTF-8 directly
                with open(project_json, "r", encoding="utf-8") as f:
                    data = json.load(f)

                # Get RAW title and description, next normalize them
                raw_title = data.get("title", wallpaper_id)
                raw_description = data.get("description", "")

                info["title"] = (
                    self.normalize_text(raw_title) if raw_title else wallpaper_id
                )
                info["description"] = (
                    self.normalize_text(raw_description) if raw_description else ""
                )

            except Exception as e:
                print(f"Error reading JSON for {wallpaper_id}: {e}")
                info["title"] = wallpaper_id
                info["description"] = ""

        # Load preview if it exists
        if os.path.exists(preview_jpg):
            info["preview"] = preview_jpg
        elif os.path.exists(preview_gif):
            info["preview"] = preview_gif

        # Verifica si es apto para linux-wallpaperengine
        supported, reason = self.is_wallpaper_supported(wallpaper_path)
        info["supported"] = supported
        info["unsupported_reason"] = reason

        self.wallpapers[wallpaper_id] = info

    def normalize_text(self, text):
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

    def update_listboxes(self):
        """Update the wallpaper list in the QListWidget (Qt version)"""
        if hasattr(self, "wallpaper_list"):
            self.wallpaper_list.clear()
            sorted_wallpapers = sorted(
                self.wallpapers.items(), key=lambda x: x[1]["title"].lower()
            )
            for wallpaper_id, info in sorted_wallpapers:
                display_text = f"{info['title']} (ID: {wallpaper_id})"
                if not info.get("supported", True):
                    display_text += f" [NOT SUPPORTED: {info['unsupported_reason']}]"
                self.wallpaper_list.addItem(display_text)
            # Highlight the current selection if it exists
            if self.current_selection is not None:
                for idx, (wallpaper_id, _) in enumerate(sorted_wallpapers):
                    if wallpaper_id == self.current_selection:
                        self.wallpaper_list.setCurrentRow(idx)
                        break
        # Update screen status
        self.update_screen_status()

    def update_screen_status(self):
        """
        Update the status labels for each screen to reflect the currently assigned wallpaper.
        """
        for screen in self.detected_screens:
            label = self.status_labels.get(screen)
            wallpaper_id = self.selected_wallpapers.get(screen)
            if label is not None:
                if wallpaper_id and wallpaper_id in self.wallpapers:
                    title = self.wallpapers[wallpaper_id]["title"]
                    # Set the screen name in orange and the title in green
                    label.setText(
                        f'<span style="color: Green;">{screen}:</span> <span style="color: yellow;">{title}</span>'
                    )

                else:
                    label.setText(f"{screen}: Not assigned")
                    label.setStyleSheet("color: red;")

    def check_wallpaper_process(self):
        """Check if wallpaper engine is running"""
        try:
            for proc in psutil.process_iter(["pid", "name", "cmdline"]):
                try:
                    # Check by process name
                    if (
                            proc.info["name"]
                            and "linux-wallpaperengine" in proc.info["name"]
                    ):
                        return True

                    # Check by command line (more reliable)
                    if proc.info["cmdline"]:
                        cmdline_str = " ".join(proc.info["cmdline"])
                        if "linux-wallpaperengine" in cmdline_str:
                            return True

                    # Also check the bash script that runs wallpaper engine
                    if proc.info["name"] == "bash" and proc.info["cmdline"]:
                        cmdline_str = " ".join(proc.info["cmdline"])
                        if "start-wallpaperengine.sh" in cmdline_str:
                            return True

                except (
                        psutil.NoSuchProcess,
                        psutil.AccessDenied,
                        psutil.ZombieProcess,
                ):
                    continue

        except Exception as e:
            print(f"Error checking processes: {e}")

        return False

    def stop_wallpaper_engine(self):
        """Stop the wallpaper engine process"""
        import os

        stopped_processes = []
        current_pid = os.getpid()  # PID del proceso actual (python)
        try:
            for proc in psutil.process_iter(["pid", "name", "cmdline"]):
                try:
                    process_found = False

                    # Check by name
                    if (
                            proc.info["name"]
                            and "linux-wallpaperengine" in proc.info["name"]
                    ):
                        process_found = True

                    # Check by command line
                    if not process_found and proc.info["cmdline"]:
                        cmdline_str = " ".join(proc.info["cmdline"])
                        if "linux-wallpaperengine" in cmdline_str:
                            process_found = True

                    # Also stop the bash script
                    if (
                            not process_found
                            and proc.info["name"] == "bash"
                            and proc.info["cmdline"]
                    ):
                        cmdline_str = " ".join(proc.info["cmdline"])
                        if "start-wallpaperengine.sh" in cmdline_str:
                            process_found = True

                    # Evitar matar el proceso actual (python)
                    if process_found and proc.info["pid"] != current_pid:
                        print(
                            f"Stopping process: {proc.info['name']} (PID: {proc.info['pid']})"
                        )
                        proc.terminate()
                        stopped_processes.append(proc.info["pid"])

                except (
                        psutil.NoSuchProcess,
                        psutil.AccessDenied,
                        psutil.ZombieProcess,
                ):
                    continue

            # Wait for processes to finish
            if stopped_processes:
                import time

                time.sleep(2)

                # Check if still running and force termination
                for proc in psutil.process_iter(["pid", "name"]):
                    try:
                        if proc.info["pid"] in stopped_processes and proc.is_running():
                            proc.kill()
                            print(
                                f"Forcing termination of process PID: {proc.info['pid']}"
                            )
                    except (
                            psutil.NoSuchProcess,
                            psutil.AccessDenied,
                            psutil.ZombieProcess,
                    ):
                        continue

            return len(stopped_processes) > 0

        except Exception as e:
            print(f"Error stopping wallpaper engine: {e}")
            return False

    def start_wallpaper_engine(self):
        """Start wallpaper engine in the background"""
        try:
            print("Starting wallpaper engine...")

            # Run the script in the background
            process = subprocess.Popen(
                [self.script_path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )

            print(f"Script started with PID: {process.pid}")

            # Wait longer for the script to execute (it has sleep 5)
            import time

            print("Waiting for the script to initialize...")

            # Try to detect the process with longer intervals
            for attempt in range(15):  # 15 attempts over 15 seconds
                time.sleep(1)  # Wait 1 second between attempts

                if self.check_wallpaper_process():
                    print(
                        f"✓ Wallpaper engine detected successfully (attempt {attempt + 1})"
                    )
                    return True

                # Show progress every 3 attempts
                if attempt % 3 == 2:
                    print(f"Waiting... ({attempt + 1}/15 attempts)")

            # If we reach here, it was not detected in 15 seconds
            print("⚠ Wallpaper engine not detected in 15 seconds")

            # Check if the bash script is still running
            try:
                if process.poll() is None:  # The process is still running
                    print(
                        "✓ The script is still running, probably started successfully"
                    )
                    return True
                else:
                    print("✗ The script ended unexpectedly")
                    return False
            except:
                print("✓ Assuming successful start")
                return True

        except Exception as e:
            print(f"Error starting wallpaper engine: {e}")
            return False

    def save_current_config(self):
        """
        Save the current wallpaper configuration for each screen.
        """
        config_path = os.path.expanduser("~/.config/wallpaperengine_config.json")
        config_dir = os.path.dirname(config_path)
        os.makedirs(config_dir, exist_ok=True)  # Ensure directory exists
        try:
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(self.selected_wallpapers, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")

    def assign_and_apply(self, screen_name):
        """Assign wallpaper to a screen and automatically apply changes"""
        if self.current_selection is None:
            QMessageBox.warning(
                self,
                "No selection",
                "Please select a wallpaper from the list first.",
            )
            return

        # Assign the wallpaper
        self.selected_wallpapers[screen_name] = self.current_selection
        self.save_current_config()  # Save config after assignment
        self.update_screen_status()
        # If we reach here, all screens have assigned wallpapers
        self.apply_changes_automatically()

    def load_config_from_script(self):
        """Read the .sh file to extract the actual config"""
        if not os.path.exists(self.script_path):
            return {}

        configs = {}
        try:
            with open(self.script_path, "r") as f:
                content = f.read()

            # Search for the command line
            if "linux-wallpaperengine" not in content:
                return {}

            import re

            # Extraer FPS (Global)
            fps_match = re.search(r"--fps (\d+)", content)
            fps = int(fps_match.group(1)) if fps_match else 30

            # Extract Audio (Global)
            silent = "--silent" in content
            vol_match = re.search(r"--volume (\d+)", content)
            volume = int(vol_match.group(1)) if vol_match else 15

            # Extract config per screen
            # Search every --screen-root and everything before the next key arg
            screens = re.findall(r"--screen-root\s+([\w-]+)", content)

            for screen in screens:
                # Look for the next text fragment for this screen
                # (From this screen-root to the next or the final of the line)
                pattern = rf"--screen-root\s+{screen}.*?--bg\s+[\"']\$WALLPAPER\d+[\"'](.*?)(?=--screen-root|$)"
                screen_block = re.search(pattern, content, re.DOTALL)
                block_text = screen_block.group(1) if screen_block else ""

                # Parse properties
                props = {}
                prop_matches = re.findall(r"--set-property\s+([\w.-]+)=([^\s\\]+|'[^']*'|\"[^\"]*\")", block_text)
                for p_key, p_val in prop_matches:
                    props[p_key] = p_val.strip("'\"")

                configs[screen] = {
                    "fps": fps,
                    "volume": volume,
                    "silent": silent,
                    "scaling": (
                        "fill"
                        if "--scaling fill" in block_text or "--scaling fill" in content
                        else "fit" if "--scaling fit" in block_text or "--scaling fit" in content else "default"
                    ),
                    "clamp": (
                        "border"
                        if "--clamp border" in block_text
                        else "clamp" if "--clamp clamp" in block_text else "repeat"
                    ),
                    "noautomute": "--noautomute" in content,
                    "no_audio_proc": "--no-audio-processing" in content,
                    "mouse": "--disable-mouse" not in content,
                    "parallax": "--disable-parallax" not in content,
                    "fs_pause": "--no-fullscreen-pause" not in content,
                    "properties": props,
                }
            return configs
        except Exception as e:
            print(f"Error al leer el script: {e}")
            return {}

    def config_wallpaper(self, screen_name):
        from PySide6.QtWidgets import (
            QDialog,
            QVBoxLayout,
            QFormLayout,
            QSpinBox,
            QCheckBox,
            QComboBox,
            QDialogButtonBox,
            QGroupBox,
        )

        if screen_name not in self.screen_configs:
            file_configs = self.load_config_from_script()
            if screen_name in file_configs:
                self.screen_configs[screen_name] = file_configs[screen_name]
        defaults = {
            "fps": 30,
            "volume": 15,
            "silent": True,
            "scaling": "fill",
            "noautomute": False,
            "no_audio_proc": False,
            "clamp": "border",
            "mouse": True,
            "parallax": True,
            "fs_pause": True,
        }
        cfg = self.screen_configs.get(screen_name, defaults)

        dialog = QDialog(self)
        dialog.setWindowTitle(f"Configuración Avanzada: {screen_name}")
        main_layout = QVBoxLayout(dialog)
        form = QFormLayout()

        # --- Audio Section ---
        audio_group = QGroupBox("Audio")
        audio_form = QFormLayout(audio_group)
        vol_spin = QSpinBox()
        vol_spin.setRange(0, 100)
        vol_spin.setValue(cfg["volume"])
        silent_cb = QCheckBox("Mute (--silent)")
        silent_cb.setChecked(cfg["silent"])
        automute_cb = QCheckBox("Disable Automute")
        automute_cb.setChecked(cfg["noautomute"])
        audio_proc_cb = QCheckBox("Disable Audio Processing")
        audio_proc_cb.setChecked(cfg["no_audio_proc"])
        audio_form.addRow("Volumen:", vol_spin)
        audio_form.addRow(silent_cb)
        audio_form.addRow(automute_cb)
        audio_form.addRow(audio_proc_cb)

        # --- Performance & Behavior Section ---
        perf_group = QGroupBox("Performance")
        perf_form = QFormLayout(perf_group)
        fps_spin = QSpinBox()
        fps_spin.setRange(1, 144)
        fps_spin.setValue(cfg["fps"])
        mouse_cb = QCheckBox("Enable Mouse Interaction")
        mouse_cb.setChecked(cfg["mouse"])
        parallax_cb = QCheckBox("Enable Parallax")
        parallax_cb.setChecked(cfg["parallax"])
        fs_pause_cb = QCheckBox("Pause on Fullscreen")
        fs_pause_cb.setChecked(cfg["fs_pause"])
        perf_form.addRow("Max FPS:", fps_spin)
        perf_form.addRow(mouse_cb)
        perf_form.addRow(parallax_cb)
        perf_form.addRow(fs_pause_cb)

        # --- Visual Section ---
        visual_group = QGroupBox("Visual")
        visual_form = QFormLayout(visual_group)
        scaling_combo = QComboBox()
        scaling_combo.addItems(["fill", "fit", "stretch", "default"])
        scaling_combo.setCurrentText(cfg["scaling"])
        clamp_combo = QComboBox()
        clamp_combo.addItems(["border", "clamp", "repeat"])
        clamp_combo.setCurrentText(cfg["clamp"])
        visual_form.addRow("Scaling:", scaling_combo)
        visual_form.addRow("Clamping:", clamp_combo)

        main_layout.addWidget(audio_group)
        main_layout.addWidget(perf_group)
        main_layout.addWidget(visual_group)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        main_layout.addWidget(buttons)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            # 1. Def of GLOBAL and LOCAL keys
            global_keys = [
                "fps",
                "volume",
                "silent",
                "noautomute",
                "no_audio_proc",
                "fs_pause",
                "clamp",
                "mouse",
                "parallax",
            ]
            local_keys = ["scaling"]

            # 2. Recopilamos los nuevos valores del diálogo
            new_config = {
                "fps": fps_spin.value(),
                "volume": vol_spin.value(),
                "silent": silent_cb.isChecked(),
                "noautomute": automute_cb.isChecked(),
                "no_audio_proc": audio_proc_cb.isChecked(),
                "scaling": scaling_combo.currentText(),
                "clamp": clamp_combo.currentText(),
                "mouse": mouse_cb.isChecked(),
                "parallax": parallax_cb.isChecked(),
                "fs_pause": fs_pause_cb.isChecked(),
            }
            # 3. Sync: Apply global keys to all the screens
            for s_name in getattr(self, "detected_screens", []):
                # If the screen not exist in the dict, we set the default keys
                if s_name not in self.screen_configs:
                    self.screen_configs[s_name] = defaults.copy()

                # Update only for global keys
                for key in global_keys:
                    self.screen_configs[s_name][key] = new_config[key]

            # 4. Custom: apply local keys only for the screen
            for key in local_keys:
                self.screen_configs[screen_name][key] = new_config[key]

            # 5. Regen script and apply changes
            self.apply_changes_automatically()

    def unassign_wallpaper(self, screen_name):
        """Unassign the wallpaper from a screen and update the status"""
        self.selected_wallpapers[screen_name] = None
        self.save_current_config()  # Save config after unassignment
        self.update_screen_status()
        # Optionally: stop the engine if there are no wallpapers assigned
        assigned = [s for s in self.detected_screens if self.selected_wallpapers.get(s)]
        if not assigned:
            self.stop_wallpaper_engine()
        else:
            wallpaper_paths = {}
            for screen in assigned:
                wallpaper_id = self.selected_wallpapers.get(screen)
                if wallpaper_id:
                    wallpaper_paths[screen] = os.path.join(
                        self.wallpaper_base_path, wallpaper_id
                    )
            self.update_script_with_assigned_screens(wallpaper_paths)
            self.start_wallpaper_engine()
        # Update the UI
        self.update_screen_status()

    def apply_changes_automatically(self):
        """Automatically apply changes when at least one screen is configured"""
        # Detect screens again in case the session changed (e.g., xrdp vs physical session)
        self.detected_screens = self.detect_screens()

        # Check that at least one wallpaper is assigned
        assigned_screens = [
            s for s in self.detected_screens if self.selected_wallpapers.get(s)
        ]
        if not assigned_screens:
            QMessageBox.warning(
                self,
                "No wallpapers assigned",
                "Please assign at least one wallpaper to a screen before applying changes.",
            )
            return

        # Check that assigned wallpapers exist
        wallpaper_paths = {}
        for screen in assigned_screens:
            wallpaper_id = self.selected_wallpapers.get(screen)
            if wallpaper_id is None:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"No wallpaper assigned for {screen}.",
                )
                return

            wallpaper_path = os.path.join(self.wallpaper_base_path, wallpaper_id)
            if not os.path.exists(wallpaper_path):
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Wallpaper for {screen} does not exist: {wallpaper_path}",
                )
                return

            wallpaper_paths[screen] = wallpaper_path

        # Update interface
        QApplication.processEvents()

        try:
            # Step 1: Stop wallpaper engine if running
            was_running = self.check_wallpaper_process()
            if was_running:
                self.stop_wallpaper_engine()

            # Step 2: Update script configuration (only with assigned screens)
            self.update_script_with_assigned_screens(wallpaper_paths)

            # Step 3: Restart wallpaper engine
            QApplication.processEvents()

            self.start_wallpaper_engine()

            # Show confirmation
            success_lines = ["Wallpapers applied successfully:\n"]
            for screen in self.detected_screens:
                wallpaper_id = self.selected_wallpapers.get(screen)
                if wallpaper_id is not None and wallpaper_id in self.wallpapers:
                    title = self.wallpapers[wallpaper_id]["title"]
                    success_lines.append(
                        f"✓ {screen}: {title[:30]}{'...' if len(title) > 30 else ''}"
                    )
                else:
                    success_lines.append(f"○ {screen}: Not assigned")

            QMessageBox.information(
                self,
                "Changes Applied",
                "\n".join(success_lines),
            )

        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Error applying changes: {e}",
            )

    def update_script_with_assigned_screens(self, wallpaper_paths):
        """Update the script with only the screens that have assigned wallpapers"""
        try:
            assigned_screens = list(wallpaper_paths.keys())

            # Generate full script content
            script_content = f"""#!/bin/bash

            # Automatically generated file by wallpaper-config.py
            # Do not edit manually - changes will be overwritten
            # Last updated: $(date)

            # Create log file if it doesn't exist
            LOG_FILE="/tmp/wallpaper-engine.log"
            touch "$LOG_FILE"

            echo "$(date): Starting Wallpaper Engine..." >> "$LOG_FILE"

            # Wait for the system to be ready
            sleep 5

            # Check that wallpapers exist
            """

            # Add WALLPAPER variables only for assigned screens
            for i, screen in enumerate(assigned_screens, 1):
                wallpaper_path = wallpaper_paths[screen]
                script_content += f'WALLPAPER{i}="{wallpaper_path}"\n'

            script_content += "\n# Check that wallpapers exist\n"
            # Add checks only for assigned screens
            for i, screen in enumerate(assigned_screens, 1):
                script_content += f'if [[ ! -d "$WALLPAPER{i}" ]]; then\n'
                script_content += f'    echo "$(date): Error: Wallpaper for {screen} not found at $WALLPAPER{i}" >> "$LOG_FILE"\n'
                script_content += f"    exit 1\nfi\n"

            # Clean up previous processes
            script_content += "# Clean up previous processes\npkill -f linux-wallpaperengine 2>/dev/null\n\n"
            script_content += "# Environment variables for stability\n"
            script_content += (
                "export LD_LIBRARY_PATH=/opt/linux-wallpaperengine:$LD_LIBRARY_PATH\n"
            )
            script_content += "export __GL_THREADED_OPTIMIZATIONS=0\n"
            script_content += 'export PULSE_RUNTIME_PATH="/run/user/$(id -u)/pulse"\n\n'
            script_content += (
                'echo "$(date): Running with wallpapers:" >> "$LOG_FILE"\n'
            )
            for idx, screen in enumerate(assigned_screens, 1):
                script_content += f'echo "  {screen}: $WALLPAPER{idx}" >> "$LOG_FILE"\n'

            # Generate command using only assigned screens
            script_content += "\n# Run wallpaper engine\nlinux-wallpaperengine"
            for i, screen in enumerate(assigned_screens, 1):
                cs = self.screen_configs.get(screen, {})
                scaling = cs.get("scaling", "fill")
                script_content += f" --scaling {scaling} \\\n --screen-root {screen} \\\n --bg \"$WALLPAPER{i}\" \\\n"
                # If defined, set custom properties for the wallpaper engine
                if "properties" in cs and isinstance(cs["properties"], dict):
                    for p_key, p_val in cs["properties"].items():
                        # Los strings con espacios deben ir entre comillas
                        if isinstance(p_val, str) and " " in p_val:
                            script_content += f" --set-property {p_key}=\"{p_val}\" \\\n"
                        else:
                            script_content += f" --set-property {p_key}={p_val} \\\n"

            # Add --silent only ONCE at the end
            base_defaults = {
                "fps": 30,
                "volume": 15,
                "silent": True,
                "noautomute": False,
                "no_audio_proc": False,
                "mouse": True,
                "parallax": True,
                "fs_pause": True,
                "clamp": "border",
            }

            # 2. Obtenemos la config de la primera pantalla y le inyectamos los defaults
            # para que nunca falte ninguna llave (KeyError)
            first_screen = assigned_screens[0]
            c = base_defaults.copy()
            c.update(self.screen_configs.get(first_screen, {}))

            # 3. Ahora usamos 'c' con total seguridad
            if c["silent"]:
                script_content += " --silent \\\n"
            else:
                script_content += f" --volume {c['volume']} \\\n"

            if c["noautomute"]:
                script_content += " --noautomute \\\n"

            if c["no_audio_proc"]:
                script_content += " --no-audio-processing \\\n"

            if not c["mouse"]:
                script_content += " --disable-mouse \\\n"

            # Aquí es donde fallaba antes si 'clamp' no estaba en el .get()
            if c.get("clamp"):
                script_content += f" --clamp {c['clamp']} \\\n"

            if not c["parallax"]:
                script_content += " --disable-parallax \\\n"

            if not c["fs_pause"]:
                script_content += " --no-fullscreen-pause \\\n"

            script_content += f" --fps {c['fps']} \\\n"

            script_content += '2>&1 | tee -a "$LOG_FILE"\n'

            print(f"Final script content:\n{script_content}")

            # Write the file
            with open(self.script_path, "w") as f:

                f.write(script_content)

            # Ensure it's executable
            os.chmod(self.script_path, 0o755)

        except Exception as e:
            raise Exception(f"Error updating script: {e}")

    def view_script(self):
        """Show the current content of the script"""
        try:
            with open(self.script_path, "r") as f:
                content = f.read()

            # Create window to show script using PySide6

            script_window = QDialog(self)
            script_window.setWindowTitle("Wallpaper Engine Script")
            script_window.resize(800, 600)

            layout = QVBoxLayout(script_window)

            text_edit = QTextEdit()
            text_edit.setReadOnly(True)
            text_edit.setPlainText(content)
            text_edit.setFont(QFont("Monaco", 10))
            layout.addWidget(text_edit)

            # Optional: Add a close button
            btn_layout = QHBoxLayout()
            close_btn = QPushButton("Close")
            close_btn.clicked.connect(script_window.accept)
            btn_layout.addStretch()
            btn_layout.addWidget(close_btn)
            layout.addLayout(btn_layout)

            script_window.exec()

        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Error reading script: {e}",
            )

    def create_overlays(self):
        """Create persistent per-screen overlay widgets and keep them hidden.
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
                                target_x >= sgeom.x()
                                and target_x < sgeom.x() + sgeom.width()
                                and target_y >= sgeom.y()
                                and target_y < sgeom.y() + sgeom.height()
                        ):
                            try:
                                overlay.windowHandle().setScreen(s)
                                assigned_qscreen = s
                                try:
                                    name = s.name()
                                except Exception:
                                    name = str(sgeom)
                                print(
                                    f"Overlay for {screen}: assigned to QScreen: {name} (geom {sgeom})"
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
                # Re-assert assigned screen (some compositors only honor setScreen when mapping)
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

    def is_wayland(self):
        """Return True if running under Wayland (likely compositor restrictions apply)."""
        return bool(os.environ.get("WAYLAND_DISPLAY"))

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

        geoms = self.get_monitor_geometries()
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
        """Show overlay only for a single screen and log diagnostics."""
        print(f"identify_monitor: requested for {screen_name}")
        # If overlays exist, show only that one
        ov = None
        if hasattr(self, "_screen_overlays"):
            ov = self._screen_overlays.get(screen_name)
        if ov:
            try:
                # Try re-asserting assigned screen
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
        if self.is_wayland():
            QMessageBox.information(
                self,
                "Identify Monitors",
                "Wayland compositor detected. Overlays may be restricted to the screen containing the application.\nUse the 'Identify' button while the app is on the target monitor, or move the app to that monitor and retry.",
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
        """Show overlay labels on each screen to identify them (persistent-overlay method)."""
        # If Wayland, show a monitor map simulation (Wayland may restrict real overlays)
        if self.is_wayland():
            print("Wayland detected: showing monitor map simulation")
            self.show_monitor_map(3000)
            return

        # Inform Wayland users about possible compositor restrictions
        if self.is_wayland():
            QMessageBox.information(
                self,
                "Identify Monitors",
                "Wayland compositor detected: some compositors restrict showing windows on outputs other than the one containing the app.\nIf overlays don't appear on other monitors, move the app to that monitor or use the per-screen 'Identify' buttons.",
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

    def manage_autostart(self):
        """
        Show a dialog to enable or disable autostart for the wallpaper engine.
        """
        autostart_exists = os.path.exists(self.desktop_path)
        answer = QMessageBox.question(
            self,
            "Autostart Configuration",
            f"Autostart is currently {'ENABLED' if autostart_exists else 'DISABLED'}.\n\n"
            f"Do you want to {'disable' if autostart_exists else 'enable'} autostart for Wallpaper Engine?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if answer == QMessageBox.StandardButton.Yes:
            if autostart_exists:
                try:
                    os.remove(self.desktop_path)
                    QMessageBox.information(
                        self,
                        "Autostart Disabled",
                        "Autostart has been disabled.",
                    )
                except Exception as e:
                    QMessageBox.critical(
                        self,
                        "Error",
                        f"Could not remove autostart file:\n{e}",
                    )
            else:
                try:
                    self.create_desktop_file()
                    QMessageBox.information(
                        self,
                        "Autostart Enabled",
                        "Autostart has been enabled.",
                    )
                except Exception as e:
                    QMessageBox.critical(
                        self,
                        "Error",
                        f"Could not create autostart file:\n{e}",
                    )
        # Refresh UI info and reload wallpapers/config
        self.setup_ui()
        self.load_wallpapers()
        self.load_current_config()

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
            text_edit = QTextEdit()
            text_edit.setReadOnly(True)
            text_edit.setFont(QFont("Monaco", 10))
            layout.addWidget(text_edit)

            # Clear Logs Button

            btnC_layout = QHBoxLayout()
            clear_btn = QPushButton("Clear Logs")
            clear_btn.clicked.connect(lambda checked,: self.clear_log())
            btnC_layout.addStretch()
            btnC_layout.addWidget(clear_btn)
            layout.addLayout(btnC_layout)

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
                # Stop accessing the widget if it was destroyed
                if not hasattr(text_edit, "setPlainText") or text_edit is None:
                    return
                try:
                    content = read_last_lines(log_file)
                    text_edit.setPlainText(content)
                    if auto_follow_check.isChecked():
                        from PySide6.QtGui import QTextCursor

                        text_edit.moveCursor(QTextCursor.MoveOperation.End)
                except Exception as e:
                    # Stop crashing if the widget was already destroyed
                    if hasattr(text_edit, "setPlainText") and text_edit is not None:
                        try:
                            text_edit.setPlainText(f"Error reading log: {e}")
                        except RuntimeError:
                            pass
                # If the widget was destroyed, stop updating it
                if not log_window.isVisible():
                    return
                # If auto-refresh is active, call again after 2 seconds
                if auto_refresh_check.isChecked():
                    QTimer.singleShot(2000, refresh_log_content)

            # Connect checkbox to refresh logic
            def on_auto_refresh_toggle(state):
                if auto_refresh_check.isChecked():
                    refresh_log_content()

            auto_refresh_check.stateChanged.connect(on_auto_refresh_toggle)

            # Initial load
            refresh_log_content()

            log_window.exec()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error reading log: {e}")

    def load_wallpaper_properties(self, wallpaper_id):
        """Load properties of a specific wallpaper for configuration"""
        # Execute the command and parse the output
        try:
            # Crucial for stand-alone binaries (PyInstaller):
            # PyInstaller modifies LD_LIBRARY_PATH to point to its internal _MEI folder.
            # We need to restore the original system paths AND add the WE path.
            env = os.environ.copy()
            we_path = "/opt/linux-wallpaperengine"

            # 1. Clean LD_LIBRARY_PATH from PyInstaller's influence
            if getattr(sys, 'frozen', False):
                if 'LD_LIBRARY_PATH_ORIG' in env:
                    env['LD_LIBRARY_PATH'] = env['LD_LIBRARY_PATH_ORIG']
                else:
                    env.pop('LD_LIBRARY_PATH', None)

            # 2. Re-construct LD_LIBRARY_PATH carefully
            current_ld = env.get('LD_LIBRARY_PATH', '')
            paths = [
                we_path,
                os.path.join(we_path, "lib"),
                '/usr/lib',
                '/usr/local/lib',
                '/usr/lib/x86_64-linux-gnu',
                '/lib/x86_64-linux-gnu'
            ]
            if current_ld:
                paths.append(current_ld)

            env['LD_LIBRARY_PATH'] = ":".join([p for p in paths if os.path.exists(p)])

            # Check for the binary in common locations
            binary = os.path.join(we_path, "linux-wallpaperengine")
            if not os.path.exists(binary):
                binary = "linux-wallpaperengine"

            result = subprocess.run(
                [binary, "--list-properties", wallpaper_id],
                capture_output=True,
                text=True,
                timeout=5,
                env=env
            )
            if result.returncode != 0:
                print(f"Error listing properties for {wallpaper_id}: {result.stderr}")
                return {}

            properties = {}
            lines = result.stdout.strip().split("\n")
            current_key = None
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                if " - " in line:
                    # New property
                    parts = line.split(" - ", 1)
                    if len(parts) == 2:
                        current_key = parts[0].strip()
                        properties[current_key] = {"type": parts[1].strip()}
                elif current_key:
                    if line.startswith("Text:"):
                        properties[current_key]["text"] = line.split("Text:", 1)[1].strip()
                    elif line.startswith("Value:"):
                        properties[current_key]["value"] = line.split("Value:", 1)[1].strip()
                    elif line.startswith("Min:"):
                        properties[current_key]["min"] = line.split("Min:", 1)[1].strip()
                    elif line.startswith("Max:"):
                        properties[current_key]["max"] = line.split("Max:", 1)[1].strip()
                    elif line.startswith("Step:"):
                        properties[current_key]["step"] = line.split("Step:", 1)[1].strip()

            return properties
        except Exception as e:
            print(f"Error loading properties for {wallpaper_id}: {e}")
            return {}


def main():
    app = QApplication(sys.argv)
    window = WallpaperConfigQt()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(" Process interrupted by user.")
    except Exception as e:
        print(f"Error: {e}")
