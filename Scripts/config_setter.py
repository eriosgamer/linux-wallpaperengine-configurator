import os

from PySide6.QtWidgets import QMessageBox, QApplication

from Files.config_files import save_current_config
from Screen.screen_detection import detect_screens


from Wallpaper_Engine.process_manager import stop_wallpaper_engine, start_wallpaper_engine, check_wallpaper_process


def assign_and_apply(self, screen_name):
    from UI.user_interface import update_screen_status
    """Assign wallpaper to a Screen and automatically apply changes"""
    if self.current_selection is None:
        QMessageBox.warning(
            self,
            "No selection",
            "Please select a wallpaper from the list first.",
        )
        return

    # Assign the wallpaper
    self.selected_wallpapers[screen_name] = self.current_selection
    save_current_config(self, screen_name, self.current_selection)  # Save config after assignment
    update_screen_status(self)
    # If we reach here, all screens have assigned wallpapers
    apply_changes_automatically(self)

def unassign_wallpaper(self, screen_name):
    from UI.user_interface import update_screen_status
    from Scripts.start_script import update_script_with_assigned_screens
    """Unassign the wallpaper from a Screen and update the status"""
    self.selected_wallpapers[screen_name] = None
    save_current_config(self, screen_name, None)  # Save config after unassignment
    update_screen_status(self)
    # Optionally: stop the engine if there are no wallpapers assigned
    assigned = [s for s in self.detected_screens if self.selected_wallpapers.get(s)]
    if not assigned:
        stop_wallpaper_engine(self)
    else:
        wallpaper_paths = {}
        for screen in assigned:
            wallpaper_id = self.selected_wallpapers.get(screen)
            if wallpaper_id:
                wallpaper_paths[screen] = os.path.join(
                    self.wallpaper_base_path, wallpaper_id
                )
        update_script_with_assigned_screens(self, wallpaper_paths)
        start_wallpaper_engine(self)
    # Update the UI
    update_screen_status(self)

def apply_changes_automatically(self):
    from Scripts.start_script import update_script_with_assigned_screens
    """Automatically apply changes when at least one Screen is configured"""
    # Detect screens again in case the session changed (e.g., xrdp vs physical session)
    self.detected_screens = detect_screens(self)

    # Check that at least one wallpaper is assigned
    assigned_screens = [
        s for s in self.detected_screens if self.selected_wallpapers.get(s)
    ]
    if not assigned_screens:
        QMessageBox.warning(
            self,
            "No wallpapers assigned",
            "Please assign at least one wallpaper to a Screen before applying changes.",
        )
        return

    # Check that assigned wallpapers exist
    wallpaper_paths = {}
    for screen in assigned_screens:
        wallpaper_id = self.selected_wallpapers.get(screen)
        if wallpaper_id is None:
            QMessageBox.critical(
                self,
                "Error",
                f"No wallpaper assigned for {screen}.",
            )
            return

        wallpaper_path = os.path.join(self.wallpaper_base_path, wallpaper_id)
        if not os.path.exists(wallpaper_path):
            QMessageBox.critical(
                self,
                "Error",
                f"Wallpaper for {screen} does not exist: {wallpaper_path}",
            )
            return

        wallpaper_paths[screen] = wallpaper_path

    # Update interface
    QApplication.processEvents()

    try:
        # Step 1: Stop wallpaper engine if running
        was_running = check_wallpaper_process(self)
        if was_running:
            stop_wallpaper_engine(self)

        # Step 2: Update script configuration (only with assigned screens)
        update_script_with_assigned_screens(self, wallpaper_paths)

        # Step 3: Restart wallpaper engine
        QApplication.processEvents()

        start_wallpaper_engine(self)

        # Show confirmation
        success_lines = ["Wallpapers applied successfully:\n"]
        for screen in self.detected_screens:
            wallpaper_id = self.selected_wallpapers.get(screen)
            if wallpaper_id is not None and wallpaper_id in self.wallpapers:
                title = self.wallpapers[wallpaper_id]["title"]
                success_lines.append(
                    f"✓ {screen}: {title[:30]}{'...' if len(title) > 30 else ''}"
                )
            else:
                success_lines.append(f"○ {screen}: Not assigned")

        QMessageBox.information(
            self,
            "Changes Applied",
            "\n".join(success_lines),
        )

    except Exception as e:
        QMessageBox.critical(
            self,
            "Error",
            f"Error applying changes: {e}",
        )
