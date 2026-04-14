import os
from textwrap import dedent

def create_desktop_file(self):
    """Create the .desktop file for autostart"""
    # Usamos dedent para que el string no tenga espacios al inicio de cada línea
    desktop_content = dedent(f"""\
        [Desktop Entry]
        Type=Application
        Name=Wallpaper Engine
        Comment=Automatically starts Linux-WallpaperEngine at system startup
        Exec={os.path.expanduser(self.script_path)}
        Icon=preferences-desktop-wallpaper
        Terminal=false
        Hidden=false
        X-GNOME-Autostart-enabled=true
        StartupNotify=false
        Categories=Graphics;Settings;
    """)

    try:
        # Aseguramos que el directorio de autostart exista
        os.makedirs(os.path.dirname(self.autostart_path), exist_ok=True)

        with open(self.autostart_path, "w") as f:
            f.write(desktop_content)

        print(f"Desktop file created: {self.autostart_path}")

    except Exception as e:
        print(f"Error creating desktop file: {e}")
