import os
import subprocess


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
    except Exception as e:
        print(f"Error getting the directory with find: {e}")

    # Fallback to default path
    default_path = f"/home/{os.getenv('USER')}/.local/share/Steam/steamapps/workshop/content/431960"
    print(f"Using default directory: {default_path}")
    return default_path
