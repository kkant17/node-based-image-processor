from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .port import Port

class Connection:
    """Represents a connection between an output port and an input port."""

    def __init__(self, output_port: 'Port', input_port: 'Port'):
        """
        Initializes a Connection. Assumes validation has already occurred.

        Args:
            output_port: The source Port (must be PortType.OUTPUT).
            input_port: The destination Port (must be PortType.INPUT).
        """
        if not output_port or not input_port:
             raise ValueError("Output and input ports cannot be None")
        if output_port.port_type != output_port.port_type.OUTPUT:
            raise ValueError("Connection source must be an OUTPUT port.")
        if input_port.port_type != input_port.port_type.INPUT:
            raise ValueError("Connection destination must be an INPUT port.")

        self._output_port = output_port
        self._input_port = input_port

        # Add this connection to the respective ports
        self._output_port.add_connection(self)
        self._input_port.add_connection(self)

        # Mark downstream node as dirty
        if self._input_port.node:
             self._input_port.node.mark_dirty()


    @property
    def output_port(self) -> 'Port':
        """Returns the output (source) port."""
        return self._output_port

    @property
    def input_port(self) -> 'Port':
        """Returns the input (destination) port."""
        return self._input_port

    def remove(self) -> None:
        """Removes the connection from both connected ports."""
        if self._output_port:
            self._output_port.remove_connection(self)
        if self._input_port:
            input_node = self._input_port.node # Get node before removing connection
            self._input_port.remove_connection(self)
            # Mark the node that lost input as dirty
            if input_node:
                input_node.mark_dirty()

        # Clear references
        self._output_port = None
        self._input_port = None
        print(f"Removed connection: {self}") # For debugging

    def __repr__(self) -> str:
        out_node_name = self.output_port.node.name if self.output_port and self.output_port.node else "<?>"
        in_node_name = self.input_port.node.name if self.input_port and self.input_port.node else "<?>"
        return (f"<Connection {out_node_name}.{self.output_port.name} -> "
                f"{in_node_name}.{self.input_port.name}>")