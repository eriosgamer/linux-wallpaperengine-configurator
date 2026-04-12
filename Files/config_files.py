import os
import json

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QMessageBox


def load_current_config(self):
    """
    Load the current wallpaper configuration for each Screen, if available.
    This method should set self.selected_wallpapers for each detected Screen.
    """
    config_path = os.path.expanduser("~/.config/wallpaper-engine-configurator/wallpaperengine_config.json")
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

def ensure_required_files(self):
    """Check and create required files if they don't exist"""
    from Scripts.start_script import create_wallpaper_script
    files_created = []

    # Always create the script if it does not exist
    if not os.path.exists(self.script_path):
        create_wallpaper_script(self)
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
                "Linux Wallpaper Engine script is ready.",
            ),
        )

def get_autostart_path():
    """Get the .desktop file path for autostart"""
    # Create .config/autostart directory if it doesn't exist
    autostart_dir = f"/home/{os.getenv('USER')}/.config/autostart"
    os.makedirs(autostart_dir, exist_ok=True)
    return os.path.join(autostart_dir, "start-wallpaperengine.sh.desktop")

def save_current_config(self, key, value):
    """
    Save the current wallpaper configuration for each Screen.
    """
    config_path = os.path.expanduser("~/.config/wallpaper-engine-configurator/wallpaperengine_config.json")
    config_dir = os.path.dirname(config_path)
    os.makedirs(config_dir, exist_ok=True)  # Ensure directory exists
    try:
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(self.selected_wallpapers, f, indent=2)
    except Exception as e:
        print(f"Error saving config: {e}")
