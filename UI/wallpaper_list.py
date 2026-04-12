import os

from PIL import Image

def on_wallpaper_select(self):
    """Handle wallpaper selection in the list (Text widget version)"""
    # Get the index of the current selection in the Text widget
    try:
        # Get the current cursor position
        index = self.wallpaper_list.currentRow()
        sorted_wallpapers = sorted(
            self.wallpapers.items(), key=lambda x: x[1]["title"].lower()
        )
        if index >= 0 and index < len(sorted_wallpapers):
            wallpaper_id, wallpaper_info = sorted_wallpapers[index]
            self.current_selection = wallpaper_id
        else:
            self.current_selection = None
            return
    except Exception:
        self.current_selection = None
        return

    # Update preview with larger size
    if wallpaper_info["preview"]:
        try:
            image = Image.open(wallpaper_info["preview"])
            # If GIF, show first frame (Pillow handles animated GIFs)
            if getattr(image, "is_animated", False):
                image.seek(0)
            image.thumbnail((300, 170), Image.Resampling.LANCZOS)
            from PySide6.QtGui import QImage, QPixmap

            image = image.convert("RGBA")
            data = image.tobytes("raw", "RGBA")
            qimage = QImage(
                data, image.width, image.height, QImage.Format.Format_RGBA8888
            )
            pixmap = QPixmap.fromImage(qimage)
            self.preview_label.setPixmap(pixmap)
            self.preview_label.setText("")
            self._preview_photo = pixmap
        except Exception as e:
            print(f"Error loading preview image: {e}")
            from PySide6.QtGui import QPixmap

            self.preview_label.setPixmap(QPixmap())
            self.preview_label.setText("No preview")
    else:
        # Try loading preview from Steam Workshop if not found locally
        try:
            import requests

            steam_preview_url = f"https://steamcommunity.com/sharedfiles/filedetails/?id={wallpaper_id}"
            resp = requests.get(steam_preview_url, timeout=5)
            if resp.ok:
                import re

                match = re.search(
                    r'<img[^>]+id="previewImageMain"[^>]+src="([^"]+)"', resp.text
                )
                if match:
                    img_url = match.group(1)
                    from io import BytesIO

                    img_resp = requests.get(img_url, timeout=5)
                    if img_resp.ok:
                        try:
                            image = Image.open(BytesIO(img_resp.content))
                            # If GIF, show first frame (Pillow handles animated GIFs)
                            if getattr(image, "is_animated", False):
                                print(
                                    "No local preview found. Loading from Steam workshop."
                                )
                                image.seek(0)
                            image.thumbnail((300, 170), Image.Resampling.LANCZOS)
                            from PySide6.QtGui import QImage, QPixmap

                            image = image.convert("RGBA")
                            data = image.tobytes("raw", "RGBA")
                            qimage = QImage(
                                data,
                                image.width,
                                image.height,
                                QImage.Format.Format_RGBA8888,
                            )
                            pixmap = QPixmap.fromImage(qimage)
                            self.preview_label.setPixmap(pixmap)
                            self.preview_label.setText("")
                            self._preview_photo = pixmap
                        except Exception as e:
                            print(f"Error loading preview image: {e}")
                            from PySide6.QtGui import QPixmap

                            self.preview_label.setPixmap(QPixmap())
                            self.preview_label.setText("No preview")
                    else:
                        from PySide6.QtGui import QPixmap

                        self.preview_label.setPixmap(QPixmap())
                        self.preview_label.setText("No preview")
                else:
                    from PySide6.QtGui import QPixmap

                    self.preview_label.setPixmap(QPixmap())
                    self.preview_label.setText("No preview")
            else:
                print(f"Error fetching preview from Steam: {resp.status_code}")
                from PySide6.QtGui import QPixmap

                self.preview_label.setPixmap(QPixmap())
                self.preview_label.setText("No preview")
        except Exception:
            from PySide6.QtGui import QPixmap

            self.preview_label.setPixmap(QPixmap())
            self.preview_label.setText("No preview")

    # Update info WITHOUT processing the text
    title = wallpaper_info["title"]
    info_text = f"Title: {title}\n\nID: {wallpaper_id}"

    # Check wallpaper type
    wallpaper_path = wallpaper_info["path"]
    try:
        if os.path.exists(os.path.join(wallpaper_path, "scene.pkg")):
            info_text += "\n\nType: Animated Wallpaper"
        elif any(
                f.endswith((".mp4", ".webm", ".avi"))
                for f in os.listdir(wallpaper_path)
                if os.path.isfile(os.path.join(wallpaper_path, f))
        ):
            info_text += "\n\nType: Video"
        else:
            info_text += "\n\nType: Static Image"
    except:
        info_text += "\n\nType: Unknown"

    # Add description as is
    if wallpaper_info["description"]:
        description = wallpaper_info["description"]
        if len(description) > 200:
            description = description[:200] + "..."
        info_text += f"\n\nDescription:\n{description}"

    # Use the method to update text
    from UI.user_interface import update_info_text
    update_info_text(self, info_text)