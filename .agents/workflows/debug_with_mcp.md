---
description: How to debug and test rhinoPaths components using MCP tools in Rhino and Grasshopper
---

# Agent-Driven Debugging with MCP Workflow

If you need to test or debug a feature in the `rhinoPaths` toolpath generation algorithm, use this workflow to interact directly with the Rhino/Grasshopper environment.

1. Ensure the UI components have been compiled with the latest python changes. (Optional depending on if we are testing python code or GH definitions)
   ```sh
   python3 scripts/generate_gh_plugin.py
   ```
2. Remind the user to ensure Rhino 8 is open, the `GH_MCP` component is on the canvas, and `_mcpstart` has been run.
3. Read the `plugin/mcp_knowledge.json` file to understand the inputs and outputs of the component you are trying to test.
4. Use the `rhinomcp` server to create a test geometry in the Rhino document (e.g., a simple planar curve or bounding box).
5. Use the `grasshopper-mcp` server to wire the test geometry into your target `rhinoPaths` component.
6. Trigger the compute cycle and read the outputs back via the `rhinomcp` or `grasshopper-mcp` tools.
7. Verify the output GCode or PolyLines are mathematically correct according to the operation (e.g., checking if the offset toolpath is exactly Tool_Diameter/2 away from the boundary).
