import os
import subprocess
import sys


def load_wallpaper_properties(self, wallpaper_id):
    """Load properties of a specific wallpaper for configuration"""
    # Execute the command and parse the output
    try:
        # Crucial for stand-alone binaries (PyInstaller):
        # PyInstaller modifies LD_LIBRARY_PATH to point to its internal _MEI folder.
        # We need to restore the original system paths AND add the WE path.
        env = os.environ.copy()
        we_path = "/opt/linux-wallpaperengine"

        # 1. Clean LD_LIBRARY_PATH from PyInstaller's influence
        if getattr(sys, 'frozen', False):
            if 'LD_LIBRARY_PATH_ORIG' in env:
                env['LD_LIBRARY_PATH'] = env['LD_LIBRARY_PATH_ORIG']
            else:
                env.pop('LD_LIBRARY_PATH', None)

        # 2. Re-construct LD_LIBRARY_PATH carefully
        current_ld = env.get('LD_LIBRARY_PATH', '')
        paths = [
            we_path,
            os.path.join(we_path, "lib"),
            '/usr/lib',
            '/usr/local/lib',
            '/usr/lib/x86_64-linux-gnu',
            '/lib/x86_64-linux-gnu'
        ]
        if current_ld:
            paths.append(current_ld)

        env['LD_LIBRARY_PATH'] = ":".join([p for p in paths if os.path.exists(p)])

        # Check for the binary in common locations
        binary = os.path.join(we_path, "linux-wallpaperengine")
        if not os.path.exists(binary):
            binary = "linux-wallpaperengine"

        result = subprocess.run(
            [binary, "--list-properties", wallpaper_id],
            capture_output=True,
            text=True,
            timeout=5,
            env=env
        )
        if result.returncode != 0:
            print(f"Error listing properties for {wallpaper_id}: {result.stderr}")
            return {}

        properties = {}
        lines = result.stdout.strip().split("\n")
        current_key = None
        for line in lines:
            line = line.strip()
            if not line:
                continue
            if " - " in line:
                # New property
                parts = line.split(" - ", 1)
                if len(parts) == 2:
                    current_key = parts[0].strip()
                    properties[current_key] = {"type": parts[1].strip()}
            elif current_key:
                if line.startswith("Text:"):
                    properties[current_key]["text"] = line.split("Text:", 1)[1].strip()
                elif line.startswith("Value:"):
                    properties[current_key]["value"] = line.split("Value:", 1)[1].strip()
                elif line.startswith("Min:"):
                    properties[current_key]["min"] = line.split("Min:", 1)[1].strip()
                elif line.startswith("Max:"):
                    properties[current_key]["max"] = line.split("Max:", 1)[1].strip()
                elif line.startswith("Step:"):
                    properties[current_key]["step"] = line.split("Step:", 1)[1].strip()

        return properties
    except Exception as e:
        print(f"Error loading properties for {wallpaper_id}: {e}")
        return {}
