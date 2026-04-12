import os

from PySide6.QtGui import QFont
from PySide6.QtWidgets import QMessageBox, QDialog, QVBoxLayout, QTextEdit, QHBoxLayout, QPushButton

from Files.config_files import load_current_config
from Scripts.destok_file import create_desktop_file
from Steam.workshop_items import load_wallpapers
from UI.user_interface import setup_ui


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
    script_content += "# Automatically generated file by WallpaperEngineConfigurator.py\n"
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
        script_content += f'    echo "$(date): Error: Wallpaper for Screen not configured yet. Use WallpaperEngineConfigurator.py to configure." >> "$LOG_FILE"\n'
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
    for idx, (screen, _) in enumerate(assigned, 1):
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

    # Try to get config from the first assigned Screen if available
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

def get_script_path(self):
    """Get the wallpaper engine script path"""
    # Create .local/bin directory if it doesn't exist
    bin_dir = f"~/.local/bin"
    os.makedirs(bin_dir, exist_ok=True)
    return os.path.join(bin_dir, "start-wallpaperengine.sh")

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

        # Extract config per Screen
        # Search every --screen-root and everything before the next key arg
        screens = re.findall(r"--screen-root\s+([\w-]+)", content)

        for screen in screens:
            # Look for the next text fragment for this Screen
            # (From this Screen-root to the next or the final of the line)
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

def update_script_with_assigned_screens(self, wallpaper_paths):
    """Update the script with only the screens that have assigned wallpapers"""
    try:
        assigned_screens = list(wallpaper_paths.keys())

        # Generate full script content
        script_content = f"""#!/bin/bash

        # Automatically generated file by WallpaperEngineConfigurator.py
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

def manage_autostart(self):
    """
    Show a dialog to enable or disable autostart for the wallpaper engine.
    """
    autostart_exists = os.path.exists(self.autostart_path)
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
                os.remove(self.autostart_path)
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
                create_desktop_file(self)
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
    setup_ui(self)
    load_wallpapers(self)
    load_current_config(self)
