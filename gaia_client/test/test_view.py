import time

from PyQt5.QtWidgets import QLabel, QVBoxLayout, QHBoxLayout
from PyQt5.QtCore import QTimer

from gaia_client.ui.views.base_view import BaseView
from gaia_client.ui.views.components.validated_input import (
    ValidatedInput,
)
from gaia_client.ui.widgets.header import HeaderWidget
from gaia_client.ui.widgets.notification_area import NotificationArea


class TestView(BaseView):
    def __init__(self, iface, **kwargs):
        super().__init__(iface)
        self.progress_value = 0
        self.notification_area = None
        self.progress_timer = None

        self.render_header()
        self.render_notification_area()
        self.render_inputs()

        # Start the progress timer after all UI elements are rendered
        self.start_progress_timer()

    def clean_up(self):
        if self.progress_timer:
            self.progress_timer.stop()
            self.progress_timer = None

    def start_progress_timer(self):
        # Create a timer that updates the progress bar every 100ms
        self.progress_timer = QTimer()
        self.progress_timer.timeout.connect(self.update_progress)
        self.progress_timer.start(100)  # 100ms interval

    def update_progress(self):
        if self.notification_area:
            self.notification_area.update_progress(self.progress_value, 100)
            self.progress_value += 1
            if self.progress_value >= 100:
                self.progress_value = 0

    def render_notification_area(self):
        self.notification_area = NotificationArea("Title", "Initial message")
        self.layout.addWidget(self.notification_area)
        self.notification_area.show()

    def render_header(self):
        header_layout = QHBoxLayout()
        header_layout.addWidget(QLabel("Test view"))
        self.layout.addLayout(header_layout)

    def render_inputs(self):
        vertical_layout = QVBoxLayout()

        header_widget = HeaderWidget("Test view", "project_start")
        vertical_layout.addWidget(header_widget)

        # With integer validator
        number_input = ValidatedInput(
            "Number:",
        )

        # With regex validator for letters only
        letter_input = ValidatedInput(
            "Letters:",
            error_message="Please enter only letters",
        )

        # With regex validator for alphanumeric
        alphanumeric_input = ValidatedInput(
            "Alphanumeric:",
            error_message="Please enter only letters or numbers",
        )

        vertical_layout.addWidget(number_input)
        vertical_layout.addWidget(letter_input)
        vertical_layout.addWidget(alphanumeric_input)
        self.layout.addLayout(vertical_layout)
