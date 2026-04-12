<h1 align="center">
Wallpaper Engine Configurator
</h1>

<img src="https://github.com/user-attachments/assets/a8a23028-b0c5-4c43-a96d-c3e8ce446f3e" title="Wallpaper Engine Configurator"/>

Graphical configurator for [Linux-WallpaperEngine](https://github.com/Almamu/linux-wallpaperengine), compatible with multi-monitor setups.
It requires the Official Wallpaper Engine installed on Steam and wallpapers downloaded from the Steam Workshop.

## Features

- **Multi-Monitor Support**: Automatically detects connected screens via `xrandr`, `wlr-randr`, or `swaymsg`.
- **Per-Screen Assignment**: Assign different wallpapers to each monitor independently.
- **Advanced Configuration**: Adjust FPS, volume, mute, scaling, and more for each individual screen.
- **Wallpaper Properties**: Support for user-configurable properties (customize colors, sliders, and checkboxes of your wallpapers).
- **Startup Script Generation**: Creates a robust `start-wallpaperengine.sh` that adapts to screen changes.
- **Autostart Support**: Easily enable/disable autostart via a `.desktop` entry.
- **Preview & Details**: View wallpaper previews and metadata directly in the app.
- **Modern UI**: Built with PySide6 (Qt) featuring a built-in Light/Dark theme toggle.
- **Standalone Installation**: Includes scripts to build and install the app as a system-wide executable.

## Requirements

- **Python 3.11+**
- **Dependencies**: `psutil`, `PySide6`, `Pillow`, `requests`, `pyqtdarktheme`
- **Linux Wallpaper Engine**: Must be installed and available in your PATH (`linux-wallpaperengine`).
- **Screen Tools**: `xrandr` (X11), `wlr-randr` or `swaymsg` (Wayland).
- **Steam**: Official Wallpaper Engine and subscribed wallpapers.

## Installation

### 1. Clone the repository
```bash
git clone https://github.com/eriosgamer/linux-wallpaperengine-configurator.git
cd linux-wallpaperengine-configurator
```

### 2. Setup environment (Recommended)
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Run or Install
You can run the script directly:
```bash
python3 WallpaperEngineConfigurator.py
```
Or install it permanently (this will compile a standalone binary and add it to your applications menu):
```bash
./install.sh
```

## Screen Compatibility & Identification

- **X11**: Displays small overlays on each screen to identify them.
- **Wayland (Hyprland, Sway, etc.)**: Uses a **Monitor Map** simulation showing monitor positions and sizes, as compositors often restrict window placement.
- Use the **Identify Monitors** button in the UI to help locate your displays.

## Usage

1. Use **Identify Monitors** to see your screen layout.
2. Select a wallpaper from the list.
3. Click on the screen button (e.g., `>> HDMI-A-1`) to assign it.
4. Use **Config** for performance settings (FPS, etc.) or **Properties** to customize the wallpaper appearance.
5. Enable **Autostart** if you want the wallpapers to load on login.

## Logs and Support

Logs are saved in `/tmp/wallpaper-engine.log` and can be viewed directly from the interface using the **View Logs** button.

## License

This project is licensed under the Creative Commons BY-NC-ND License. See the [LICENSE](LICENSE) file for details.

---
**Author:** eriosgamer
