import enum
import weakref # Use weakref to avoid circular references Node <-> Port
from typing import TYPE_CHECKING, Any, Type, List, Optional

# Forward reference for type hinting
if TYPE_CHECKING:
    from .node import Node
    from .connection import Connection

class PortType(enum.Enum):
    """Enum defining whether a port is for input or output."""
    INPUT = 1
    OUTPUT = 2

class Port:
    """Represents an input or output connection point on a Node."""

    def __init__(self, node: 'Node', name: str, port_type: PortType, data_type: Type = Any):
        """
        Initializes a Port.

        Args:
            node: The Node this port belongs to (using weakref).
            name: The unique name of the port within the node.
            port_type: PortType.INPUT or PortType.OUTPUT.
            data_type: The expected Python type of data for this port (e.g., int, float, np.ndarray).
                       Used for connection validation. Defaults to Any.
        """
        self._node_ref = weakref.ref(node) # Avoid circular reference
        self._name = name
        self._port_type = port_type
        self._data_type = data_type
        self._connections: List['Connection'] = []
        self._data: Any = None # Cached data for outputs or received data for inputs

    @property
    def node(self) -> Optional['Node']:
        """Returns the node this port belongs to, or None if the node has been deleted."""
        return self._node_ref()

    @property
    def name(self) -> str:
        """Returns the name of the port."""
        return self._name

    @property
    def port_type(self) -> PortType:
        """Returns the type of the port (INPUT or OUTPUT)."""
        return self._port_type

    @property
    def data_type(self) -> Type:
        """Returns the expected data type for this port."""
        return self._data_type

    @property
    def connections(self) -> List['Connection']:
        """Returns a list of connections attached to this port."""
        # Return a copy to prevent external modification
        return list(self._connections)

    def get_data(self) -> Any:
        """
        Retrieves the data associated with this port.
        For INPUT ports, this triggers upstream evaluation if necessary.
        For OUTPUT ports, it returns the cached data.
        """
        node = self.node
        if not node:
            # Should ideally not happen if graph management is correct
            print(f"Warning: Accessing port '{self.name}' on a deleted node.")
            return None

        if self.port_type == PortType.INPUT:
            # Input port: get data from the connected output port (if any)
            if not self.is_connected():
                # Return default value or raise error? For now, None.
                # Specific nodes might handle unconnected inputs differently.
                # print(f"Warning: Input port '{self.node.name}.{self.name}' is not connected.")
                return None
            else:
                # Assumes only one connection per input port (common practice)
                connection = self._connections[0]
                output_port = connection.output_port
                # Trigger evaluation of the upstream node if needed
                output_node = output_port.node
                if output_node:
                   return output_node.evaluate() # Get data from the specific port later if needed
                   # More refined: evaluate should return all output port data
                   # return output_node.evaluate().get(output_port.name) # Ideal, needs evaluate() update
                else:
                     print(f"Warning: Upstream node for port '{self.node.name}.{self.name}' not found.")
                     return None


        elif self.port_type == PortType.OUTPUT:
            # Output port: return the cached data set by the node's process method
            # The evaluation logic is handled by the Node.evaluate() method
             if node.is_dirty():
                # This should ideally be caught by Node.evaluate calling this
                print(f"Warning: Accessing data from dirty output port '{node.name}.{self.name}' without evaluation.")
                # Trigger evaluation just in case, though Node.evaluate should be the entry point
                node.evaluate()
             return node.get_cached_output(self.name) # Get specific port data

        return None # Should not be reached


    def set_data(self, value: Any) -> None:
        """
        Sets the data for this port. Primarily used by Nodes internally
        for OUTPUT ports after processing. Input ports generally receive
        data via connections.
        """
        # Optional: Add type checking here based on self._data_type
        # if self._data_type != Any and not isinstance(value, self._data_type):
        #     raise TypeError(f"Invalid data type for port {self.node.name}.{self.name}. Expected {self._data_type}, got {type(value)}")
        self._data = value
        # If this is an output port, setting data might trigger downstream updates
        # This logic is better handled by the Node/Graph marking things dirty


    def can_connect(self, other_port: 'Port') -> bool:
        """
        Checks if this port can connect to another port.

        Args:
            other_port: The other Port object to check connection compatibility with.

        Returns:
            True if connection is valid, False otherwise.
        """
        if not other_port:
            return False
        # Cannot connect to self
        if self == other_port:
            return False
        # Cannot connect to a port on the same node
        if self.node == other_port.node:
            return False
        # Must connect Input to Output or vice-versa
        if self.port_type == other_port.port_type:
            return False

        # Ensure data types are compatible (simple check for now, Any allows anything)
        # More complex type compatibility (e.g., inheritance) could be added here.
        input_port = self if self.port_type == PortType.INPUT else other_port
        output_port = other_port if self.port_type == PortType.INPUT else self

        if input_port.data_type != Any and output_port.data_type != Any:
             # Basic check: allow connection if types match exactly or if one is Any
             # A more robust system might check for assignability/subclassing
             if input_port.data_type != output_port.data_type:
                  print(f"Connection failed: Data type mismatch between {output_port.node.name}.{output_port.name} ({output_port.data_type.__name__}) and {input_port.node.name}.{input_port.name} ({input_port.data_type.__name__})")
                  return False

        # Input ports typically only allow one connection
        if input_port.is_connected():
             print(f"Connection failed: Input port '{input_port.node.name}.{input_port.name}' is already connected.")
             return False

        return True

    def add_connection(self, connection: 'Connection') -> None:
        """Adds a connection to this port's list."""
        if connection not in self._connections:
            self._connections.append(connection)
            # When an input port gets connected, the node might need re-evaluation
            if self.port_type == PortType.INPUT and self.node:
                self.node.mark_dirty()


    def remove_connection(self, connection: 'Connection') -> None:
        """Removes a connection from this port's list."""
        try:
            self._connections.remove(connection)
             # When an input port gets disconnected, the node might need re-evaluation
            if self.port_type == PortType.INPUT and self.node:
                self.node.mark_dirty()
        except ValueError:
            # Connection not found, potentially already removed
            pass

    def is_connected(self) -> bool:
        """Checks if the port has one or more connections."""
        return len(self._connections) > 0

    def __repr__(self) -> str:
        node_name = self.node.name if self.node else "Detached"
        return f"<Port {node_name}.{self.name} ({self.port_type.name}, {self.data_type.__name__})>"