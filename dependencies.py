import os
import shutil
import sys

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
