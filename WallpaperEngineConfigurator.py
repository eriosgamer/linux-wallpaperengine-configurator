#!/usr/bin/env python3
import os
import sys
from typing import Optional, Dict

import qdarktheme
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QMessageBox,
)

from Files.config_files import ensure_required_files, get_autostart_path
from Files.icon_file import set_icon_file
from Screen.screen_detection import detect_screens
from Scripts.start_script import get_script_path
from Steam.wallpaper_location import find_wallpaper_directory
from Steam.workshop_items import load_wallpapers
from UI.UI_Tools import create_overlays
from UI.user_interface import setup_ui
from dependencies import check_and_install_dependencies



class WallpaperConfigQt(QMainWindow):
    def __init__(self):
        super().__init__()
        self.screen_configs = {}
        self.status_labels = {}
        self.script_path = get_script_path(self)
        self.autostart_path = get_autostart_path()
        self.detected_screens = detect_screens(self)
        self.wallpapers: Dict[str, dict] = {}
        self.selected_wallpapers: Dict[str, Optional[str]] = {}
        self.wallpaper_list = {}
        self.info_text = {}
        self.current_selection: Optional[str] = None
        self.setWindowTitle("Linux-WallpaperEngine Configuration")
        self.setGeometry(100, 100, 1200, 800)
        self.wallpaper_base_path = find_wallpaper_directory(self)
        if not self.wallpaper_base_path:
            QMessageBox.critical(
                self,
                "Error",
                "Wallpaper directory not found. Make sure you have Steam Workshop content installed.",
            )
            sys.exit(1)
        for screen in self.detected_screens:
            self.selected_wallpapers[screen] = None

        try:
            create_overlays(self)
        except Exception as exc:
            print(f"Warning: could not create overlays at init: {exc}")


        # Main UI
        qdarktheme.setup_theme("dark")
        set_icon_file(self)
        setup_ui(self)
        load_wallpapers(self)
        ensure_required_files(self)

def main():
    # Force UTF-8
    os.environ["PYTHONIOENCODING"] = "utf-8"

    check_and_install_dependencies()

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
