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
        with open(self.autostart_path, "w") as f:
            f.write(desktop_content)

        print(f"Desktop file created: {self.autostart_path}")

    except Exception as e:
        print(f"Error creating desktop file: {e}")
