import unittest
import numpy as np # Example data type
from node_graph import Node, Graph, PortType, Port
from typing import Any # For Any type hint

# A concrete node implementation for testing
class AdderNode(Node):
    """A simple node that adds two numbers."""
    def _setup_ports(self):
        self.add_input_port("in_a", data_type=float)
        self.add_input_port("in_b", data_type=float)
        self.add_output_port("result", data_type=float)

    def _setup_parameters(self):
        self.parameters["bias"] = 0.0

    # Process method exists but is not called by the simplified framework tests
    def process(self):
        # a = self.get_input_data("in_a") or 0.0 # Would need get_input_data
        # b = self.get_input_data("in_b") or 0.0 # Would need get_input_data
        # result = a + b + self.get_parameter("bias")
        # self.set_output_data("result", result) # Would need set_output_data
        pass

class TestNode(unittest.TestCase):

    def setUp(self):
        # Use the actual Graph class now as Node depends on it
        self.graph = Graph()
        self.node = AdderNode(self.graph, "MyAdder")
        # Add node to graph for context, although not strictly needed for all tests here
        self.graph.add_node(self.node)

    def test_node_creation(self):
        """Test node attributes after creation."""
        self.assertEqual(self.node.name, "MyAdder")
        self.assertIsNotNone(self.node.id)
        self.assertIs(self.node.graph, self.graph)
        self.assertIn("in_a", self.node.input_ports)
        self.assertIn("in_b", self.node.input_ports)
        self.assertIn("result", self.node.output_ports)
        self.assertIn("bias", self.node.parameters)
        self.assertEqual(self.node.get_parameter("bias"), 0.0)

    def test_add_ports(self):
        """Test adding ports via helper methods."""
        in_port = self.node.get_input_port("in_a")
        out_port = self.node.get_output_port("result")
        self.assertIsInstance(in_port, Port)
        self.assertIsInstance(out_port, Port)
        self.assertEqual(in_port.name, "in_a")
        self.assertEqual(in_port.port_type, PortType.INPUT)
        self.assertEqual(in_port.data_type, float)
        self.assertIs(in_port.node, self.node) # Check weakref resolves correctly
        self.assertEqual(out_port.name, "result")
        self.assertEqual(out_port.port_type, PortType.OUTPUT)
        self.assertEqual(out_port.data_type, float)

    def test_add_duplicate_port_raises_error(self):
        """Test that adding a port with an existing name fails."""
        with self.assertRaisesRegex(ValueError, "Input port 'in_a' already exists"):
            self.node.add_input_port("in_a")
        with self.assertRaisesRegex(ValueError, "Output port 'result' already exists"):
            self.node.add_output_port("result")

    def test_get_nonexistent_port(self):
        """Test getting ports that don't exist returns None."""
        self.assertIsNone(self.node.get_input_port("nonexistent"))
        self.assertIsNone(self.node.get_output_port("nonexistent"))

    def test_set_get_parameter(self):
        """Test setting and getting node parameters."""
        self.node.set_parameter("bias", 5.5)
        self.assertEqual(self.node.get_parameter("bias"), 5.5)

        # Test setting a new parameter (allowed in simplified version)
        self.node.set_parameter("new_param", "hello")
        self.assertEqual(self.node.get_parameter("new_param"), "hello")

    def test_get_nonexistent_parameter(self):
        """Test getting a parameter that doesn't exist returns None."""
        self.assertIsNone(self.node.get_parameter("nonexistent"))

    def test_node_repr(self):
        """Test the string representation of the node."""
        self.assertTrue(repr(self.node).startswith("<Node MyAdder (ID:"))

    # disconnect_all testing is better done in test_graph.py where
    # connections are managed and verified within the graph context.

if __name__ == '__main__':
    unittest.main()