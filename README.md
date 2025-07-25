# wallpaper-config

Graphical configurator for Linux-WallpaperEngine, compatible with multi-monitor setups.
Requires the Official Wallpaper Engine installed on Steam and wallpapers downloaded from the Official Wallpaper Engine Workshop. You don't need to run Wallpaper Engine; when installed, it automatically downloads the subscribed wallpapers using Steam.

## Features

- Automatically detects connected screens (`xrandr`, `wlr-randr`, `swaymsg`).
- Assign different wallpapers to each screen.
- Generates a startup script (`start-wallpaperengine.sh`) that adapts to screen changes (physical or remote sessions).
- Autostart support via `.desktop` file in `~/.config/autostart/`.
- Preview and details for each wallpaper.
- Logs accessible from the interface.
- All interface texts are in English.
- Automatic installation of all dependencies, including `requests`.

## Requirements

- Python 3
- Dependencies: `psutil`, `tkinter`, `Pillow`, `requests` (auto-installed)
- Linux Wallpaper Engine installed and available in the PATH (`linux-wallpaperengine`)
- `xrandr`, `wlr-randr`, or `swaymsg` for screen detection
- Steam and wallpapers downloaded from Official Wallpaper Engine Workshop

All dependencies are installed automatically when running the script.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/eriosgamer/linux-wallpaperengine-GUI.git
   cd linux-wallpaperengine-GUI
   ```
2. Run the configurator:
   ```bash
   python3 wallpaper-config.py
   ```

## Autostart

The application creates a `.desktop` file in `~/.config/autostart/` to automatically start the script when a graphical session begins.

**Note:**  
This method works on most Linux desktop environments based on Freedesktop/xdg (GNOME, KDE, XFCE, Cinnamon, MATE, LXDE, etc).  
It may not work on minimalistic window managers or non-graphical sessions.
RDP sessions (xrdp) do not support showing the wallpaper; it loads but does not display.

## Screen Compatibility

- The generated script automatically updates according to the screens detected in each session.
- If you change session (e.g., from xrdp to physical), the script adapts to the new environment when you apply changes from the interface.

## Usage

1. Select wallpapers for each screen using the graphical interface.
2. Apply changes; the script and configuration are updated automatically.
3. Optionally, enable/disable autostart from the interface.

## Logs and Support

- Logs are saved in `/tmp/wallpaper-engine.log` and can be viewed from the interface.
- If you encounter issues, check the logs and ensure all dependencies are installed.

## License

This project is licensed under the Creative Commons BY-NC-ND License. See the [LICENSE](LICENSE) file for details.

**Warning:**  
The project overwrites the startup script every time changes are applied. Do not manually edit the `start-wallpaperengine.sh` file.

---

**Author:**  
eriosgamer
