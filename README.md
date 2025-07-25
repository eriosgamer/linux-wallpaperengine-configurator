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
- **Modern Qt interface using PySide6.**
- Uses Tkinter only for monitor identification popups.

## Requirements

- Python 3
- Dependencies: `psutil`, `PySide6`, `Pillow`, `requests`, `tkinter` (auto-installed)
  - `psutil` for system monitoring
  - `PySide6` for the graphical interface
  - `Pillow` for image handling
  - `requests` for network operations
  - `tkinter` for monitor identification popups
- Linux Wallpaper Engine installed and available in the PATH (`linux-wallpaperengine`)
- `xrandr`, `wlr-randr`, or `swaymsg` for screen detection
- Steam and wallpapers downloaded from Official Wallpaper Engine Workshop

All dependencies are installed automatically when running the script.  
If a dependency is missing, the script will prompt you with the exact `pip install` command.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/eriosgamer/linux-wallpaperengine-configurator.git
   cd linux-wallpaperengine-configurator
   ```
2. Run the configurator:
   ```bash
   python3 wallpaper-config.py
   ```

## Autostart

The application creates a `.desktop` file in `~/.config/autostart/` to automatically start the script when a graphical session begins.  
Autostart can be enabled or disabled from the configuration menu in the interface.

**Note:**  
This method works on most Linux desktop environments based on Freedesktop/xdg (GNOME, KDE, XFCE, Cinnamon, MATE, LXDE, etc).  
It may not work on minimalistic window managers or non-graphical sessions.  
RDP sessions (xrdp) do not support showing the wallpaper; it loads but does not display.

## Screen Compatibility

- The generated script automatically updates according to the screens detected in each session.
- If you change session (e.g., from xrdp to physical), the script adapts to the new environment when you apply changes from the interface.

## Usage

1. Select wallpapers for each screen using the graphical interface (Qt).
2. Apply changes; the script and configuration are updated automatically.
3. Optionally, enable/disable autostart from the interface.
4. Use the "Identify Monitors" button to show a popup on each screen (requires Tkinter).

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
