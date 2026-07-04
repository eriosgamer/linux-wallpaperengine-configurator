#!/bin/bash

# Exit on error
set -e

APP_NAME="WallpaperEngineConfigurator"
BINARY_NAME="WallpaperEngineConfigurator"
INSTALL_BIN_DIR="$HOME/.local/bin"
INSTALL_APPS_DIR="$HOME/.local/share/applications"
INSTALL_ICONS_DIR="$HOME/.local/share/icons/hicolor/32x32/apps"
ICON_NAME="wallpaper-engine-configurator"

echo "--- Starting uninstall script ---"

if [ -f "$DIST_DIR/$BINARY_NAME" ]; then
    if [ -f "$INSTALL_BIN_DIR/$APP_NAME" ]; then
        echo "Existing version found. Removing binary at $INSTALL_BIN_DIR..."
        rm -f "$INSTALL_ICONS_DIR/$ICON_NAME.png"
        rm -f "$INSTALL_BIN_DIR/$APP_NAME"
        rm -f "$INSTALL_APPS_DIR/$APP_NAME.desktop"
        echo "Successful uninstallation"
    else
        echo "Binary not found at $INSTALL_BIN_DIR"
    fi
else
    echo "Error: Binary not found in $DIST_DIR"
    exit 1
fi