from PySide6.QtWidgets import QGraphicsEllipseItem, QGraphicsItem, QGraphicsSceneMouseEvent
from PySide6.QtGui import QBrush, QPen, QColor, QPainterPath
from PySide6.QtCore import Qt, QRectF, QPointF

# Assuming node_graph package is importable
from node_graph import Port, PortType

PORT_RADIUS = 5
PORT_DIAMETER = PORT_RADIUS * 2

class UIPort(QGraphicsEllipseItem):
    """Represents a visual port (input/output point) on a UINode."""

    def __init__(self, parent_node_item: 'UINode', backend_port: Port):
        super().__init__(-PORT_RADIUS, -PORT_RADIUS, PORT_DIAMETER, PORT_DIAMETER, parent=parent_node_item)
        self._parent_node_item = parent_node_item
        self._backend_port = backend_port
        self._connection_items: list['UIConnection'] = [] # Connections attached to this UI port

        # Basic styling
        self.setBrush(QBrush(QColor("lightblue") if backend_port.port_type == PortType.INPUT else QColor("lightgreen")))
        self.setPen(QPen(Qt.black))
        self.setAcceptHoverEvents(True) # Needed for hover feedback if desired

        # Tooltip shows port name and type
        self.setToolTip(f"{backend_port.name} ({backend_port.data_type.__name__})")

    @property
    def backend_port(self) -> Port:
        return self._backend_port

    @property
    def parent_node_item(self) -> 'UINode':
        return self._parent_node_item

    def get_scene_position(self) -> QPointF:
        """Get the port's position in scene coordinates."""
        return self.scenePos()

    def add_connection_item(self, connection_item: 'UIConnection'):
        if connection_item not in self._connection_items:
            self._connection_items.append(connection_item)

    def remove_connection_item(self, connection_item: 'UIConnection'):
        try:
            self._connection_items.remove(connection_item)
        except ValueError:
            pass # Ignore if not found

    def update_connection_positions(self):
        """Tell connected lines to update their paths."""
        for conn_item in self._connection_items:
            conn_item.update_path()

    # --- Mouse Events for Connection Dragging (handled by scene for now) ---
    # Override mousePressEvent, mouseMoveEvent, mouseReleaseEvent if needed
    # directly on the port, but starting drag logic is often cleaner in the scene.

    def __repr__(self):
        node_name = self.parent_node_item.backend_node.name if self.parent_node_item else "Detached"
        return f"<UIPort name='{self.backend_port.name}' node='{node_name}'>"