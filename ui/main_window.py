from PySide6.QtWidgets import QMainWindow, QGraphicsView, QWidget, QVBoxLayout
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter
from node_graph import Graph # Backend graph
from .node_graph_scene import NodeGraphScene

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Basic Node Graph Editor")
        self.setGeometry(100, 100, 800, 600) # x, y, width, height

        # Initialize backend graph
        self.backend_graph = Graph()

        # Initialize UI components
        self.scene = NodeGraphScene(self.backend_graph)
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.Antialiasing) # Smoother lines
        self.view.setDragMode(QGraphicsView.RubberBandDrag) # Allow selecting multiple items
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # Set central widget
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        layout.addWidget(self.view)
        layout.setContentsMargins(0, 0, 0, 0) # Use full space
        self.setCentralWidget(central_widget)

        # TODO: Add menu bar, toolbars, properties panel etc. later

    # Override closeEvent if needed for cleanup or saving prompts
    # def closeEvent(self, event):
    #     # Add save confirmation logic here
    #     super().closeEvent(event)