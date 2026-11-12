from PyQt5.QtWidgets import (
    QHBoxLayout,
)
from gaia_client.ui.utils.window_utils import Singleton


class GaiaRouter(metaclass=Singleton):
    """Router to handle showing different views"""

    def __init__(self, iface, main_widget=None):
        if hasattr(self, "initialized") and self.initialized:
            return
        if main_widget is None:
            raise ValueError("GaiaRouter must be initialized with 'main_widget' once.")

        self.iface = iface
        self.current_route = None
        self.initial_route = None
        self.main_widget = main_widget
        # the router will maintain one layout for all views
        # in order to switch between them, we use widgets (since we can not remove layouts)
        self.layout = QHBoxLayout()
        self.main_widget.setLayout(self.layout)

        self.initialized = True
        self.route_callbacks = {}
        self.routes_counter = 0
        self.current_view = None

    @classmethod
    def get_instance(cls):
        """Get the router instance without needing the layout parameter"""
        if cls not in cls._instances:
            raise RuntimeError(
                "Router hasn't been initialized yet. Call with main_layout first."
            )
        return cls._instances[cls]

    def register_route_callback(self, route_name: str, callback: type):
        """Register a callback for a specific route"""
        self.route_callbacks[route_name] = RouterViewRegistry(
            route_name, callback, self.routes_counter
        )
        self.routes_counter = self.routes_counter + 1

    def handle_route(self, route_name: str, **kwargs) -> None:
        print(f"Handling route: {route_name}")
        self.current_route = route_name

        # find the view, instantiate it and add it to the layout
        if route_name in self.route_callbacks:
            # get the view class type
            view_type = self.route_callbacks[route_name].view_type
            # instantiate the view

            # NOTE: Most API calls are made when we create the view here
            new_view = view_type(self.iface, **kwargs)
            # Remove current view if exists (this is the new cleaning)
            if self.current_view is not None:
                self.current_view.clean_up()
                self.current_view = None
            # add the view's widget to the layout
            self.layout.addWidget(new_view.get_widget())
            # needed so it is not garbage collected
            self.current_view = new_view
        else:
            print("Invalid route, what do we do now?")

    def set_initial_route(self, route_name: str, **kwargs):
        """Set and render the initial route after all routes are registered"""
        if self.current_route is None:
            self.initial_route = route_name
            self.handle_route(route_name, **kwargs)

    def go_home(self):
        """Go to the initial route"""
        if self.initial_route is not None:
            self.handle_route(self.initial_route)


class RouterViewRegistry:
    """A class registry for router views. In case we want to move to using QStackedLayout"""

    # Note. Using stack layout means creating all views once and then
    # loading data on them in case they have to be reused.

    def __init__(self, name, view_type, index):
        self.name = name
        self.view_type = view_type
        self.index = index
