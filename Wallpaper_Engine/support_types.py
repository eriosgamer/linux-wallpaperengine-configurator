import json
import os


def is_wallpaper_supported(wallpaper_path):
    """
    Analyze the wallpaper and determine if it is suitable for linux-wallpaperengine.
    Based on https://github.com/Almamu/linux-wallpaperengine and common errors.
    """
    project_json = os.path.join(wallpaper_path, "project.json")
    if not os.path.exists(project_json):
        return False, "No project.json"

    try:
        with open(project_json, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        return False, f"Error: {e}"

    wallpaper_type = data.get("type", "").lower()
    # Basic type check
    if wallpaper_type == "scene":
        if not (os.path.exists(os.path.join(wallpaper_path, "scene.json")) or os.path.exists(
            os.path.join(wallpaper_path, "scene.pkg"))):
            return False, "Missing scene.json/scene.pkg"
    elif wallpaper_type == "video":
        if not any(f.endswith(ext) for ext in (".mp4", ".webm", ".avi") for f in os.listdir(wallpaper_path)):
            return False, "Missing video file"
    elif wallpaper_type == "web":
        if not (os.path.exists(os.path.join(wallpaper_path, "scene.json")) or os.path.exists(
            os.path.join(wallpaper_path, "scene.pkg"))):
            return False, "Missing scene.json/scene.pkg"
    elif not wallpaper_type:
        return False, "No type specified in project.json"
    else:
        return False, f"Type '{wallpaper_type}' not supported"

    # Advanced check for problematic properties
    general = data.get("general")
    if isinstance(general, dict):
        props = general.get("properties", {})
    else:
        props = {}
    for key, prop in props.items():
        # Detect properties of type scenetexture
        if isinstance(prop, dict) and prop.get("type", "") == "scenetexture":
            return False, f"Property '{key}' type scenetexture not supported"
        # Detect unsupported animations
        if isinstance(prop, dict) and "animation" in prop.get("type", "").lower():
            return False, f"Property '{key}' with unsupported animation"
        # Detect composed materials
        if "material" in key.lower() and "compose" in prop.get("type", "").lower():
            return False, f"Composed material not supported ({key})"

    # Check shader files for common errors
    for fname in os.listdir(wallpaper_path):
        if fname.endswith((".frag", ".vert", ".glsl")):
            shader_path = os.path.join(wallpaper_path, fname)
            try:
                with open(shader_path, "r", encoding="utf-8", errors="ignore") as f:
                    shader_code = f.read()
                    # Look for common error patterns
                    if "cannot convert" in shader_code or "syntax error" in shader_code:
                        return False, f"Incompatible shader: {fname}"
            except Exception as e:
                print(f"Error reading shader {fname}: {e}")
                continue

    # Check required keys in particle emitters
    if "scene.json" in os.listdir(wallpaper_path):
        try:
            with open(os.path.join(wallpaper_path, "scene.json"), "r", encoding="utf-8") as f:
                scene_data = f.read()
                if "Particle emitter" in scene_data and "origin" not in scene_data:
                    return False, "Particle emitter without 'origin' (not supported)",
        except Exception as e:
            print(f"Error reading scene.json: {e}")
            pass

    # If everything is OK
    return True, ""
