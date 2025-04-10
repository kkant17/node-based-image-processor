import unittest
import weakref
from typing import Any
# Adjust import path if your project structure is different
from node_graph import Port, PortType, Node, Graph

# A minimal concrete Node for testing Port's node reference
class MockNodeForPort(Node):
    def __init__(self, graph, name="MockNode"):
        # Temporarily bypass the graph requirement for isolated node instance
        self._graph = graph # Store graph reference manually if needed
        self._name = name
        self._id = "mock_node_for_port_test"
        self.input_ports = {}
        self.output_ports = {}
        self.parameters = {}
        # Don't call super().__init__ as it requires a graph in the simplified version
        # No need to call _setup_ports/_setup_parameters for this mock

    def _setup_ports(self): pass # Override abstract method
    # def process(self): pass # No process in simplified Node base

# Need a graph instance for nodes, even if simple
class MockGraphForPort:
    def notify_connection_removed(self, conn): pass # Dummy method

class TestPort(unittest.TestCase):

    def setUp(self):
        """Set up test fixtures, if any."""
        self.mock_graph = MockGraphForPort()
        self.node1 = MockNodeForPort(self.mock_graph, "Node1")
        self.node2 = MockNodeForPort(self.mock_graph, "Node2")
        # Create ports directly for testing, bypassing Node.add_port for isolation
        self.out_port = Port(self.node1, "out1", PortType.OUTPUT, data_type=int)
        self.in_port1 = Port(self.node2, "in1", PortType.INPUT, data_type=int)
        self.in_port2 = Port(self.node2, "in2", PortType.INPUT, data_type=str) # Different type
        self.in_port_any = Port(self.node2, "in_any", PortType.INPUT, data_type=Any)
        self.out_port_any = Port(self.node1, "out_any", PortType.OUTPUT, data_type=Any)

    def test_port_creation(self):
        """Test basic port attributes after creation."""
        self.assertEqual(self.out_port.name, "out1")
        self.assertIs(self.out_port.node, self.node1)
        self.assertEqual(self.out_port.port_type, PortType.OUTPUT)
        self.assertEqual(self.out_port.data_type, int)
        self.assertFalse(self.out_port.is_connected())
        self.assertEqual(len(self.out_port.connections), 0)

    def test_can_connect_valid(self):
        """Test valid connection scenarios."""
        self.assertTrue(self.out_port.can_connect(self.in_port1))
        self.assertTrue(self.in_port1.can_connect(self.out_port)) # Order shouldn't matter
        self.assertTrue(self.out_port.can_connect(self.in_port_any)) # Output int -> Input Any
        self.assertTrue(self.out_port_any.can_connect(self.in_port1)) # Output Any -> Input int

    def test_can_connect_invalid_direction(self):
        """Test connection attempt between ports of the same direction."""
        another_out = Port(self.node1, "out2", PortType.OUTPUT)
        self.assertFalse(self.out_port.can_connect(another_out))
        self.assertFalse(self.in_port1.can_connect(self.in_port_any))

    def test_can_connect_invalid_same_node(self):
        """Test connection attempt within the same node."""
        in_on_node1 = Port(self.node1, "in_local", PortType.INPUT)
        self.assertFalse(self.out_port.can_connect(in_on_node1))

    def test_can_connect_invalid_data_type(self):
        """Test connection attempt with incompatible data types."""
        self.assertFalse(self.out_port.can_connect(self.in_port2)) # int -> str

    def test_can_connect_invalid_input_already_connected(self):
        """Test connection attempt to an already connected input port."""
        # Mock a connection
        mock_connection = object() # Just need a placeholder object
        self.in_port1._connections.append(mock_connection) # Directly modify for test
        self.assertTrue(self.in_port1.is_connected())
        self.assertFalse(self.out_port.can_connect(self.in_port1))
        self.in_port1._connections.remove(mock_connection) # Clean up

    def test_add_remove_connection(self):
        """Test adding and removing a connection object to the port's list."""
        mock_connection = object() # Placeholder
        self.assertEqual(len(self.out_port.connections), 0)
        self.out_port.add_connection(mock_connection)
        self.assertEqual(len(self.out_port.connections), 1)
        self.assertIn(mock_connection, self.out_port.connections)
        self.assertTrue(self.out_port.is_connected())

        self.out_port.remove_connection(mock_connection)
        self.assertEqual(len(self.out_port.connections), 0)
        self.assertFalse(self.out_port.is_connected())

    def test_remove_nonexistent_connection(self):
        """Test removing a connection that isn't there doesn't raise error."""
        mock_connection = object()
        try:
            self.out_port.remove_connection(mock_connection)
        except ValueError:
            self.fail("Port.remove_connection() raised ValueError unexpectedly.")

    def test_port_repr(self):
        """Test the string representation of the port."""
        self.assertEqual(repr(self.out_port), "<Port Node1.out1 (OUTPUT, int)>")
        self.assertEqual(repr(self.in_port_any), "<Port Node2.in_any (INPUT, Any)>")

if __name__ == '__main__':
    unittest.main()