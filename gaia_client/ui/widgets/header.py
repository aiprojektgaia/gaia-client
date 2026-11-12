from typing import Callable

from PyQt5.QtWidgets import QWidget, QPushButton, QLabel, QHBoxLayout, QVBoxLayout, QFrame
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QSize

from gaia_client.ui.utils.view import goto_view, go_home
from gaia_client.ui.views import h1_size, title_height
from gaia_client.ui.i18n.se import project_back_button, project_home_button
from gaia_client.ui.utils.safe_text import SafeLabel, safe_tooltip


class HeaderWidget(QWidget):
    def __init__(
        self,
        title: str,
        previous_view_callback: Callable | str = None,
        previous_view_title: str = project_back_button,
        title_hint: str = None,
        parent=None,
    ):
        super().__init__(parent)
        self.previous_view = None
        self.previous_view_callback = None
        if isinstance(previous_view_callback, str):
            self.previous_view = previous_view_callback
        elif isinstance(previous_view_callback, Callable):
            self.previous_view_callback = previous_view_callback
        self.previous_view_title = previous_view_title
        self.layout = QVBoxLayout()
        self.top_row = QHBoxLayout()
        self.bottom_row = QHBoxLayout()

        self.layout.addLayout(self.top_row)
        self.layout.addLayout(self.bottom_row)

        self.render_home_button()
        self.render_back_button()
        self.render_title(title, title_hint)
        self.render_break_line()

        self.setLayout(self.layout)

    def render_home_button(self):
        home_icon = QIcon(":images/themes/default/mActionQgisHomePage.png")
        self.home_button = QPushButton()
        self.home_button.setIcon(home_icon)
        self.home_button.setIconSize(QSize(20, 20))
        self.home_button.setFixedSize(30, 30)
        self.home_button.setToolTip(project_home_button)
        self.home_button.setCursor(Qt.PointingHandCursor)
        self.home_button.setFlat(True)
        self.home_button.clicked.connect(self.home_button_clicked)
        self.top_row.addWidget(self.home_button)

    def home_button_clicked(self):
        go_home()

    def render_back_button(self):
        if self.previous_view is None and self.previous_view_callback is None:
            return

        self.back_icon = QIcon(":images/themes/default/mActionArrowLeft.svg")
        self.back_button = QPushButton()
        self.back_button.setText(self.previous_view_title)
        self.back_button.setIcon(self.back_icon)
        self.back_button.clicked.connect(self.back_button_clicked)
        self.back_button.setToolTip(project_back_button)
        self.back_button.setCursor(Qt.PointingHandCursor)
        self.back_button.setIconSize(QSize(20, 20))
        self.back_button.setFlat(True)
        self.bottom_row.addWidget(self.back_button)
        self.bottom_row.addStretch(1)

    def back_button_clicked(self):
        if self.previous_view:
            goto_view(self.previous_view)
        elif self.previous_view_callback:
            self.previous_view_callback()

    def render_title(self, title: str, title_hint: str = None):
        self.title = SafeLabel(title)
        self.top_row.addWidget(self.title)
        self.title.setContentsMargins(16, 4, 0, 0)
        self.title.setStyleSheet(f"font-size: {h1_size}px;")
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setFixedHeight(title_height)
        self.title.setToolTip(safe_tooltip(title_hint if title_hint is not None else title))

    def render_break_line(self):
        frame = QFrame()
        frame.setFrameShape(QFrame.HLine)
        self.layout.addWidget(frame)
