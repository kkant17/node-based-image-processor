# Node-Based Image Processor

This project is an implementation of a node-based image manipulation application in Python, inspired by tools like Substance Designer or Blender's node editors.

## Overview

Users can visually create image processing pipelines by connecting different nodes. Each node performs a specific operation (loading, filtering, blending, saving, etc.). The graph automatically determines the execution order and updates previews in real-time (planned).

## Current Status (Step 1)

-   **Core Framework:** Implemented the fundamental classes:
    -   `Graph`: Manages nodes and connections.
    -   `Node`: Abstract base class for processing units.
    -   `Port`: Input/Output points on nodes.
    -   `Connection`: Links between ports.
-   **Basic Features:**
    -   Node/Connection addition and removal.
    -   Port compatibility checking (type, data type, input connections).
    -   Dirtiness tracking (`mark_dirty`, `is_dirty`) to manage re-computation.
    -   Basic output caching on nodes.
    -   Topological sorting (Kahn's algorithm) for execution order.
    -   Cycle detection (during connection and via topological sort).
    -   Graph evaluation logic (`evaluate_graph`, `node.evaluate`).
    -   Abstract `Node.process()` method for custom logic.

## Getting Started

1.  Clone the repository.
2.  Create a virtual environment: `python -m venv venv`
3.  Activate the environment:
    -   Windows: `.\venv\Scripts\activate`
    -   macOS/Linux: `source venv/bin/activate`
4.  Install dependencies: `pip install -r requirements.txt`
5.  (Currently no runnable application - framework only. See tests or example scripts when added).

## Next Steps

-   Implement basic concrete Node types (e.g., `NumberInput`, `Add`, `ImageInput`, `Output`).
-   Add unit tests for the framework.
-   Start implementing image processing nodes using OpenCV/Pillow.
-   Develop the Graphical User Interface (GUI).

## Project Structure