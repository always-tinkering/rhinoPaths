---
description: How to package Rhino 8 Grasshopper plugins using the rhinocode CLI
---
# Building Rhino 8 Grasshopper Plugins (`rhinocode`)

When creating a Grasshopper plugin in Rhino 8, we build out of a `.rhproj` (Script Editor Project) file rather than manually distributing `.ghuser` or `.ghx` files. The project file serves as the plugin manifest and compiler configuration.

## Requirements
1. **Source Definitions**: The user provides `.gh` definitions that contain Script/Contextual components.
2. **Project File**: A `.rhproj` JSON file that maps those definitions into a compiled `.yak` or `.rhp`.
3. **Compilation**: Using the `rhinocode` CLI to execute the build.

## Workflow Steps

1. Setup the project configuration (`rhinoPaths.rhproj`):
This JSON metadata structure includes plugin identity and source `.gh` files wrapper. Example `.rhproj`:
```json
{
  "id": "A4181B5E-32E1-4BE5-A2DA-23C2A3C1BEA1",
  "identity": {
    "name": "rhinoPaths",
    "version": "0.1.0",
    "publisher": "Your Name"
  },
  "settings": {
    "buildPath": "build/",
    "buildTarget": {
      "host": { "name": "Rhino3D", "version": "8.0" }
    }
  },
  "source": {
    "scripts": [
      { "location": "src/gh_components/rhinoPaths_components.gh" }
    ]
  }
}
```

2. Command to compile:
Run the `rhinocode project build` command, which processes the `.rhproj` file:
```bash
# macOS default path
/Applications/Rhino\ 8.app/Contents/Resources/bin/rhinocode project build path/to/project.rhproj
```
*(On Windows: `C:\Program Files\Rhino 8\System\rhinocode.exe project build ...`)*

3. Deliver the `.yak` file containing the compiled `rhp`/`gha` package.

## Constraints
- Do not attempt to modify Grasshopper canvas structures via XML injection unless absolutely unavoidable. Rely on the user providing `.gh` source components, which you can augment in Python, and the RhinoCode compiler takes over from there.
