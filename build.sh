#!/usr/bin/env bash

# macOS path to Rhino 8's rhinocode CLI utility
RHINOCODE_CLI="/Applications/Rhino 8.app/Contents/Resources/bin/rhinocode"

if [ ! -x "$RHINOCODE_CLI" ]; then
    echo "Error: 'rhinocode' CLI not found or not executable at $RHINOCODE_CLI. Is Rhino 8 installed?"
    exit 1
fi

PROJECT_FILE="rhinoPaths.rhproj"

if [ ! -f "$PROJECT_FILE" ]; then
    echo "Error: Project file $PROJECT_FILE not found."
    echo "Please create a .rhproj file containing the plugin metadata and source components."
    exit 1
fi

echo "Building Rhino 8 plugin from $PROJECT_FILE ..."
"$RHINOCODE_CLI" project build "$PROJECT_FILE"

if [ $? -eq 0 ]; then
    echo "Build successful! Your .yak package should be in the build/ directory."
else
    echo "Build failed. Ensure the Rhino script server is running (StartScriptServer inside Rhino 8) and check the errors above."
    exit 1
fi
