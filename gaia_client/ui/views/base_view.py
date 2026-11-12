from PyQt5.QtWidgets import QVBoxLayout, QWidget
from abc import ABC, abstractmethod


class BaseView(ABC):
    def __init__(self, iface):
        self.iface = iface

        self.widget = QWidget()
        self.layout = QVBoxLayout()
        self.widget.setLayout(self.layout)

    # @abstractmethod
    # def setup_ui(self):
    #     """This method must be implemented by child classes to set up their UI components."""
    #     pass

    @abstractmethod
    def clean_up(self):
        """This method must be implemented by child classes to clean up their UI components."""
        self.widget.setParent(None)
        self.widget.deleteLater()

    def _finished_view_setup(self):
        self.widget.setLayout(self.layout)

    def get_layout(self):
        return self.layout

    def get_widget(self):
        return self.widget
