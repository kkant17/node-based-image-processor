# Design Document - Node-Based Image Processor

## 1. Architecture Overview

The application follows a node-graph architecture, separating backend logic from the user interface. The core components are:

-   **Node Graph Backend (`node_graph/`):**
    -   **Node:** Represents an operation (e.g., load image, apply blur, save image). Each node has input and output ports and parameters. Currently implemented as an abstract base class with structural focus.
    -   **Port:** An endpoint on a node for connections. Ports have types (input/output) and data types.
    -   **Connection:** Represents a link between an output port and an input port.
    -   **Graph:** Manages the collection of nodes and connections. Responsible for storing the graph structure. (Evaluation logic currently omitted but planned).
-   **User Interface (UI) (`ui/`):**
    -   Built using **PySide6** (Qt for Python).
    -   Provides the visual representation of the node graph.
    -   Handles user interactions (node creation, movement, connections).
    -   Communicates with the `node_graph` backend to reflect and modify the graph state.

## 2. Core Backend Classes (`node_graph`)

*(Keep sections 2.1 PortType, 2.2 Port, 2.3 Node (simplified), 2.4 Connection, 2.5 Graph (simplified) as they describe the current simplified backend structure. Remove mentions of evaluation, dirtiness, caching, sorting from their descriptions if you committed the simplified versions).*

*Example adjustment for 2.5 Graph:*
### 2.5. `Graph`
- **Attributes:**
    - `nodes`: Dictionary `{node_id: Node}`.
    - `connections`: List of `Connection` objects.
- **Methods:**
    - `add_node(node_instance)`
    - `remove_node(node_id)`
    - `add_connection(output_node_id, output_port_name, input_node_id, input_port_name)`: Creates and validates a connection based on port compatibility. (No cycle detection in simplified version).
    - `remove_connection(connection)`
    - `get_node(node_id)`
    - *(Removed methods related to evaluation, sorting, etc.)*

## 3. Execution Flow (Planned)

*(Keep this section, but maybe add a note that it describes the *intended* flow once the evaluation engine is re-integrated)*

**Note:** The following describes the planned execution flow once the evaluation engine is added back to the backend. The current implementation only manages the graph structure.

1.  User modifies a parameter (via Properties Panel - TBD) or connection (via GUI).
2.  The affected backend node and all downstream nodes are marked `dirty`.
3.  User requests evaluation (e.g., by viewing an Output Node or an explicit trigger).
4.  The backend `Graph` performs a topological sort. Cycle detection occurs here.
5.  The `Graph` iterates through the sorted nodes.
6.  For each node, `evaluate()` is called (handling dirtiness, caching, calling `process()`).
7.  UI elements (like previews) are updated based on the results.

## 4. Data Types

*(Keep this section as is - primarily numpy arrays)*

## 5. Third-Party Libraries

-   **NumPy:** Essential for numerical operations and image data representation (arrays). Chosen for performance and widespread use in scientific Python.
-   **PySide6:** Official Qt for Python bindings. Used for building the entire graphical user interface (windows, widgets, graphics scene). Chosen for its comprehensive features, maturity, and cross-platform compatibility.
-   **(Potential)** OpenCV-Python (`opencv-python`): Will be used for image loading, saving, and processing operations within concrete Node implementations.
-   **(Potential)** Pillow: Alternative or supplement to OpenCV for image I/O.

## 6. UI Components (`ui/`)

This section describes the main classes responsible for the graphical user interface.

### 6.1. `MainWindow` (`QMainWindow`)

-   Top-level application window.
-   Contains the main `QGraphicsView` which displays the scene.
-   Will eventually host menus, toolbars, status bars, and potentially dockable widgets like a properties panel.

### 6.2. `NodeGraphScene` (`QGraphicsScene`)

-   The interactive canvas where UI items (`UINode`, `UIConnection`) are placed and managed.
-   Subclasses `QGraphicsScene` to handle custom interactions.
-   Manages collections/mappings of UI items corresponding to backend objects.
-   Handles mouse events for:
    -   Node selection and movement.
    -   Starting, dragging, and completing connections between ports.
    -   Displaying context menus (e.g., for adding nodes).
-   Coordinates with the backend `Graph`:
    -   Requests backend to add/remove nodes/connections based on user actions.
    -   Instantiates corresponding UI items (`UINode`, `UIConnection`) when the backend confirms an addition.
    -   Removes UI items when corresponding backend objects are removed.

### 6.3. `UINode` (`QGraphicsRectItem`)

-   Visual representation of a backend `Node`.
-   Drawn as a rectangle with a distinct header containing the node's title.
-   Owns and positions child `UIPort` items along its edges.
-   Implements basic styling (colors, fonts).
-   Handles user interaction for movement (`ItemIsMovable`) and selection (`ItemIsSelectable`).
-   Overrides `itemChange` to detect position changes and notify attached `UIConnection` items to update their paths.

### 6.4. `UIPort` (`QGraphicsEllipseItem`)

-   Visual representation of a backend `Port`.
-   Displayed as a small circle on the `UINode`.
-   Color-coded (tentatively) to distinguish input vs. output.
-   Provides tooltips showing port information (name, data type).
-   Acts as the visual anchor point for `UIConnection` start/end points.
-   Stores references to `UIConnection` items connected to it.

### 6.5. `UIConnection` (`QGraphicsPathItem`)

-   Visual representation of a backend `Connection`.
-   Drawn as a path (currently a Bezier curve) between two `UIPort` items.
-   Updates its path dynamically when connected `UINode` items are moved (triggered by `UINode.itemChange`).
-   Styled with a specific pen (color, thickness).
-   Drawn with a lower Z-value to appear underneath nodes and ports.

## 7. UI Interaction Flow Example (Adding Connection)

1.  User clicks and holds the mouse button over an output `UIPort`.
2.  `NodeGraphScene.mousePressEvent` detects the press on the `UIPort`, stores it as the potential starting port, and creates a temporary visual line originating from the port.
3.  User drags the mouse (`NodeGraphScene.mouseMoveEvent` updates the temporary line endpoint).
4.  User releases the mouse button over a compatible input `UIPort`.
5.  `NodeGraphScene.mouseReleaseEvent` identifies the target `UIPort`.
6.  The scene retrieves the corresponding backend `Port` objects for both the start and target `UIPort`.
7.  The scene calls `backend_graph.add_connection(...)`, passing the backend node IDs and port names.
8.  The backend `Graph` performs validation (port type compatibility, input port availability, potentially cycle detection later).
9.  If the backend validation passes, the `Graph` creates a backend `Connection` object and potentially adds it to its internal list, returning the new connection object (or True).
10. If the backend call was successful, the `NodeGraphScene` creates a `UIConnection` instance linking the start and target `UIPort` items and adds this `UIConnection` to the scene.
11. The temporary visual line is removed from the scene.