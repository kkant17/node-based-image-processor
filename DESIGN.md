# Design Document - Node-Based Image Processor

## 1. Architecture Overview

The application follows a node-graph architecture. The core components are:
- **Node:** Represents an operation (e.g., load image, apply blur, save image). Each node has input and output ports.
- **Port:** An endpoint on a node for connections. Ports have types (input/output) and data types (e.g., image, number, string).
- **Connection:** Represents a link between an output port of one node and an input port of another, enabling data flow.
- **Graph:** Manages the collection of nodes and connections. Responsible for orchestrating the execution pipeline, detecting dependencies, and ensuring correct processing order.

## 2. Core Classes

### 2.1. `PortType` (Enum)
- Defines whether a port is for input (`INPUT`) or output (`OUTPUT`).

### 2.2. `Port`
- **Attributes:**
    - `node`: Reference to the parent `Node`.
    - `name`: Unique identifier within the node (e.g., "image_in", "value").
    - `port_type`: `PortType.INPUT` or `PortType.OUTPUT`.
    - `data_type`: Expected type of data (e.g., `np.ndarray`, `int`, `float`, `str`). Used for connection validation.
    - `data`: Holds the actual data value (cached for outputs, received for inputs).
    - `connections`: List of `Connection` objects attached to this port.
- **Methods:**
    - `can_connect(other_port)`: Checks if a connection is valid (type mismatch, data type mismatch, etc.).
    - `add_connection(connection)`
    - `remove_connection(connection)`
    - `get_data()`: Retrieves data (crucial for input ports pulling data).
    - `set_data(value)`: Sets data (crucial for output ports after processing).
    - `is_connected()`: Checks if the port has any connections.

### 2.3. `Node` (Abstract Base Class)
- **Attributes:**
    - `id`: Unique identifier within the graph.
    - `name`: Display name or type name (e.g., "Blur", "Image Input").
    - `input_ports`: Dictionary `{port_name: Port}`.
    - `output_ports`: Dictionary `{port_name: Port}`.
    - `parameters`: Dictionary for node-specific settings (e.g., {'radius': 5}).
    - `graph`: Reference to the parent `Graph`.
    - `_dirty`: Flag indicating if the node needs recomputation.
    - `_cached_output_data`: Dictionary `{port_name: data}` for caching.
- **Methods:**
    - `__init__(...)`: Initializes ports and parameters.
    - `add_input_port(...)`
    - `add_output_port(...)`
    - `get_input_port(name)`
    - `get_output_port(name)`
    - `get_input_data(port_name)`: Helper to get data from a specific input port (handles connection logic).
    - `set_output_data(port_name, data)`: Helper to set data on an output port and update cache.
    - `process()`: Abstract method to be implemented by subclasses. Performs the node's operation using input data and parameters, then sets output data.
    - `mark_dirty()`: Sets the dirty flag and propagates dirtiness downstream.
    - `mark_clean()`: Clears the dirty flag.
    - `is_dirty()`: Returns the dirty status.
    - `evaluate()`: Manages the computation logic (check cache, check dirty, call process).

### 2.4. `Connection`
- **Attributes:**
    - `output_port`: The source `Port`.
    - `input_port`: The destination `Port`.
- **Methods:**
    - `remove()`: Disconnects the connection from both ports.

### 2.5. `Graph`
- **Attributes:**
    - `nodes`: Dictionary `{node_id: Node}`.
    - `connections`: List of `Connection` objects.
    - `_next_node_id`: Counter for generating unique node IDs.
- **Methods:**
    - `add_node(node_instance)`
    - `remove_node(node_id)`
    - `add_connection(output_node_id, output_port_name, input_node_id, input_port_name)`: Creates and validates a connection.
    - `remove_connection(connection)`
    - `get_node(node_id)`
    - `build_dependency_graph()`: Creates an internal representation of node dependencies.
    - `topological_sort()`: Orders nodes for execution based on dependencies. Detects cycles.
    - `evaluate_graph(target_node_id=None)`: Executes the graph (or up to a specific node) in the correct order, handling caching and dirtiness.
    - `clear_cache()`: Marks all nodes as dirty.

## 3. Execution Flow

1.  User modifies a parameter or connection.
2.  The affected node and all downstream nodes are marked `dirty`.
3.  User requests evaluation (e.g., by viewing an Output Node).
4.  The `Graph` performs a topological sort starting from the necessary input nodes up to the target node(s). Cycle detection occurs here.
5.  The `Graph` iterates through the sorted nodes.
6.  For each node:
    a. If the node is `dirty` or its cache is invalid:
        i. Call the node's `evaluate()` method.
        ii. `evaluate()` calls `get_input_data()` for each required input port.
        iii. `get_input_data()` recursively triggers evaluation of upstream connected nodes if necessary.
        iv. `evaluate()` calls the node's `process()` method.
        v. `process()` computes results and calls `set_output_data()`.
        vi. `set_output_data()` caches the result and marks the node `clean`.
    b. If the node is not `dirty`, its cached output data is used directly.

## 4. Data Types

- Primarily `numpy.ndarray` for image data.
- Standard Python types (`int`, `float`, `str`, `bool`) for parameters and potentially simple data flow.
- Ports will have explicit `data_type` attributes for validation.

## 5. Third-Party Libraries

- **NumPy:** Essential for numerical operations and image data representation (arrays). Chosen for performance and widespread use in scientific Python.
- **(Potential)** NetworkX: Could be used for graph algorithms (topological sort, cycle detection), but implementing these directly might offer more control specific to the node graph needs. *Decision: Implement sorting/cycle detection manually first.*
- **(Later)** OpenCV-Python (`opencv-python-headless` or `opencv-python`): For image loading, saving, and processing operations. Chosen for its comprehensive set of image algorithms.
- **(Later)** PyQt6 / PySide6: For the Graphical User Interface. Chosen for their maturity, features, and C++ Qt backend familiarity.