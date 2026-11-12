from PyQt5.QtWidgets import (
    QVBoxLayout,
    QLabel,
    QProgressBar,
    QFrame,
)
from PyQt5.QtCore import Qt
from gaia_client.ui.utils.safe_text import SafeLabel


class NotificationArea(QFrame):
    def __init__(self, title: str, initial_message: str, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        #self.setLayout(self.layout)
        self.layout.setAlignment(Qt.AlignCenter)
        self.layout.setContentsMargins(15, 15, 15, 15)
        self.layout.setSpacing(8)

        # Set frame properties
        self.setFrameShape(QFrame.Box)
        self.setFrameShadow(QFrame.Plain)
        self.setFixedHeight(100)

        # Set style for the frame
        self.setStyleSheet("""
            NotificationArea {
                background-color: #f8f8f8;
                border: 1px solid #ddd;
                border-radius: 4px;
            }
            QLabel {
                background: transparent;
            }
            QProgressBar {
                text-align: center;
                border: 1px solid #ddd;
                border-radius: 2px;
                background-color: white;
            }
            QProgressBar::chunk {
                background-color: #2196F3;
            }
        """)

        # Create title label with bold text
        self.title_label = SafeLabel(title)
        self.title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.title_label)

        # Create progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setAlignment(Qt.AlignCenter)
        self.progress_bar.setFixedHeight(20)  # Set a fixed height for the progress bar
        self.layout.addWidget(self.progress_bar)

        # Create message label
        self.message_label = SafeLabel(initial_message)
        self.message_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.message_label)

        self.hide()

    def update_notification_message(self, message: str):
        self.message_label.setText(message)

    def update_progress(self, current_value: int, total_value: int):
        """Update the progress bar value (0-100)"""
        self.progress_bar.setValue(current_value)
        self.progress_bar.setMaximum(total_value)
