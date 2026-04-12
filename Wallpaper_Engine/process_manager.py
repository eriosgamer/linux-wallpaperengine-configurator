import subprocess

import psutil


def check_wallpaper_process(self):
    """Check if wallpaper engine is running"""
    try:
        for proc in psutil.process_iter(["pid", "name", "cmdline"]):
            try:
                # Check by process name
                if (
                        proc.info["name"]
                        and "linux-wallpaperengine" in proc.info["name"]
                ):
                    return True

                # Check by command line (more reliable)
                if proc.info["cmdline"]:
                    cmdline_str = " ".join(proc.info["cmdline"])
                    if "linux-wallpaperengine" in cmdline_str:
                        return True

                # Also check the bash script that runs wallpaper engine
                if proc.info["name"] == "bash" and proc.info["cmdline"]:
                    cmdline_str = " ".join(proc.info["cmdline"])
                    if "start-wallpaperengine.sh" in cmdline_str:
                        return True

            except (
                    psutil.NoSuchProcess,
                    psutil.AccessDenied,
                    psutil.ZombieProcess,
            ):
                continue

    except Exception as e:
        print(f"Error checking processes: {e}")

    return False


def stop_wallpaper_engine(self):
    """Stop the wallpaper engine process"""
    import os

    stopped_processes = []
    current_pid = os.getpid()  # PID del proceso actual (python)
    try:
        for proc in psutil.process_iter(["pid", "name", "cmdline"]):
            try:
                process_found = False

                # Check by name
                if (
                        proc.info["name"]
                        and "linux-wallpaperengine" in proc.info["name"]
                ):
                    process_found = True

                # Check by command line
                if not process_found and proc.info["cmdline"]:
                    cmdline_str = " ".join(proc.info["cmdline"])
                    if "linux-wallpaperengine" in cmdline_str:
                        process_found = True

                # Also stop the bash script
                if (
                        not process_found
                        and proc.info["name"] == "bash"
                        and proc.info["cmdline"]
                ):
                    cmdline_str = " ".join(proc.info["cmdline"])
                    if "start-wallpaperengine.sh" in cmdline_str:
                        process_found = True

                # Evitar matar el proceso actual (python)
                if process_found and proc.info["pid"] != current_pid:
                    print(
                        f"Stopping process: {proc.info['name']} (PID: {proc.info['pid']})"
                    )
                    proc.terminate()
                    stopped_processes.append(proc.info["pid"])

            except (
                    psutil.NoSuchProcess,
                    psutil.AccessDenied,
                    psutil.ZombieProcess,
            ):
                continue

        # Wait for processes to finish
        if stopped_processes:
            import time

            time.sleep(2)

            # Check if still running and force termination
            for proc in psutil.process_iter(["pid", "name"]):
                try:
                    if proc.info["pid"] in stopped_processes and proc.is_running():
                        proc.kill()
                        print(
                            f"Forcing termination of process PID: {proc.info['pid']}"
                        )
                except (
                        psutil.NoSuchProcess,
                        psutil.AccessDenied,
                        psutil.ZombieProcess,
                ):
                    continue

        return len(stopped_processes) > 0

    except Exception as e:
        print(f"Error stopping wallpaper engine: {e}")
        return False


def start_wallpaper_engine(self):
    """Start wallpaper engine in the background"""
    try:
        print("Starting wallpaper engine...")

        # Run the script in the background
        process = subprocess.Popen(
            [self.script_path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )

        print(f"Script started with PID: {process.pid}")

        # Wait longer for the script to execute (it has sleep 5)
        import time

        print("Waiting for the script to initialize...")

        # Try to detect the process with longer intervals
        for attempt in range(15):  # 15 attempts over 15 seconds
            time.sleep(1)  # Wait 1 second between attempts

            if check_wallpaper_process(self):
                print(
                    f"✓ Wallpaper engine detected successfully (attempt {attempt + 1})"
                )
                return True

            # Show progress every 3 attempts
            if attempt % 3 == 2:
                print(f"Waiting... ({attempt + 1}/15 attempts)")

        # If we reach here, it was not detected in 15 seconds
        print("⚠ Wallpaper engine not detected in 15 seconds")

        # Check if the bash script is still running
        try:
            if process.poll() is None:  # The process is still running
                print(
                    "✓ The script is still running, probably started successfully"
                )
                return True
            else:
                print("✗ The script ended unexpectedly")
                return False
        except:
            print("✓ Assuming successful start")
            return True

    except Exception as e:
        print(f"Error starting wallpaper engine: {e}")
        return False
