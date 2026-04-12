from PySide6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QGroupBox, QSpinBox, QCheckBox, QComboBox, \
    QDialogButtonBox

from Scripts.config_setter import apply_changes_automatically


def config_wallpaper(self, screen_name):
    from Scripts.start_script import load_config_from_script
    if screen_name not in self.screen_configs:
        file_configs = load_config_from_script(self)
        if screen_name in file_configs:
            self.screen_configs[screen_name] = file_configs[screen_name]
    defaults = {
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
    cfg = self.screen_configs.get(screen_name, defaults)

    dialog = QDialog(self)
    dialog.setWindowTitle(f"Configuración Avanzada: {screen_name}")
    main_layout = QVBoxLayout(dialog)
    form = QFormLayout()

    # --- Audio Section ---
    audio_group = QGroupBox("Audio")
    audio_form = QFormLayout(audio_group)
    vol_spin = QSpinBox()
    vol_spin.setRange(0, 100)
    vol_spin.setValue(cfg["volume"])
    silent_cb = QCheckBox("Mute (--silent)")
    silent_cb.setChecked(cfg["silent"])
    automute_cb = QCheckBox("Disable Automute")
    automute_cb.setChecked(cfg["noautomute"])
    audio_proc_cb = QCheckBox("Disable Audio Processing")
    audio_proc_cb.setChecked(cfg["no_audio_proc"])
    audio_form.addRow("Volumen:", vol_spin)
    audio_form.addRow(silent_cb)
    audio_form.addRow(automute_cb)
    audio_form.addRow(audio_proc_cb)

    # --- Performance & Behavior Section ---
    perf_group = QGroupBox("Performance")
    perf_form = QFormLayout(perf_group)
    fps_spin = QSpinBox()
    fps_spin.setRange(1, 144)
    fps_spin.setValue(cfg["fps"])
    mouse_cb = QCheckBox("Enable Mouse Interaction")
    mouse_cb.setChecked(cfg["mouse"])
    parallax_cb = QCheckBox("Enable Parallax")
    parallax_cb.setChecked(cfg["parallax"])
    fs_pause_cb = QCheckBox("Pause on Fullscreen")
    fs_pause_cb.setChecked(cfg["fs_pause"])
    perf_form.addRow("Max FPS:", fps_spin)
    perf_form.addRow(mouse_cb)
    perf_form.addRow(parallax_cb)
    perf_form.addRow(fs_pause_cb)

    # --- Visual Section ---
    visual_group = QGroupBox("Visual")
    visual_form = QFormLayout(visual_group)
    scaling_combo = QComboBox()
    scaling_combo.addItems(["fill", "fit", "stretch", "default"])
    scaling_combo.setCurrentText(cfg["scaling"])
    clamp_combo = QComboBox()
    clamp_combo.addItems(["border", "clamp", "repeat"])
    clamp_combo.setCurrentText(cfg["clamp"])
    visual_form.addRow("Scaling:", scaling_combo)
    visual_form.addRow("Clamping:", clamp_combo)

    main_layout.addWidget(audio_group)
    main_layout.addWidget(perf_group)
    main_layout.addWidget(visual_group)

    buttons = QDialogButtonBox(
        QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
    )
    buttons.accepted.connect(dialog.accept)
    buttons.rejected.connect(dialog.reject)
    main_layout.addWidget(buttons)

    if dialog.exec() == QDialog.DialogCode.Accepted:
        # 1. Def of GLOBAL and LOCAL keys
        global_keys = [
            "fps",
            "volume",
            "silent",
            "noautomute",
            "no_audio_proc",
            "fs_pause",
            "clamp",
            "mouse",
            "parallax",
        ]
        local_keys = ["scaling"]

        # 2. Recopilamos los nuevos valores del diálogo
        new_config = {
            "fps": fps_spin.value(),
            "volume": vol_spin.value(),
            "silent": silent_cb.isChecked(),
            "noautomute": automute_cb.isChecked(),
            "no_audio_proc": audio_proc_cb.isChecked(),
            "scaling": scaling_combo.currentText(),
            "clamp": clamp_combo.currentText(),
            "mouse": mouse_cb.isChecked(),
            "parallax": parallax_cb.isChecked(),
            "fs_pause": fs_pause_cb.isChecked(),
        }
        # 3. Sync: Apply global keys to all the screens
        for s_name in getattr(self, "detected_screens", []):
            # If the Screen not exist in the dict, we set the default keys
            if s_name not in self.screen_configs:
                self.screen_configs[s_name] = defaults.copy()

            # Update only for global keys
            for key in global_keys:
                self.screen_configs[s_name][key] = new_config[key]

        # 4. Custom: apply local keys only for the Screen
        for key in local_keys:
            self.screen_configs[screen_name][key] = new_config[key]

        # 5. Regen script and apply changes
        apply_changes_automatically(self)
