import uuid
from typing import Dict, Any, Optional, List

# We keep Port/PortType for structure
from .port import Port, PortType

# Forward reference for type hinting 
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .graph import Graph
    from .connection import Connection # Needed for disconnect_all type hints

import abc

class Node(abc.ABC):
    """
    Abstract base class for all nodes in the graph.
    *** SIMPLIFIED VERSION: Focuses on structure, removes evaluation,
        dirtiness, caching, and process execution logic. ***
    """

    def __init__(self, graph: 'Graph', name: str, node_id: Optional[str] = None):
        """
        Initializes a Node.

        Args:
            graph: The Graph this node belongs to.
            name: A descriptive name for the node (e.g., "Blur", "Image Input").
            node_id: Optional specific ID. If None, a unique ID is generated.
        """
        if graph is None:
            raise ValueError("Node must belong to a Graph.")
        self._graph = graph # Store graph reference
        self._name = name
        self._id = node_id or str(uuid.uuid4()) # Ensure unique ID

        self.input_ports: Dict[str, Port] = {}
        self.output_ports: Dict[str, Port] = {}
        self.parameters: Dict[str, Any] = {} # Node-specific settings

        self._setup_ports()
        self._setup_parameters()

    @property
    def id(self) -> str:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        self._name = value
        # Potentially notify graph/UI of name change if needed

    @property
    def graph(self) -> 'Graph':
        return self._graph

    # Subclasses still need to define their ports
    @abc.abstractmethod
    def _setup_ports(self) -> None:
        """Abstract method for subclasses to define their input/output ports."""
        pass

    def _setup_parameters(self) -> None:
        """Optional method for subclasses to define their parameters."""
        pass

    # --- Port Management (Remains the Same) ---

    def add_input_port(self, name: str, data_type: type = Any) -> Port:
        """Creates and adds an input port."""
        if name in self.input_ports:
            raise ValueError(f"Input port '{name}' already exists on node '{self.name}'.")
        port = Port(self, name, PortType.INPUT, data_type)
        self.input_ports[name] = port
        return port

    def add_output_port(self, name: str, data_type: type = Any) -> Port:
        """Creates and adds an output port."""
        if name in self.output_ports:
            raise ValueError(f"Output port '{name}' already exists on node '{self.name}'.")
        port = Port(self, name, PortType.OUTPUT, data_type)
        self.output_ports[name] = port
        return port

    def get_input_port(self, name: str) -> Optional[Port]:
        return self.input_ports.get(name)

    def get_output_port(self, name: str) -> Optional[Port]:
        return self.output_ports.get(name)

    def set_parameter(self, name: str, value: Any) -> None:
        """Sets a node parameter."""
        if name in self.parameters:
            if self.parameters[name] != value:
                self.parameters[name] = value
                # Removed self.mark_dirty()
                print(f"Parameter '{name}' set to '{value}' on node '{self.name}'.")
        else:
            print(f"Warning: Setting unknown parameter '{name}' on node '{self.name}'.")
            self.parameters[name] = value
            # Removed self.mark_dirty()

    def get_parameter(self, name: str) -> Any:
        """Gets a node parameter's value."""
        return self.parameters.get(name)

    def process(self) -> None:
        """
        Method where the node's computation logic would reside.
        *** In this simplified framework, this method is NOT automatically called. ***
        """
        pass # Subclasses will override

    # Inside node_graph/node.py

    def disconnect_all(self):
        """Removes all connections attached to this node's ports."""
        print(f"Disconnecting all ports for node {self.name} ({self.id})")
        ports_to_clear = list(self.input_ports.values()) + list(self.output_ports.values())
        for port in ports_to_clear:
            for conn in list(port.connections):
                 # Let the graph handle the full removal process
                 if self.graph:
                     self.graph.remove_connection(conn)
                 else:
                      # Fallback if no graph context? Should ideally not happen.
                      conn.remove()


    def __repr__(self) -> str:
        return f"<Node {self.name} (ID: {self.id})>"