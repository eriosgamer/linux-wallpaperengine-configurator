#!/bin/bash

# Exit on error
set -e

APP_NAME="WallpaperEngineConfigurator"
BINARY_NAME="WallpaperEngineConfigurator"
BUILD_SCRIPT="./build.sh"
DIST_DIR="dist"
INSTALL_BIN_DIR="$HOME/.local/bin"
INSTALL_APPS_DIR="$HOME/.local/share/applications"
INSTALL_ICONS_DIR="$HOME/.local/share/icons/hicolor/32x32/apps"
ICON_NAME="wallpaper-engine-configurator"

echo "--- Starting Installation/Update Process ---"

# 1. Run the build script
if [ -f "$BUILD_SCRIPT" ]; then
    echo "Compiling the executable..."
    bash "$BUILD_SCRIPT"
else
    echo "Error: $BUILD_SCRIPT not found"
    exit 1
fi

# 2. Create necessary directories if they don't exist
mkdir -p "$INSTALL_BIN_DIR"
mkdir -p "$INSTALL_APPS_DIR"
mkdir -p "$INSTALL_ICONS_DIR"

# 3. Extract/Update Icon
echo "Updating application icon..."
# We remove the old icon to ensure a clean extraction
rm -f "$INSTALL_ICONS_DIR/$ICON_NAME.png"
grep "icon_base64 =" Files/icon_file.py | cut -d'"' -f2 | base64 -d > "$INSTALL_ICONS_DIR/$ICON_NAME.png" || echo "Warning: Could not extract icon."

# 4. Copy/Update the binary
if [ -f "$DIST_DIR/$BINARY_NAME" ]; then
    if [ -f "$INSTALL_BIN_DIR/$APP_NAME" ]; then
        echo "Existing version found. Updating binary at $INSTALL_BIN_DIR..."
    else
        echo "Installing binary to $INSTALL_BIN_DIR..."
    fi
    # Use -f (force) to overwrite the existing binary even if it has different permissions
    cp -f "$DIST_DIR/$BINARY_NAME" "$INSTALL_BIN_DIR/$APP_NAME"
    chmod +x "$INSTALL_BIN_DIR/$APP_NAME"
else
    echo "Error: Binary not found in $DIST_DIR"
    exit 1
fi

# 5. Generate/Update the .desktop file
echo "Updating desktop entry..."
cat <<EOF > "$INSTALL_APPS_DIR/$APP_NAME.desktop"
[Desktop Entry]
Version=1.0
Type=Application
Name=Wallpaper Engine Configurator
Comment=Dynamic configuration tool for linux-wallpaperengine
Exec=$INSTALL_BIN_DIR/$APP_NAME
Icon=$ICON_NAME
Terminal=false
Categories=Settings;System;Qt;
Keywords=wallpaper;engine;config;
EOF

# 6. Refresh the system
echo "Refreshing system databases..."
if command -v update-desktop-database &> /dev/null; then
    update-desktop-database "$INSTALL_APPS_DIR"
fi

# 7. Final check
if [ -f "$INSTALL_BIN_DIR/$APP_NAME" ] && [ -f "$INSTALL_APPS_DIR/$APP_NAME.desktop" ]; then
    echo -e "\n--- Process Finished Successfully! ---"
    echo "The application has been updated to the latest version."
else
    echo -e "\n--- Process failed or incomplete ---"
    exit 1
fi