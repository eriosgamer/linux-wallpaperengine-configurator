
#!/bin/bash


# Script to compile wallpaper-config.py into a single executable (onefile)

set -e

MAIN_SCRIPT="wallpaper-config.py"
DIST_DIR="dist"

# Install PyInstaller if not present
if ! command -v pyinstaller &> /dev/null; then
	echo "PyInstaller not found. Installing..."
	# Check if inside a virtualenv
	if [ -n "$VIRTUAL_ENV" ]; then
		pip install pyinstaller
	else
		pip install --user pyinstaller
	fi
fi

# Clean previous builds
rm -rf build/ "$DIST_DIR"/ __pycache__/

# Build single-file executable
pyinstaller --onefile --distpath "$DIST_DIR" "$MAIN_SCRIPT"

echo -e "\nBuild finished. The executable is in $DIST_DIR/"
