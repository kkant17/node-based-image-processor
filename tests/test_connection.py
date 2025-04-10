import unittest
from node_graph import Port, PortType, Node, Graph, Connection

# Minimal Node and Graph for context
class MockNodeForConn(Node):
    def __init__(self, graph, name):
        self._graph = graph
        self._name = name
        self._id = f"mock_{name}"
        self.input_ports = {}
        self.output_ports = {}
        self.parameters = {}

    def _setup_ports(self): pass
    # def process(self): pass

class MockGraphForConn:
     def notify_connection_removed(self, conn): pass # Dummy method

class TestConnection(unittest.TestCase):

    def setUp(self):
        self.mock_graph = MockGraphForConn()
        self.node1 = MockNodeForConn(self.mock_graph, "NodeA")
        self.node2 = MockNodeForConn(self.mock_graph, "NodeB")
        self.out_port = Port(self.node1, "out", PortType.OUTPUT)
        self.in_port = Port(self.node2, "in", PortType.INPUT)

    def test_connection_creation(self):
        """Test successful connection creation and linking to ports."""
        self.assertFalse(self.out_port.is_connected())
        self.assertFalse(self.in_port.is_connected())

        connection = Connection(self.out_port, self.in_port)

        self.assertIs(connection.output_port, self.out_port)
        self.assertIs(connection.input_port, self.in_port)
        self.assertTrue(self.out_port.is_connected())
        self.assertTrue(self.in_port.is_connected())
        self.assertIn(connection, self.out_port.connections)
        self.assertIn(connection, self.in_port.connections)

    def test_connection_creation_invalid_ports(self):
        """Test Connection init raises error for invalid port types."""
        in_port2 = Port(self.node2, "in2", PortType.INPUT)
        with self.assertRaisesRegex(ValueError, "Connection source must be an OUTPUT port"):
            Connection(self.in_port, self.out_port) # Input -> Output
        with self.assertRaisesRegex(ValueError, "Connection source must be an OUTPUT port"):
            Connection(self.in_port, in_port2) # Input -> Input
        with self.assertRaisesRegex(ValueError, "Connection destination must be an INPUT port"):
            Connection(self.out_port, self.out_port) # Output -> Output (also same port)

    def test_connection_remove(self):
        """Test removing a connection disconnects it from both ports."""
        connection = Connection(self.out_port, self.in_port)
        self.assertTrue(self.out_port.is_connected())
        self.assertTrue(self.in_port.is_connected())

        connection.remove()

        self.assertFalse(self.out_port.is_connected())
        self.assertFalse(self.in_port.is_connected())
        self.assertEqual(len(self.out_port.connections), 0)
        self.assertEqual(len(self.in_port.connections), 0)
        # Check internal references are cleared (optional, depends on impl)
        self.assertIsNone(connection._output_port)
        self.assertIsNone(connection._input_port)

    def test_connection_repr(self):
        """Test the string representation of the connection."""
        connection = Connection(self.out_port, self.in_port)
        self.assertEqual(repr(connection), "<Connection NodeA.out -> NodeB.in>")


if __name__ == '__main__':
    unittest.main()