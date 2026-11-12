# main_dialog.py
from PyQt5.QtWidgets import (
    QWidget,
    QDockWidget,
    QSizePolicy,
)
from PyQt5.QtCore import Qt, QEvent, QObject

from gaia_client.ui.handlers.layer_handler import LayerHandler
from gaia_client.ui.utils.router import GaiaRouter
from gaia_client.ui.utils.window_utils import WindowUtils
from gaia_client.ui.views.project import ViewProject
from gaia_client.ui.views.project_run_create import CreateProjectRunView
from gaia_client.ui.views.project_start import ProjectStart
from gaia_client.ui.i18n.se import plugin_name


class MainDockWidget(QDockWidget):
    """Main dock widget containing project list."""

    def __init__(self, iface, parent=None):
        super(MainDockWidget, self).__init__(plugin_name, parent)
        self.iface = iface
        self.window_utils = WindowUtils()  # Access the singleton instance
        self.layer_handler = LayerHandler()
        self._setup_ui()

        # self.setFont(QFont("Arial", 12))

        # change the title size and colour
        self.setStyleSheet("QDockWidget::title { color: #fff}")
        # self.layer_handler.load_logo_layer()
        # Install event filter to handle resize events
        self.iface.mainWindow().installEventFilter(self)

    def shutdown(self):
        """Stop everything this dock started: the current view (and its status
        polling timers) and the main-window event filter."""
        try:
            router = self.gaia_router
            if router.current_view is not None:
                router.current_view.clean_up()
                router.current_view = None
        finally:
            self.iface.mainWindow().removeEventFilter(self)

    def eventFilter(self, obj, event):
        if obj == self.iface.mainWindow() and event.type() == QEvent.Resize:
            # Main window was resized
            self.adjust_dock_width()
        return QObject.eventFilter(self, obj, event)

    def adjust_dock_width(self):
        """Adjust the dock widget's width based on the main window's width."""
        main_window_width = self.window_utils.get_main_window_width()
        min_width = 500
        desired_width = int(main_window_width * 0.2)
        max_width = desired_width if desired_width > min_width else min_width
        print('desired width:', desired_width, "min width:", min_width, "max width:", max_width)
        self.setMinimumWidth(min_width)
        self.setMaximumWidth(max_width)

    def _setup_ui(self):
        """Initialize UI components."""
        # Set allowed areas to right side only if desired
        self.setAllowedAreas(Qt.RightDockWidgetArea)

        # Set features to disable closing, making it persistent
        self.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetClosable)

        # Create the main widget for the dock
        main_widget = QWidget(self)
        self.setWidget(main_widget)

        # Add the view router
        self.gaia_router = GaiaRouter(self.iface, main_widget)
        self._register_routes()

        # self.layout = QHBoxLayout()
        # main_layout.setLayout(self.layout)
        # self.area_selector = AreaSelector(self.iface, self.layout)

        # Ensure the dock widget occupies full height
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)

        # Initial adjustment of dock width
        self.adjust_dock_width()

    def _register_routes(self):
        """
        Each router has to register its callback (the render function) for its own view
        to make sure that the view will be rendered when we call the "goto_view" function.
        """

        self.gaia_router.register_route_callback("project_start", ProjectStart)
        self.gaia_router.register_route_callback("project", ViewProject)
        self.gaia_router.register_route_callback(
            "project_create_run", CreateProjectRunView
        )

        self.gaia_router.set_initial_route("project_start")
