import os

import qdarktheme
from PySide6.QtGui import QFont, QPalette
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QListWidget, QTextEdit, QGroupBox, \
    QGridLayout, QDoubleSpinBox, QSlider

from Files.log_manager import view_logs
from Scripts.config_setter import assign_and_apply, unassign_wallpaper
from Steam.screen_tools import identify_monitors
from UI.config_interface import config_wallpaper
from UI.properties_interface import wallpaper_property_setup
from UI.wallpaper_list import on_wallpaper_select

def update_listboxes(self):
    """Update the wallpaper list in the QListWidget (Qt version)"""
    if hasattr(self, "wallpaper_list"):
        self.wallpaper_list.clear()
        sorted_wallpapers = sorted(
            self.wallpapers.items(), key=lambda x: x[1]["title"].lower()
        )
        for wallpaper_id, info in sorted_wallpapers:
            display_text = f"{info['title']} (ID: {wallpaper_id})"
            if not info.get("supported", True):
                display_text += f" [NOT SUPPORTED: {info['unsupported_reason']}]"
            self.wallpaper_list.addItem(display_text)
        # Highlight the current selection if it exists
        if self.current_selection is not None:
            for idx, (wallpaper_id, _) in enumerate(sorted_wallpapers):
                if wallpaper_id == self.current_selection:
                    self.wallpaper_list.setCurrentRow(idx)
                    break
    # Update Screen status
    update_screen_status(self)

def update_info_text(self, text):
    """
    Update the info_text QTextEdit widget with the provided text.
    """
    if hasattr(self, "info_text"):
        self.info_text.setPlainText(text)

def setup_fonts(self):
    """Configure fonts that support Unicode/CJK characters in Qt."""
    # List of fonts that typically support CJK
    font_candidates = [
        "Noto Sans CJK SC",  # Specific for Simplified Chinese
        "Noto Sans CJK TC",  # Specific for Traditional Chinese
        "Noto Sans CJK JP",  # Specific for Japanese
        "Noto Sans CJK",
        "Noto Nerd",
        "Source Han Sans",
        "WenQuanYi Micro Hei",
        "DejaVu Sans",
        "Liberation Sans",
        "Arial Unicode MS",
        "Unifont",
        "FreeSans",
        "Arial",
    ]

    from PySide6.QtGui import QFontDatabase

    available_fonts = QFontDatabase().families()
    self.unicode_font = None

    for font_name in font_candidates:
        if font_name in available_fonts:
            self.unicode_font = font_name
            break

    # Fallback: force Unifont if no CJK font found
    if not self.unicode_font:
        print("Available fonts:", available_fonts)
        if "Unifont" in available_fonts:
            self.unicode_font = "Unifont"
        elif "Arial" in available_fonts:
            self.unicode_font = "Arial"
            print("Warning: No CJK font found. Using Arial as fallback.")
        else:
            self.unicode_font = QFontDatabase.systemFont(
                QFontDatabase.SystemFont.GeneralFont
            ).family()
            print(
                "Warning: No CJK/Arial/Unifont font found. Using system default font."
            )

    print(f"Using font: {self.unicode_font}")

def setup_ui(self):
    from Steam.workshop_items import load_wallpapers
    from Scripts.start_script import view_script, manage_autostart


    # Remove previous widgets if they exist
    central = QWidget()
    self.setCentralWidget(central)
    main_layout = QVBoxLayout(central)

    # Title
    title = QLabel(
        f"Wallpaper Configurator - {len(self.detected_screens)} Screen(s) detected"
    )
    title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
    main_layout.addWidget(title)

    top_layout = QHBoxLayout()

    # System info
    info_lines = [
        f"Directory: {self.wallpaper_base_path}",
        f"Screens: {', '.join(self.detected_screens)}",
        f"Script: {self.script_path}",
        f"Autostart: {'Configured' if os.path.exists(self.autostart_path) else 'Not configured'}",
    ]
    info_label = QLabel("\n".join(info_lines))
    info_label.setStyleSheet("color: gray; font-size: 10px;")

    top_layout.addWidget(info_label)
    top_layout.addStretch()

    # Theme selector slider
    theme_layout = QHBoxLayout()

    label_dark = QLabel("🌙 Dark")
    label_light = QLabel("☀️ Light")

    self.theme_slider = QSlider(Qt.Orientation.Horizontal)
    self.theme_slider.setRange(0, 1)
    self.theme_slider.setSingleStep(1)
    self.theme_slider.setValue(0)  # Inicia en dark

    theme_layout.addWidget(label_dark)
    theme_layout.addWidget(self.theme_slider)
    theme_layout.addWidget(label_light)
    self.theme_slider.setTickInterval(1)

    def toggle_theme(event):
        current = self.theme_slider.value()
        self.theme_slider.setValue(1 - current)

    self.theme_slider.mousePressEvent = toggle_theme

    def change_theme(value):
        if value == 0:
            qdarktheme.setup_theme("dark")
        else:
            qdarktheme.setup_theme("light")
        update_screen_status(self)

    self.theme_slider.valueChanged.connect(change_theme)

    theme_widget = QWidget()
    theme_widget.setLayout(theme_layout)

    top_layout.addWidget(theme_widget)
    main_layout.addLayout(top_layout)


    # Top utility panel
    util_layout = QHBoxLayout()
    btn_identify = QPushButton("Identify Monitors")
    btn_identify.clicked.connect(lambda: identify_monitors(self))
    util_layout.addWidget(btn_identify)
    btn_refresh = QPushButton("Refresh List")
    btn_refresh.clicked.connect(lambda: load_wallpapers(self))
    util_layout.addWidget(btn_refresh)
    btn_script = QPushButton("View Script")
    btn_script.clicked.connect(lambda: view_script(self))
    util_layout.addWidget(btn_script)
    btn_autostart = QPushButton("Config Autostart")
    btn_autostart.clicked.connect(lambda: manage_autostart(self))
    util_layout.addWidget(btn_autostart)
    btn_logs = QPushButton("View Logs")
    btn_logs.clicked.connect(lambda: view_logs(self))
    util_layout.addWidget(btn_logs)
    main_layout.addLayout(util_layout)

    # Central panel (wallpapers and preview)
    content_layout = QHBoxLayout()
    # Wallpaper list
    self.wallpaper_list = QListWidget()
    self.wallpaper_list.itemSelectionChanged.connect(lambda: on_wallpaper_select(self))
    content_layout.addWidget(self.wallpaper_list, 2)
    # Right panel: preview and info
    right_panel = QVBoxLayout()
    self.preview_label = QLabel("Select a wallpaper")
    self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    self.preview_label.setFixedSize(320, 180)
    right_panel.addWidget(self.preview_label)
    self.info_text = QTextEdit()
    self.info_text.setReadOnly(True)
    right_panel.addWidget(self.info_text)
    content_layout.addLayout(right_panel, 1)
    main_layout.addLayout(content_layout)

    # Bottom panel: assignment and status
    bottom_layout = QHBoxLayout()
    # Assign wallpapers to screens
    assign_group = QGroupBox("Assign to Screen")
    assign_layout = QGridLayout()
    for idx, screen in enumerate(self.detected_screens):
        btn_assign = QPushButton(f">> {screen}")
        btn_assign.clicked.connect(
            lambda checked, s=screen: assign_and_apply(self, s)
        )
        assign_layout.addWidget(btn_assign, idx, 0)

        btn_unassign = QPushButton("Unassign")
        btn_unassign.clicked.connect(
            lambda checked, s=screen: unassign_wallpaper(self, s)
        )
        assign_layout.addWidget(btn_unassign, idx, 1)

        btn_config = QPushButton("Config")
        btn_config.clicked.connect(
            lambda checked, s=screen: config_wallpaper(self, s)
        )
        assign_layout.addWidget(btn_config, idx, 2)

        btn_properties = QPushButton("Properties")
        btn_properties.clicked.connect(
            lambda checked, s=screen: wallpaper_property_setup(self, s)
        )
        assign_layout.addWidget(btn_properties, idx, 3)

    assign_group.setLayout(assign_layout)
    bottom_layout.addWidget(assign_group)
    # Current status
    status_group = QGroupBox("Current status")
    self.status_labels = {}
    status_layout = QVBoxLayout()
    for screen in self.detected_screens:
        lbl = QLabel(f"{screen}: Not assigned")
        lbl.setStyleSheet("color: gray;")
        status_layout.addWidget(lbl)
        self.status_labels[screen] = lbl
    status_group.setLayout(status_layout)
    bottom_layout.addWidget(status_group)
    main_layout.addLayout(bottom_layout)

def get_title_color(self):
    return "#FFFFFF" if self.theme_slider.value() == 0 else "#000000"

def update_screen_status(self):
    """
    Update the status labels for each Screen to reflect the currently assigned wallpaper.
    """
    for screen in self.detected_screens:
        label = self.status_labels.get(screen)
        wallpaper_id = self.selected_wallpapers.get(screen)
        if label is not None:
            if wallpaper_id and wallpaper_id in self.wallpapers:
                title = self.wallpapers[wallpaper_id]["title"]

                color = get_title_color(self)

                label.setText(
                    f'<span style="color: green;">{screen}:</span> '
                    f'<span style="color: {color};">{title}</span>'
                )

            else:
                label.setText(f"{screen}: Not assigned")
                label.setStyleSheet("color: red;")
