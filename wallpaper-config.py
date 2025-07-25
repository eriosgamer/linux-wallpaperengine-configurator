#!/usr/bin/env python3
import os
import json
import subprocess
import sys
import shutil
import threading
import re

# Force UTF-8
os.environ["PYTHONIOENCODING"] = "utf-8"


# Check dependencies: PySide6 and others
def check_and_install_dependencies():
    missing_packages = []
    try:
        import tkinter
    except ImportError:
        print("tkinter is not installed. Install it with: sudo apt install python3-tk")
        missing_packages.append("tkinter")
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
    QMainWindow,
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
    QDialog,  # Added QDialog import
)
from PySide6.QtGui import QPixmap, QFont
from PySide6.QtCore import Qt, QTimer
from PIL import Image
import psutil
from typing import Optional, Dict


class WallpaperConfigQt(QMainWindow):
    def __init__(self):
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
            sorted_wallpapers = sorted(self.wallpapers.items(), key=lambda x: x[1]["title"].lower())
            for wallpaper_id, info in sorted_wallpapers:
                # Detect CJK characters in the title
                def highlight_cjk(text):
                    # Regex for CJK Unified Ideographs
                    def repl(m):
                        return f'<span style="color:blue;">{m.group(0)}</span>'
                    return re.sub(r'[\u4e00-\u9fff\u3040-\u30ff\u3400-\u4dbf\uac00-\ud7af]+', repl, text)
                title_html = highlight_cjk(info['title'])
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
            import tkinter.messagebox as msgbox

            files_list = "\n• ".join(files_created)

            def show_info():
                msgbox.showinfo(
                    "Initial Setup",
                    f"The following files have been created:\n\n• {files_list}\n\n"
                    f"Linux Wallpaper Engine script is ready."
                )

            threading.Thread(target=show_info, daemon=True).start()

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
        script_content += "\n# Run wallpaper engine\nlinux-wallpaperengine"
        for idx, (screen, _) in enumerate(assigned, 1):
            script_content += f' \\\n  --scaling fill \\\n  --screen-root {screen} \\\n  --bg "$WALLPAPER{idx}"'
        script_content += ' \\\n  --silent \\\n 2>&1 | tee -a "$LOG_FILE"\n'

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
                self.unicode_font = QFontDatabase.systemFont(QFontDatabase.SystemFont.GeneralFont).family()
                print("Warning: No CJK/Arial/Unifont font found. Using system default font.")

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
            sorted_wallpapers = sorted(self.wallpapers.items(), key=lambda x: x[1]["title"].lower())
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
                qimage = QImage(data, image.width, image.height, QImage.Format.Format_RGBA8888)
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
                                qimage = QImage(data, image.width, image.height, QImage.Format.Format_RGBA8888)
                                pixmap = QPixmap.fromImage(qimage)
                                self.preview_label.setPixmap(pixmap)
                                self.preview_label.setText("")
                                self._preview_photo = pixmap
                            except Exception as e:
                                print(f"Error loading preview image: {e}")
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
            return False, "Web type not supported"
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
        return text.replace('\x00', '').strip()

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
                    label.setText(f'<span style="color: Green;">{screen}:</span> <span style="color: yellow;">{title}</span>')
                    
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
        stopped_processes = []
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

                    if process_found:
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
                script_content += f''' \\
  --scaling fill \\
  --screen-root {screen} \\
  --bg "$WALLPAPER{i}"'''

            # Add --silent only ONCE at the end
            script_content += """ \\
  --silent \\
  2>&1 | tee -a "$LOG_FILE"
"""

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
            
    def identify_monitors(self):
        """
        Shows a semi-transparent popup on each detected screen with its name and number.
        Fixes:
        - The popup should not have a title bar or icon (real floating window).
        - The popup should appear centered on each monitor, not in the corner.
        - They should not overlap on the same monitor.
        """
        import threading
        import tkinter as tk

        def get_monitor_geometries():
            """
            Returns a dict {screen_name: (x, y, w, h)} using xrandr.
            """
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
            return geometries

        def show_popup(screen_name, number, geom):
            x, y, w, h = geom
            popup = tk.Toplevel(root)
            popup.overrideredirect(True)
            popup.attributes("-topmost", True)
            # Transparency (only works on some systems)
            try:
                popup.attributes("-alpha", 0.7)
            except Exception:
                pass
            # Dark background and large text
            frame = tk.Frame(popup, bg="#222", bd=3, relief="solid")
            frame.pack(fill="both", expand=True)
            label = tk.Label(
                frame,
                text=f"{number+1}\n{screen_name}",
                font=("Arial", 36, "bold"),
                fg="white",
                bg="#222",
            )
            label.pack(padx=30, pady=30)
            # Centered on the monitor
            popup_w, popup_h = 300, 150
            pos_x = x + (w - popup_w) // 2
            pos_y = y + (h - popup_h) // 2
            popup.geometry(f"{popup_w}x{popup_h}+{pos_x}+{pos_y}")
            popup.update_idletasks()
            # Close the popup after 2 seconds
            popup.after(2000, popup.destroy)

        # Get real geometry of each monitor
        geometries = get_monitor_geometries()
        used = set()

        # Create a temporary Tk root window (hidden)
        root = tk.Tk()
        root.withdraw()  # Hide the main window

        for idx, screen in enumerate(self.detected_screens):
            geom = geometries.get(screen)
            if geom:
                used.add(screen)
                print(f"Showing popup for {screen} at {geom}")
                # Use after to ensure the popup is created in the main Tkinter thread
                root.after(0, show_popup, screen, idx, geom)
            else:
                print(f"Warning: No geometry found for {screen}, popup not shown.")

        # Run the Tkinter event loop for a short time to show popups
        root.after(2200, root.destroy)  # Destroy after popups close
        root.mainloop()

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
            from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QTextEdit, QCheckBox, QPushButton

            log_window = QDialog(self)
            log_window.setWindowTitle("Wallpaper Engine Logs")
            log_window.resize(800, 600)

            layout = QVBoxLayout(log_window)

            # Checkboxes for auto-refresh and auto-follow
            check_box_layout = QHBoxLayout()
            auto_refresh_check = QCheckBox("Auto-refresh")
            auto_follow_check = QCheckBox("Auto-follow")
            check_box_layout.addWidget(auto_refresh_check)
            check_box_layout.addWidget(auto_follow_check)
            check_box_layout.addStretch()
            layout.addLayout(check_box_layout)

            # Text area to show logs
            text_edit = QTextEdit()
            text_edit.setReadOnly(True)
            text_edit.setFont(QFont("Monaco", 10))
            layout.addWidget(text_edit)

            # Close button
            btn_layout = QHBoxLayout()
            close_btn = QPushButton("Close")
            close_btn.clicked.connect(log_window.accept)
            btn_layout.addStretch()
            btn_layout.addWidget(close_btn)
            layout.addLayout(btn_layout)

            def read_last_lines(file_path, max_bytes=200*1024, max_lines=2000):
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
                try:
                    content = read_last_lines(log_file)
                    text_edit.setPlainText(content)
                    if auto_follow_check.isChecked():
                        from PySide6.QtGui import QTextCursor
                        text_edit.moveCursor(QTextCursor.MoveOperation.End)
                except Exception as e:
                    text_edit.setPlainText(f"Error reading log: {e}")
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


def main():
    app = QApplication(sys.argv)
    window = WallpaperConfigQt()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()