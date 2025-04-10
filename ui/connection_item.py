from PySide6.QtWidgets import QGraphicsPathItem
from PySide6.QtGui import QPen, QPainterPath, QColor
from PySide6.QtCore import Qt

# Forward reference for type hinting
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .port_item import UIPort
    from node_graph import Connection # Backend connection

class UIConnection(QGraphicsPathItem):
    """Represents a visual connection (line/curve) between two UIPorts."""

    def __init__(self, start_port_item: 'UIPort', end_port_item: 'UIPort', backend_connection: 'Connection'):
        super().__init__()
        self._start_port_item = start_port_item
        self._end_port_item = end_port_item
        self._backend_connection = backend_connection # Store reference if needed

        # Add this visual connection to the ports it connects
        self._start_port_item.add_connection_item(self)
        self._end_port_item.add_connection_item(self)

        self.setPen(QPen(Qt.black, 2)) # Basic styling
        self.setZValue(-1) # Draw connections behind nodes/ports

        self.update_path() # Initial drawing

    @property
    def start_port_item(self) -> 'UIPort':
        return self._start_port_item

    @property
    def end_port_item(self) -> 'UIPort':
        return self._end_port_item

    @property
    def backend_connection(self) -> 'Connection':
        return self._backend_connection

    def update_path(self):
        """Recalculates and sets the path based on port positions."""
        if not self._start_port_item or not self._end_port_item:
            # Handle cases where ports might have been deleted unexpectedly
            self.setPath(QPainterPath()) # Clear path
            return

        start_pos = self._start_port_item.mapToScene(0, 0) # Center of port item
        end_pos = self._end_port_item.mapToScene(0, 0) # Center of port item

        path = QPainterPath()
        path.moveTo(start_pos)

        # Simple straight line for basic version
        # path.lineTo(end_pos)

        # Basic Bezier curve calculation
        dx = end_pos.x() - start_pos.x()
        dy = end_pos.y() - start_pos.y()
        ctrl_offset_x = dx * 0.5 # Adjust for more/less curve
        # ctrl_offset_y = 0 # Flat curve initially

        # Control points based on direction
        ctrl1 = QPointF(start_pos.x() + ctrl_offset_x, start_pos.y())
        ctrl2 = QPointF(end_pos.x() - ctrl_offset_x, end_pos.y())

        path.cubicTo(ctrl1, ctrl2, end_pos)

        self.setPath(path)

    def destroy(self):
        """Cleanly remove the connection item and references."""
        if self._start_port_item:
            self._start_port_item.remove_connection_item(self)
        if self._end_port_item:
            self._end_port_item.remove_connection_item(self)
        # Optionally remove from scene if added directly (usually managed by scene removal)
        if self.scene():
            self.scene().removeItem(self)
        self._start_port_item = None
        self._end_port_item = None
        self._backend_connection = None # Clear backend reference too