from PySide6.QtWidgets import QMessageBox, QScrollArea, QWidget, QFormLayout, QVBoxLayout, QDialog, QCheckBox, QSpinBox, \
    QDoubleSpinBox, QLineEdit, QDialogButtonBox, QPushButton, QColorDialog

from Files.wallpaper_properties import load_wallpaper_properties
from Scripts.config_setter import apply_changes_automatically
from UI.UI_Tools import we_to_qt_color, qt_to_we_color


def wallpaper_property_setup(self, screen):
    from Scripts.start_script import load_config_from_script
    """Open a dialog to configure properties of the assigned wallpaper for a specific Screen"""
    wallpaper_id = self.selected_wallpapers.get(screen)
    if not wallpaper_id:
        QMessageBox.warning(self, "No wallpaper assigned",
                            f"No wallpaper assigned to {screen}. Please assign one first.")
        return

    wallpaper_info = self.wallpapers.get(wallpaper_id)
    if not wallpaper_info:
        QMessageBox.warning(self, "Wallpaper not found", f"Wallpaper info not found for ID: {wallpaper_id}")
        return

    # Ensure screen_configs entry exists with defaults
    if screen not in self.screen_configs:
        file_configs = load_config_from_script(self)
        if screen in file_configs:
            self.screen_configs[screen] = file_configs[screen]
        else:
            self.screen_configs[screen] = {
                "fps": 30,
                "volume": 15,
                "silent": True,
                "scaling": "fill",
                "noautomute": False,
                "no_audio_proc": False,
                "clamp": "border",
                "mouse": True,
                "parallax": True,
                "fs_pause": True,
            }

    base_properties = load_wallpaper_properties(self, wallpaper_id)

    saved_props = self.screen_configs.get(screen, {}).get("properties", {})
    if not isinstance(saved_props, dict):
        saved_props = {}

    # Create a dialog to show properties
    dialog = QDialog(self)
    dialog.setWindowTitle(f"Properties: {wallpaper_info['title']}")
    dialog.resize(600, 700)

    main_vlayout = QVBoxLayout(dialog)

    # Scroll Area Setup
    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll_content = QWidget()
    form_layout = QFormLayout(scroll_content)
    scroll.setWidget(scroll_content)

    main_vlayout.addWidget(scroll)

    property_widgets = {}

    def safe_float(value, default=0.0):
        """Safely convert any value to float, handling 'None' and other issues."""
        if value is None or str(value).lower() == "none" or str(value).strip() == "":
            return default
        try:
            return float(value)
        except (ValueError, TypeError):
            return default

    for key, prop in base_properties.items():
        # Usar el valor guardado si existe, si no, usar el del motor (base)
        current_val = saved_props.get(key, prop.get("value"))
        p_type = prop["type"].lower()
        label_text = prop.get("text", key)  # Usar el texto descriptivo si existe

        if p_type == "boolean":
            widget = QCheckBox()
            # El motor devuelve "1" para true o "0" para false a veces
            widget.setChecked(str(current_val).lower() in ["true", "1"])
        elif p_type == "int":
            widget = QSpinBox()
            widget.setRange(-10000, 10000)
            widget.setValue(int(safe_float(current_val)))
        elif p_type == "float":
            widget = QDoubleSpinBox()
            widget.setRange(-10000.0, 10000.0)
            widget.setValue(safe_float(current_val))
        elif p_type == "slider":
            # Sliders are usually floats in WE
            widget = QDoubleSpinBox()
            p_min = safe_float(prop.get("min"), 0.0)
            p_max = safe_float(prop.get("max"), 100.0)
            p_step = safe_float(prop.get("step"), 0.1)
            widget.setRange(p_min, p_max)
            widget.setSingleStep(p_step)
            widget.setValue(safe_float(current_val, p_min))
        elif p_type == "color":
            # Botón que actúa como selector y muestra el color
            color_btn = QPushButton()
            initial_color_str = str(current_val) if current_val and str(current_val).lower() != "none" else "1,1,1"
            initial_color = we_to_qt_color(self, initial_color_str)

            # Estilo para que el botón tenga el color de fondo
            def update_btn_style(btn, color):
                btn.setStyleSheet(
                    f"background-color: {color.name()}; border: 1px solid #555; height: 25px;"
                )

            update_btn_style(color_btn, initial_color)

            # Guardamos el valor actual en un atributo del widget para leerlo después
            color_btn.setProperty("we_value", initial_color_str)

            def pick_color(btn_obj):
                current = we_to_qt_color(self, btn_obj.property("we_value"))
                new_color = QColorDialog.getColor(current, dialog, "Select Color")
                if new_color.isValid():
                    update_btn_style(btn_obj, new_color)
                    btn_obj.setProperty("we_value", qt_to_we_color(self, new_color))

            color_btn.clicked.connect(lambda _, b=color_btn: pick_color(b))
            widget = color_btn
        else:
            widget = QLineEdit(str(current_val) if current_val is not None else "")

        form_layout.addRow(label_text, widget)
        property_widgets[key] = (widget, p_type)

    # Save button
    btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
    btns.accepted.connect(dialog.accept)
    btns.rejected.connect(dialog.reject)
    main_vlayout.addWidget(btns)

    if dialog.exec() == QDialog.DialogCode.Accepted:
        new_props = {}
        for key, (widget, p_type) in property_widgets.items():
            if p_type == "boolean":
                val = 1 if widget.isChecked() else 0
            elif p_type in ["int", "float", "slider"]:
                val = widget.value()
            elif p_type == "color":
                val = widget.property("we_value")
            else:
                val = widget.text()

            # Check if it differs from the base (default) value
            base_val_raw = base_properties[key].get("value")

            if p_type == "boolean":
                norm_base = 1 if str(base_val_raw).lower() in ["1", "true"] else 0
                is_changed = (val != norm_base)
            elif p_type == "int":
                try:
                    is_changed = (int(safe_float(val)) != int(safe_float(base_val_raw)))
                except:
                    is_changed = True
            elif p_type in ["float", "slider"]:
                try:
                    is_changed = abs(safe_float(val) - safe_float(base_val_raw)) > 0.0001
                except:
                    is_changed = True
            elif p_type == "color":
                c1 = we_to_qt_color(self, str(val))
                c2 = we_to_qt_color(self,
                    str(base_val_raw) if base_val_raw and str(base_val_raw).lower() != 'none' else "1,1,1")
                is_changed = (c1 != c2)
            else:
                is_changed = (str(val) != str(base_val_raw))

            if is_changed:
                new_props[key] = val

        # Guardar en el diccionario global del configurador
        if screen not in self.screen_configs:
            self.screen_configs[screen] = {}

        self.screen_configs[screen]["properties"] = new_props

        # Aplicar cambios al script .sh y reiniciar
        apply_changes_automatically(self)
