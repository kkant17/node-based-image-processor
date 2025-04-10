# Node-Based Image Processor

This project is an implementation of a node-based image manipulation application in Python, inspired by tools like Substance Designer or Blender's node editors, and provides a basic graphical interface for interaction.

## Overview

Users can visually create image processing pipelines by connecting different nodes. Each node performs a specific operation (loading, filtering, blending, saving, etc.). The graph automatically determines the execution order and updates previews in real-time (planned). The GUI allows users to interact with the node graph visually.

## Current Status (Step 2: Basic GUI)

-   **Core Framework:** Implemented the fundamental backend classes (`Graph`, `Node`, `Port`, `Connection`) focusing on structural representation (evaluation logic removed for now). Includes basic validation, addition/removal of elements. Unit tests cover this core structure.
-   **Basic GUI (PySide6):** Implemented the initial visual framework:
    -   Displays nodes (`UINode`), ports (`UIPort`), and connections (`UIConnection`) on a canvas (`NodeGraphScene`).
    -   Allows moving nodes via drag-and-drop.
    -   Context menu (right-click) to add simple placeholder nodes (Input, Process, Output).
    -   Basic connection drawing by dragging between compatible output/input ports.
    -   **Limitations:** Uses temporary placeholder backend nodes defined in the UI code, no properties panel for editing, basic styling, connection visual feedback only on completion, no save/load functionality.

## Getting Started

1.  Clone the repository.
2.  Create a virtual environment: `python -m venv venv`
3.  Activate the environment:
    -   Windows: `.\venv\Scripts\activate`
    -   macOS/Linux: `source venv/bin/activate`
4.  Install dependencies: `pip install -r requirements.txt` (includes `numpy` and `PySide6`).
5.  Run the application: `python main.py`

## Next Steps

-   Implement *real* image processing backend Node types (e.g., `ImageInput`, `Blur`, `BrightnessContrast`, `Output`) using OpenCV/Pillow, likely in a separate `nodes/` directory.
-   Integrate these real nodes into the GUI's `NODE_TYPE_MAP` in `node_graph_scene.py`.
-   Develop the GUI properties panel to display and edit parameters of the selected node.
-   Implement the evaluation engine (topological sort, cycle detection, caching, `node.process()` execution) in the backend `node_graph` package.
-   Connect GUI actions (e.g., parameter changes) to trigger backend graph re-evaluation.
-   Add visual feedback during connection dragging.
-   Implement saving and loading of the graph structure (node positions, connections, parameters).
-   Refine UI styling and overall user experience.
-   Add proper error handling and display.

## Project Structure