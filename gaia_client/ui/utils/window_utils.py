# window_utils.py
from typing import Tuple
from dataclasses import dataclass

import qgis

class Singleton(type):
    """A metaclass that creates a Singleton base type when called."""
    _instances = {}
    
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            if 'iface' not in kwargs and not cls._instances:
                raise ValueError("WindowUtils must be initialized with 'iface' once.")
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

@dataclass
class WindowConfig:
    """Window configuration constants."""
    BUTTON_WIDTH: int = 100
    BUTTON_HEIGHT: int = 30

class WindowUtils(metaclass=Singleton):
    """Utility class for window-related operations."""
    
    def __init__(self, iface):
        if hasattr(self, 'initialized') and self.initialized:
            return  # Avoid re-initialization
        self.iface = iface
        self.config = WindowConfig()
        self.initialized = True
    
    def get_main_window_width(self) -> int:
        """Retrieve the main QGIS window's width."""
        return self.iface.mainWindow().width()
    
    def get_inner_main_window_dimensions(self) -> Tuple[int, int]:
        """Retrieve the inner dimensions of the main QGIS window's central widget."""
        central_widget = self.iface.mainWindow().centralWidget()
        return central_widget.width(), central_widget.height()
    
    def get_iface(self):
      """Get the QGIS interface instance."""
      return qgis.utils.iface