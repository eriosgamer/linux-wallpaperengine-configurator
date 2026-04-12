import sys
import subprocess
import shutil


def get_screen_detection_method(self):
    """Detect which monitor listing methods are available on the system"""
    # Priority: xrandr, wlr-randr, swaymsg
    if shutil.which("xrandr"):
        return "xrandr"
    elif shutil.which("wlr-randr"):
        return "wlr-randr"
    elif shutil.which("swaymsg"):
        return "swaymsg"
    else:
        return None


def detect_screens(self):
    """Automatically detect connected screens using available methods"""
    screens = []
    method = get_screen_detection_method(self)
    print(f"Screen detection method: {method}")

    if not method:
        print("No supported Screen detection method found.")
        sys.exit(1)

    try:
        if method == "xrandr":
            # Use xrandr to detect connected screens
            result = subprocess.run(
                ["xrandr", "--listmonitors"], capture_output=True, text=True
            )
            for line in result.stdout.split("\n"):
                line = line.strip()
                if not line or line.startswith("Monitors:"):
                    continue
                if ":" in line and "+" in line:
                    parts = line.split()
                    if len(parts) >= 2:
                        monitor_name = parts[-1]
                        if (
                                monitor_name
                                and not monitor_name.startswith("+")
                                and monitor_name not in ["Monitors:", ""]
                        ):
                            monitor_name = monitor_name.strip("*+")
                            if monitor_name and monitor_name not in screens:
                                screens.append(monitor_name)
            # Fallback to xrandr --query if none found
            if not screens:
                print("No screens detected with --listmonitors, trying --query...")
                result = subprocess.run(
                    ["xrandr", "--query"], capture_output=True, text=True
                )
                for line in result.stdout.split("\n"):
                    if " connected" in line:
                        screen_name = line.split()[0]
                        if screen_name and screen_name not in screens:
                            screens.append(screen_name)
                            print(f"Monitor detected with --query: {screen_name}")

        elif method == "wlr-randr":
            # Use wlr-randr to list outputs
            result = subprocess.run(["wlr-randr"], capture_output=True, text=True)
            print(f"wlr-randr output:\n{result.stdout}")
            for line in result.stdout.split("\n"):
                if " connected" in line or line.startswith("Output "):
                    # Example: Output HDMI-A-1 (connected)
                    parts = line.split()
                    if len(parts) >= 2:
                        screen_name = parts[1]
                        if screen_name and screen_name not in screens:
                            screens.append(screen_name)
                            print(f"Monitor detected with wlr-randr: {screen_name}")

        elif method == "swaymsg":
            # Use swaymsg to list outputs
            result = subprocess.run(
                ["swaymsg", "-t", "get_outputs"], capture_output=True, text=True
            )
            print(f"swaymsg output:\n{result.stdout}")
            import json

            try:
                outputs = json.loads(result.stdout)
                for output in outputs:
                    if output.get("active"):
                        screen_name = output.get("name")
                        if screen_name and screen_name not in screens:
                            screens.append(screen_name)
                            print(f"Monitor detected with swaymsg: {screen_name}")
            except Exception as e:
                print(f"Error parsing swaymsg output: {e}")

        # Filter out virtual or unwanted screens
        original_screens = screens.copy()
        screens = [
            s
            for s in screens
            if not any(
                x in s.lower()
                for x in ["virtual", "none", "disconnected", "unknown"]
            )
        ]
        if len(screens) != len(original_screens):
            filtered_out = set(original_screens) - set(screens)

    except Exception as e:
        print(f"Error detecting screens: {e}")
        sys.exit(1)

    if not screens:
        print("No screens detected.")
        sys.exit(1)

    screens.sort()
    print(f"Final detected screens: {screens}")
    return screens
