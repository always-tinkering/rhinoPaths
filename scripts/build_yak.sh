#!/bin/bash
set -e

# Base directories
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DIST_DIR="$PROJECT_ROOT/dist"
YAK_STAGE_DIR="$DIST_DIR/yak"

echo "Building rhinoPaths Yak package..."

# 1. Clean and prepare staging directory
rm -rf "$YAK_STAGE_DIR"
mkdir -p "$YAK_STAGE_DIR/UserObjects"
mkdir -p "$YAK_STAGE_DIR/src"

# 2. Copy Grasshopper UserObjects
if [ -d "$PROJECT_ROOT/src/ghuser_components" ]; then
    cp "$PROJECT_ROOT/src/ghuser_components/"*.ghuser "$YAK_STAGE_DIR/UserObjects/"
else
    echo "Warning: src/ghuser_components/ not found. No .ghuser files will be packaged."
fi

# 3. Copy Python module
if [ -d "$PROJECT_ROOT/src/rhinopaths" ]; then
    cp -r "$PROJECT_ROOT/src/rhinopaths" "$YAK_STAGE_DIR/src/"
else
    echo "Error: src/rhinopaths/ not found."
    exit 1
fi

# 4. Copy Manifest
if [ -f "$PROJECT_ROOT/manifest.yml" ]; then
    cp "$PROJECT_ROOT/manifest.yml" "$YAK_STAGE_DIR/"
else
    echo "Error: manifest.yml not found in project root."
    exit 1
fi

# Clean up pycache inside src before building
find "$YAK_STAGE_DIR" -name "__pycache__" -type d -exec rm -rf {} +
find "$YAK_STAGE_DIR" -name "*.pyc" -type f -delete

# 5. Run Yak Build
cd "$YAK_STAGE_DIR"
"/Applications/Rhino 8.app/Contents/Resources/bin/yak" build

# 6. Move output to dist directory
mv *.yak "$DIST_DIR/"

echo "Success! Yak package created in $DIST_DIR"
