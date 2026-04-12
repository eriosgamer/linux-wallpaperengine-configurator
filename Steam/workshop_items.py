import json
import os
from PySide6.QtWidgets import QListWidgetItem, QLabel
from PySide6.QtCore import Qt
import re

from Files.config_files import load_current_config
from UI.UI_Tools import normalize_text
from Wallpaper_Engine.support_types import is_wallpaper_supported


def load_wallpapers(self):
    """
    Scan the wallpaper directory and populate self.wallpapers with available wallpapers.
    """
    from UI.user_interface import update_screen_status

    self.wallpapers.clear()
    if not os.path.exists(self.wallpaper_base_path):
        print(f"Wallpaper directory does not exist: {self.wallpaper_base_path}")
        return
    for wid in os.listdir(self.wallpaper_base_path):
        wpath = os.path.join(self.wallpaper_base_path, wid)
        if os.path.isdir(wpath):
            load_wallpaper_info(self, wid, wpath)
    # Optionally update the UI list if needed
    if hasattr(self, "wallpaper_list"):
        self.wallpaper_list.clear()
        sorted_wallpapers = sorted(
            self.wallpapers.items(), key=lambda x: x[1]["title"].lower()
        )
        for wallpaper_id, info in sorted_wallpapers:
            # Detect CJK characters in the title
            def highlight_cjk(text):
                # Regex for CJK Unified Ideographs
                def repl(m):
                    return f'<span style="color:blue;">{m.group(0)}</span>'

                return re.sub(
                    r"[\u4e00-\u9fff\u3040-\u30ff\u3400-\u4dbf\uac00-\ud7af]+",
                    repl,
                    text,
                )

            title_html = highlight_cjk(info["title"])
            display_text = f"{title_html} (ID: {wallpaper_id})"
            item = QListWidgetItem()
            if not info.get("supported", True):
                reason = info.get("unsupported_reason", "")
                html = (
                    f"{title_html} (ID: {wallpaper_id}) "
                    f'<span style="color:red;">[NOT SUPPORTED:</span> '
                    f'<span style="color:orange;">{reason}</span>'
                    f'<span style="color:red;">]</span>'
                )
                item.setData(Qt.ItemDataRole.DisplayRole, "")
                item.setData(Qt.ItemDataRole.UserRole, html)
            else:
                item.setData(Qt.ItemDataRole.UserRole, display_text)
            self.wallpaper_list.addItem(item)
        # Set rich text for all items
        for i in range(self.wallpaper_list.count()):
            item = self.wallpaper_list.item(i)
            html = item.data(Qt.ItemDataRole.UserRole)
            if html:
                label = QLabel()
                label.setTextFormat(Qt.TextFormat.RichText)
                label.setText(html)
                self.wallpaper_list.setItemWidget(item, label)
    # After wallpapers are loaded, load config and update UI
    load_current_config(self)
    update_screen_status(self)

def load_wallpaper_info(self, wallpaper_id, wallpaper_path):
    """Load info of a specific wallpaper with better encoding handling"""
    project_json = os.path.join(wallpaper_path, "project.json")
    preview_jpg = os.path.join(wallpaper_path, "preview.jpg")
    preview_gif = os.path.join(wallpaper_path, "preview.gif")

    info = {
        "id": wallpaper_id,
        "path": wallpaper_path,
        "title": wallpaper_id,
        "description": "",
        "preview": None,
        "supported": True,
        "unsupported_reason": "",
    }

    # Read JSON if it exists
    if os.path.exists(project_json):
        try:
            # Read with UTF-8 directly
            with open(project_json, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Get RAW title and description, next normalize them
            raw_title = data.get("title", wallpaper_id)
            raw_description = data.get("description", "")

            info["title"] = (
                normalize_text(raw_title) if raw_title else wallpaper_id
            )
            info["description"] = (
                normalize_text(raw_description) if raw_description else ""
            )

        except Exception as e:
            print(f"Error reading JSON for {wallpaper_id}: {e}")
            info["title"] = wallpaper_id
            info["description"] = ""

    # Load preview if it exists
    if os.path.exists(preview_jpg):
        info["preview"] = preview_jpg
    elif os.path.exists(preview_gif):
        info["preview"] = preview_gif

    # Verifica si es apto para linux-wallpaperengine
    supported, reason = is_wallpaper_supported(wallpaper_path)
    info["supported"] = supported
    info["unsupported_reason"] = reason

    self.wallpapers[wallpaper_id] = info
