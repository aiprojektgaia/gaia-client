from PyQt5.QtWidgets import (
    QPushButton,
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
from gaia_client.ui.views import icon_height, icon_width


def make_nice_button(text: str, width=100) -> QPushButton:
    button = QPushButton(text)
    button.setFixedWidth(width)
    button.setStyleSheet("""
        QPushButton {
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 4px;
            padding: 5px;
        }
        QPushButton:hover {
            background-color: #45a049;
        }
        QPushButton:pressed {
            background-color: #3d8b40;
        }
    """)
    return button


def create_icon_button(icon_path, tool_tip, callback=None, description=None) -> QPushButton:
    icon_button = QPushButton()
    settings_icon = QIcon(icon_path)
    icon_button.setToolTip(tool_tip)
    icon_button.setIcon(settings_icon)
    icon_button.setFixedWidth(icon_width)
    icon_button.setFixedHeight(icon_height)
    if callback is not None:
        icon_button.clicked.connect(callback)
    if description is not None:
        icon_button.setAccessibleName(description)
    return icon_button


def make_blue_button(text: str) -> QPushButton:
    button = QPushButton(text)
    button.setStyleSheet("""
        QPushButton {
            background-color: #3eb1c8;
            color: white;
            border: none;
            border-radius: 4px;
            padding: 5px;
        }
        QPushButton:hover {
            background-color: #4fc3d8;
        }
        QPushButton:pressed {
            background-color: #2e91a8;
        }
    """)
    return button


def make_blue_button_with_icon(text: str, icon_path: str) -> QPushButton:
    button = QPushButton(text)
    icon = QIcon(icon_path)
    button.setIcon(icon)
    button.setLayoutDirection(Qt.RightToLeft)
    button.setFixedHeight(icon_height)
    # button.setContentsMargins(8, 0, 8, 0)
    button.setStyleSheet("""
        QPushButton {
            background-color: #3eb1c8;
            color: white;
            border-radius: 4px;
            padding: 8px;
        }
        QPushButton:hover {
            background-color: #4fc3d8;
        }
        QPushButton:pressed {
            background-color: #2e91a8;
        }
    """)
    return button
