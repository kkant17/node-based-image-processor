from PySide6.QtWidgets import QGraphicsScene, QGraphicsSceneMouseEvent, QGraphicsView, QMenu, QGraphicsLineItem, QGraphicsItem
from PySide6.QtGui import QPen, QColor, QTransform, QAction
from PySide6.QtCore import Qt, QPointF
from typing import Optional, Any
from node_graph import Graph, Node # Backend graph and node base class
from .node_item import UINode
from .port_item import UIPort, PortType
from .connection_item import UIConnection

# --- Concrete Node Types (Examples - replace with actual node classes later) ---
# These should ideally be imported from a dedicated 'nodes' package when implemented
class SimpleInputNode(Node):
    def _setup_ports(self): self.add_output_port("out", int)
    def _setup_parameters(self): self.parameters['value'] = 0
    def process(self): pass # Simplified: No process logic needed for UI structure

class SimpleProcessNode(Node):
    def _setup_ports(self):
        self.add_input_port("in1", int)
        self.add_output_port("res", int)
    def process(self): pass

class SimpleOutputNode(Node):
    def _setup_ports(self): self.add_input_port("in_val", int)
    def process(self): pass
# --- End Example Node Types ---

NODE_TYPE_MAP = {
    "Input Node": SimpleInputNode,
    "Process Node": SimpleProcessNode,
    "Output Node": SimpleOutputNode,
}

class NodeGraphScene(QGraphicsScene):
    """The scene containing nodes, connections, and handling interactions."""

    def __init__(self, backend_graph: Graph, parent=None):
        super().__init__(parent)
        self._backend_graph = backend_graph
        self.setBackgroundBrush(QColor("#404040")) # Dark background

        # Mappings to keep backend and UI in sync
        self._ui_nodes: dict[str, UINode] = {} # backend_node.id -> UINode
        self._ui_connections: list[UIConnection] = [] # Keep track of UI connections

        # For connection dragging
        self._start_port_item: Optional[UIPort] = None
        self._temp_connection_line: Optional[QGraphicsLineItem] = None

    def add_node_to_scene(self, backend_node: Node, position: QPointF):
        """Creates and adds a UINode to the scene."""
        if backend_node.id in self._ui_nodes:
            print(f"Warning: UI Node for backend node {backend_node.id} already exists.")
            return None

        ui_node = UINode(backend_node)
        self.addItem(ui_node)
        ui_node.setPos(position)
        self._ui_nodes[backend_node.id] = ui_node
        print(f"Added UINode for '{backend_node.name}' ({backend_node.id}) at {position}")
        return ui_node

    def remove_node_from_scene(self, backend_node_id: str):
        """Removes a UINode and its related UIConnections from the scene."""
        ui_node = self._ui_nodes.pop(backend_node_id, None)
        if ui_node:
            # Remove connections visually *before* removing the node
            ports = list(ui_node._ui_ports.values()) # Get ports before node is gone
            for port in ports:
                # Iterate over a copy as removing modifies the list
                for conn_item in list(port._connection_items):
                     self.remove_connection_from_scene(conn_item)

            # Now remove the node item itself
            ui_node.destroy() # Calls removeItem internally
            print(f"Removed UINode for {backend_node_id}")

    def add_connection_to_scene(self, backend_connection):
        """Creates and adds a UIConnection to the scene."""
        start_node_id = backend_connection.output_port.node.id
        end_node_id = backend_connection.input_port.node.id
        start_port_name = backend_connection.output_port.name
        end_port_name = backend_connection.input_port.name

        start_ui_node = self._ui_nodes.get(start_node_id)
        end_ui_node = self._ui_nodes.get(end_node_id)

        if not start_ui_node or not end_ui_node:
            print("Error: Could not find UI nodes for connection.")
            return None

        start_ui_port = start_ui_node.get_ui_port(start_port_name)
        end_ui_port = end_ui_node.get_ui_port(end_port_name)

        if not start_ui_port or not end_ui_port:
            print("Error: Could not find UI ports for connection.")
            return None

        # Check if visual connection already exists (shouldn't if backend added first)
        # for existing_conn in self._ui_connections:
        #     if (existing_conn.start_port_item == start_ui_port and
        #         existing_conn.end_port_item == end_ui_port):
        #         print("Warning: UI Connection already exists.")
        #         return existing_conn

        ui_conn = UIConnection(start_ui_port, end_ui_port, backend_connection)
        self.addItem(ui_conn)
        self._ui_connections.append(ui_conn)
        print(f"Added UIConnection: {ui_conn}")
        return ui_conn

    def remove_connection_from_scene(self, ui_connection_item: UIConnection):
        """Removes a UIConnection item from the scene and internal list."""
        if ui_connection_item in self._ui_connections:
            ui_connection_item.destroy() # Detaches from ports, removes from scene
            self._ui_connections.remove(ui_connection_item)
            print(f"Removed UIConnection: {ui_connection_item}")

    def get_item_at(self, position: QPointF) -> Optional[QGraphicsItem]:
        """Helper to get the topmost item at a scene position."""
        items = self.items(position)
        return items[0] if items else None

    # --- Mouse Events for Interaction ---

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent):
        """Handle starting connections."""
        item = self.get_item_at(event.scenePos())

        if isinstance(item, UIPort) and item.backend_port.port_type == PortType.OUTPUT:
            self._start_port_item = item
            # Create temporary line for visual feedback
            self._temp_connection_line = QGraphicsLineItem()
            self._temp_connection_line.setPen(QPen(QColor("yellow"), 2)) # Dashed line?
            self._temp_connection_line.setZValue(0) # Draw above connections but below nodes
            self.addItem(self._temp_connection_line)
            start_pos = self._start_port_item.get_scene_position()
            self._temp_connection_line.setLine(start_pos.x(), start_pos.y(), event.scenePos().x(), event.scenePos().y())
            print(f"Started connection drag from {self._start_port_item}")
        else:
            self._start_port_item = None
            self._temp_connection_line = None
            super().mousePressEvent(event) # Allow node moving etc.

    def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent):
        """Handle dragging connections."""
        if self._start_port_item and self._temp_connection_line:
            start_pos = self._start_port_item.get_scene_position()
            self._temp_connection_line.setLine(start_pos.x(), start_pos.y(), event.scenePos().x(), event.scenePos().y())
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QGraphicsSceneMouseEvent):
        """Handle completing connections."""
        if self._start_port_item and self._temp_connection_line:
            print("Released connection drag")
            # Remove temporary line
            self.removeItem(self._temp_connection_line)
            self._temp_connection_line = None

            item = self.get_item_at(event.scenePos())
            target_port_item: Optional[UIPort] = None
            if isinstance(item, UIPort) and item.backend_port.port_type == PortType.INPUT:
                 target_port_item = item
                 print(f"Target port found: {target_port_item}")

            if target_port_item:
                 # Attempt to add connection to backend graph
                 start_be_port = self._start_port_item.backend_port
                 target_be_port = target_port_item.backend_port
                 start_be_node = start_be_port.node
                 target_be_node = target_be_port.node

                 # Basic validation using backend (add cycle check if needed)
                 if start_be_port.can_connect(target_be_port): # and not self._backend_graph.creates_cycle(start_be_node, target_be_node):
                      print("Backend connection valid, attempting add...")
                      backend_connection = self._backend_graph.add_connection(
                          start_be_node.id, start_be_port.name,
                          target_be_node.id, target_be_port.name
                      )
                      if backend_connection:
                           # Backend added successfully, add visual connection
                           self.add_connection_to_scene(backend_connection)
                      else:
                           print("Backend refused connection.")
                 else:
                      print("Backend ports cannot connect.")
            else:
                 print("Connection released over empty space or invalid target.")

            # Reset state
            self._start_port_item = None

        else:
            super().mouseReleaseEvent(event)

    # --- Context Menu ---
    def contextMenuEvent(self, event):
        menu = QMenu()
        pos = event.scenePos()

        # Actions to add node types
        for node_name in NODE_TYPE_MAP.keys():
            action = QAction(f"Add {node_name}", menu)
            # Use lambda with default argument to capture correct node_name
            action.triggered.connect(lambda checked=False, name=node_name: self.create_node_request(name, pos))
            menu.addAction(action)

        menu.exec(event.screenPos())

    def create_node_request(self, node_type_name: str, position: QPointF):
        """Handles request to create a new node."""
        node_class = NODE_TYPE_MAP.get(node_type_name)
        if node_class:
            print(f"Requesting creation of {node_type_name} at {position}")
            # Create backend node instance FIRST
            new_backend_node = node_class(self._backend_graph, node_type_name) # Pass graph
            # Add backend node to the actual graph
            self._backend_graph.add_node(new_backend_node)
            # Add corresponding UI node to the scene
            self.add_node_to_scene(new_backend_node, position)
        else:
            print(f"Error: Unknown node type requested: {node_type_name}")