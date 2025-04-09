from typing import Dict, List, Optional

# Need Node, Port, Connection for basic structure management
from .node import Node
from .port import Port # For type hints in add_connection
from .connection import Connection

class Graph:
    """
    Manages a collection of Nodes and Connections.
    *** SIMPLIFIED VERSION: Focuses on structure, removes evaluation,
        topological sorting, cycle detection. ***
    """

    def __init__(self):
        self._nodes: Dict[str, Node] = {}
        self._connections: List[Connection] = []

    @property
    def nodes(self) -> Dict[str, Node]:
        """Returns the dictionary of nodes in the graph."""
        return self._nodes # Or return a copy if mutation is a concern

    @property
    def connections(self) -> List[Connection]:
         """Returns the list of connections in the graph."""
         return self._connections # Or return a copy

    def add_node(self, node: Node) -> None:
        """Adds a pre-constructed Node object to the graph."""
        if not isinstance(node, Node):
             raise TypeError("Object added must be an instance of Node.")
        if node.id in self._nodes:
            raise ValueError(f"Node with ID '{node.id}' already exists in the graph.")
        # Simple check if node thinks it belongs elsewhere (basic sanity)
        if hasattr(node, '_graph') and node.graph != self:
             raise ValueError("Node reports belonging to a different graph.")

        self._nodes[node.id] = node
        print(f"Node '{node.name}' (ID: {node.id}) added to graph.")

    def remove_node(self, node_id: str) -> None:
        """Removes a node and attempts to disconnect its connections."""
        node = self._nodes.get(node_id)
        if node:
            # Disconnect all ports (Node.disconnect_all calls Connection.remove)
            # Connection.remove should detach from ports.
            # We need to clean up the graph's list via notify_connection_removed.
            node.disconnect_all()

            # Remove node from graph dictionary
            del self._nodes[node_id]
            print(f"Node '{node.name}' (ID: {node.id}) removed from graph.")
        else:
            print(f"Warning: Node with ID '{node_id}' not found for removal.")


    def get_node(self, node_id: str) -> Optional[Node]:
        """Retrieves a node by its ID."""
        return self._nodes.get(node_id)

    def add_connection(self, output_node_id: str, output_port_name: str,
                       input_node_id: str, input_port_name: str) -> Optional[Connection]:
        """
        Creates and adds a connection between two ports if valid (basic checks only).
        *** SIMPLIFIED: No cycle detection. ***

        Returns:
            The created Connection object, or None if connection failed basic checks.
        """
        output_node = self.get_node(output_node_id)
        input_node = self.get_node(input_node_id)

        if not output_node:
            print(f"Connection Error: Output node '{output_node_id}' not found.")
            return None
        if not input_node:
            print(f"Connection Error: Input node '{input_node_id}' not found.")
            return None

        output_port = output_node.get_output_port(output_port_name)
        input_port = input_node.get_input_port(input_port_name)

        if not output_port:
            print(f"Connection Error: Output port '{output_port_name}' not found on node '{output_node.name}'.")
            return None
        if not input_port:
            print(f"Connection Error: Input port '{input_port_name}' not found on node '{input_node.name}'.")
            return None
        # Use Port.can_connect for basic compatibility (types, direction, input slot)
        if not output_port.can_connect(input_port):
             # can_connect prints specific error messages
             return None
        
        # --- Create Connection ---
        try:
            # Assumes Connection constructor just stores ports and calls port.add_connection
            connection = Connection(output_port, input_port)
            self._connections.append(connection)
            print(f"Connection added: {connection}")
            return connection
        except ValueError as e: # Catch potential errors during Connection init
            print(f"Connection Error during creation: {e}")
            return None

    def remove_connection(self, connection_to_remove: Connection) -> None:
        """
        Removes a specific connection object from the graph's list.
        Assumes the connection has already been told to detach from ports.
        """
        try:
            self._connections.remove(connection_to_remove)
            print(f"Connection removed from graph list: {connection_to_remove}")
        except ValueError:
            pass

    def notify_connection_removed(self, connection: Connection) -> None:
        """Callback for Node/Connection to inform Graph the connection is gone."""
        self.remove_connection(connection)
