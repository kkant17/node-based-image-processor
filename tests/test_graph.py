import unittest
from node_graph import Graph, Node, PortType, Connection
from typing import Any

# Concrete node classes for graph testing
class InputNode(Node):
    def _setup_ports(self):
        self.add_output_port("out", data_type=int)
    # def process(self): pass

class ProcessNode(Node):
    def _setup_ports(self):
        self.add_input_port("in1", data_type=int)
        self.add_input_port("in2", data_type=str) # Different type
        self.add_output_port("res", data_type=int)
    # def process(self): pass

class OutputNode(Node):
     def _setup_ports(self):
        self.add_input_port("final_in", data_type=int)
     # def process(self): pass

class TestGraph(unittest.TestCase):

    def setUp(self):
        self.graph = Graph()
        self.node_in = InputNode(self.graph, "Input")
        self.node_proc = ProcessNode(self.graph, "Process")
        self.node_out = OutputNode(self.graph, "Output")

    def test_graph_creation(self):
        """Test graph is initially empty."""
        self.assertEqual(len(self.graph.nodes), 0)
        self.assertEqual(len(self.graph.connections), 0)

    def test_add_node(self):
        """Test adding nodes to the graph."""
        self.graph.add_node(self.node_in)
        self.graph.add_node(self.node_proc)
        self.assertEqual(len(self.graph.nodes), 2)
        self.assertIn(self.node_in.id, self.graph.nodes)
        self.assertIn(self.node_proc.id, self.graph.nodes)
        self.assertIs(self.graph.get_node(self.node_in.id), self.node_in)

    def test_add_duplicate_node_id_raises_error(self):
        """Test adding a node with an existing ID fails."""
        self.graph.add_node(self.node_in)
        # Create another node instance but force the same ID
        duplicate_node = InputNode(self.graph, "Duplicate Name")
        duplicate_node._id = self.node_in.id # Force collision
        with self.assertRaisesRegex(ValueError, f"Node with ID '{self.node_in.id}' already exists"):
            self.graph.add_node(duplicate_node)

    def test_get_node(self):
        """Test retrieving nodes by ID."""
        self.graph.add_node(self.node_in)
        found_node = self.graph.get_node(self.node_in.id)
        self.assertIs(found_node, self.node_in)
        self.assertIsNone(self.graph.get_node("nonexistent_id"))

    def test_add_connection_valid(self):
        """Test adding a valid connection."""
        self.graph.add_node(self.node_in)
        self.graph.add_node(self.node_proc)
        conn = self.graph.add_connection(self.node_in.id, "out", self.node_proc.id, "in1")

        self.assertIsNotNone(conn)
        self.assertIsInstance(conn, Connection)
        self.assertEqual(len(self.graph.connections), 1)
        self.assertIn(conn, self.graph.connections)
        self.assertTrue(self.node_in.get_output_port("out").is_connected())
        self.assertTrue(self.node_proc.get_input_port("in1").is_connected())
        self.assertIn(conn, self.node_in.get_output_port("out").connections)
        self.assertIn(conn, self.node_proc.get_input_port("in1").connections)

    def test_add_connection_invalid_node_or_port(self):
        """Test adding connection fails if nodes or ports don't exist."""
        self.graph.add_node(self.node_in)
        self.graph.add_node(self.node_proc)
        # Invalid source node
        conn = self.graph.add_connection("bad_id", "out", self.node_proc.id, "in1")
        self.assertIsNone(conn)
        # Invalid target node
        conn = self.graph.add_connection(self.node_in.id, "out", "bad_id", "in1")
        self.assertIsNone(conn)
        # Invalid source port
        conn = self.graph.add_connection(self.node_in.id, "bad_port", self.node_proc.id, "in1")
        self.assertIsNone(conn)
        # Invalid target port
        conn = self.graph.add_connection(self.node_in.id, "out", self.node_proc.id, "bad_port")
        self.assertIsNone(conn)
        self.assertEqual(len(self.graph.connections), 0)

    def test_add_connection_invalid_type_mismatch(self):
        """Test adding connection fails on incompatible data types."""
        self.graph.add_node(self.node_in)
        self.graph.add_node(self.node_proc)
        # Connect int output to string input
        conn = self.graph.add_connection(self.node_in.id, "out", self.node_proc.id, "in2")
        self.assertIsNone(conn)
        self.assertEqual(len(self.graph.connections), 0)

    def test_add_connection_invalid_input_connected(self):
        """Test adding connection fails if input port already has a connection."""
        self.graph.add_node(self.node_in)
        self.graph.add_node(self.node_proc)
        # First connection is okay
        conn1 = self.graph.add_connection(self.node_in.id, "out", self.node_proc.id, "in1")
        self.assertIsNotNone(conn1)
        # Second connection to the same input port fails
        node_in2 = InputNode(self.graph, "Input2") # Need another source
        self.graph.add_node(node_in2)
        conn2 = self.graph.add_connection(node_in2.id, "out", self.node_proc.id, "in1")
        self.assertIsNone(conn2)
        self.assertEqual(len(self.graph.connections), 1) # Only first connection exists

    def test_remove_connection(self):
        """Test removing a connection explicitly from the graph."""
        self.graph.add_node(self.node_in)
        self.graph.add_node(self.node_proc)
        conn = self.graph.add_connection(self.node_in.id, "out", self.node_proc.id, "in1")
        self.assertEqual(len(self.graph.connections), 1)
        out_port = self.node_in.get_output_port("out")
        in_port = self.node_proc.get_input_port("in1")
        self.assertTrue(out_port.is_connected())
        self.assertTrue(in_port.is_connected())

        self.graph.remove_connection(conn) # Should call conn.remove() internally

        self.assertEqual(len(self.graph.connections), 0)
        self.assertFalse(out_port.is_connected())
        self.assertFalse(in_port.is_connected())

    def test_remove_node_removes_connections(self):
        """Test that removing a node also removes its connections from the graph."""
        self.graph.add_node(self.node_in)
        self.graph.add_node(self.node_proc)
        self.graph.add_node(self.node_out)
        conn1 = self.graph.add_connection(self.node_in.id, "out", self.node_proc.id, "in1")
        conn2 = self.graph.add_connection(self.node_proc.id, "res", self.node_out.id, "final_in")
        self.assertEqual(len(self.graph.connections), 2)
        self.assertTrue(self.node_in.get_output_port("out").is_connected())
        self.assertTrue(self.node_proc.get_input_port("in1").is_connected())
        self.assertTrue(self.node_proc.get_output_port("res").is_connected())
        self.assertTrue(self.node_out.get_input_port("final_in").is_connected())

        # Remove the middle node
        self.graph.remove_node(self.node_proc.id)

        self.assertEqual(len(self.graph.nodes), 2) # In and Out nodes remain
        self.assertNotIn(self.node_proc.id, self.graph.nodes)
        self.assertEqual(len(self.graph.connections), 0) # Both connections should be gone

        # Check ports on remaining nodes are disconnected
        self.assertFalse(self.node_in.get_output_port("out").is_connected())
        self.assertFalse(self.node_out.get_input_port("final_in").is_connected())

    def test_node_disconnect_all_removes_connections_from_graph(self):
        """Verify node.disconnect_all notifies the graph to remove connections."""
        self.graph.add_node(self.node_in)
        self.graph.add_node(self.node_proc)
        self.graph.add_node(self.node_out)
        conn1 = self.graph.add_connection(self.node_in.id, "out", self.node_proc.id, "in1")
        conn2 = self.graph.add_connection(self.node_proc.id, "res", self.node_out.id, "final_in")
        self.assertEqual(len(self.graph.connections), 2)

        # Disconnect the middle node
        self.node_proc.disconnect_all()

        self.assertEqual(len(self.graph.connections), 0) # Both connections should be gone
        self.assertFalse(self.node_in.get_output_port("out").is_connected())
        self.assertFalse(self.node_proc.get_input_port("in1").is_connected())
        self.assertFalse(self.node_proc.get_output_port("res").is_connected())
        self.assertFalse(self.node_out.get_input_port("final_in").is_connected())


if __name__ == '__main__':
    unittest.main()