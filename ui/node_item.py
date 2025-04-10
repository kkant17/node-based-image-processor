from PySide6.QtWidgets import (QGraphicsRectItem, QGraphicsItem, QGraphicsTextItem,
                               QStyleOptionGraphicsItem, QWidget)
from PySide6.QtGui import QBrush, QPen, QPainter, QColor, QFont
from PySide6.QtCore import Qt, QRectF, QPointF
from typing import Optional, Any
from node_graph import Node, PortType # Backend node
from .port_item import UIPort, PORT_DIAMETER, PORT_RADIUS # Visual port

NODE_WIDTH = 150
NODE_HEIGHT = 80 # Base height, might need adjusting based on ports
HEADER_HEIGHT = 20

class UINode(QGraphicsRectItem):
    """Represents a visual node in the scene."""

    def __init__(self, backend_node: Node):
        # Calculate initial height based on port count
        max_ports = max(len(backend_node.input_ports), len(backend_node.output_ports))
        node_height = max(NODE_HEIGHT, HEADER_HEIGHT + (max_ports * (PORT_DIAMETER + 5)) + 5)
        super().__init__(0, 0, NODE_WIDTH, node_height)

        self._backend_node = backend_node
        self._ui_ports: dict[str, UIPort] = {} # Map backend port name to UIPort item

        # Styling
        self.setBrush(QBrush(QColor("#555555"))) # Dark gray background
        self.setPen(QPen(Qt.black))
        self.setFlags(QGraphicsItem.ItemIsMovable |
                      QGraphicsItem.ItemIsSelectable |
                      QGraphicsItem.ItemSendsGeometryChanges) # Important for connections

        # Node Title
        self.title = QGraphicsTextItem(backend_node.name, self)
        self.title.setDefaultTextColor(Qt.white)
        self.title.setFont(QFont("Arial", 10, QFont.Bold))
        title_x = (NODE_WIDTH - self.title.boundingRect().width()) / 2
        self.title.setPos(title_x, 0)

        self._create_ports()

    @property
    def backend_node(self) -> Node:
        return self._backend_node

    def _create_ports(self):
        """Create UIPort items based on the backend node's ports."""
        input_y = HEADER_HEIGHT + 5
        output_y = HEADER_HEIGHT + 5

        for port_name, backend_port in self._backend_node.input_ports.items():
            port_item = UIPort(self, backend_port)
            port_item.setPos(0, input_y + PORT_RADIUS) # Left edge, centered vertically
            self._ui_ports[port_name] = port_item
            input_y += PORT_DIAMETER + 5 # Spacing

        for port_name, backend_port in self._backend_node.output_ports.items():
            port_item = UIPort(self, backend_port)
            port_item.setPos(NODE_WIDTH, output_y + PORT_RADIUS) # Right edge, centered vertically
            self._ui_ports[port_name] = port_item
            output_y += PORT_DIAMETER + 5 # Spacing

    def get_ui_port(self, port_name: str) -> Optional[UIPort]:
        return self._ui_ports.get(port_name)

    # Override itemChange to update connections when node moves
    def itemChange(self, change: QGraphicsItem.GraphicsItemChange, value: Any) -> Any:
        if change == QGraphicsItem.ItemPositionHasChanged:
            # Update all connections attached to this node's ports
            for port_item in self._ui_ports.values():
                port_item.update_connection_positions()
        return super().itemChange(change, value)

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: Optional[QWidget] = None):
        # Draw header background
        header_rect = QRectF(0, 0, NODE_WIDTH, HEADER_HEIGHT)
        painter.fillRect(header_rect, QColor("#333333")) # Slightly darker header

        # Let the base class draw the main rectangle outline etc.
        super().paint(painter, option, widget)

    def destroy(self):
        """Clean up UI elements before node removal."""
        # Ports are children, should be removed automatically, but clear refs
        self._ui_ports.clear()
        # Connections attached to ports need to be handled by the scene/graph removal logic
        # Base class removal from scene handles visual cleanup
        if self.scene():
            self.scene().removeItem(self)