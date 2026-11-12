from typing import Optional
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout
from gaia_client.ui.utils.safe_text import SafeLabel


class ProjectItemWidget(QWidget):
    """Widget to display a single project item."""

    def __init__(self, name: str, description: str, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._setup_ui(name, description)

    def _setup_ui(self, name: str, description: str) -> None:
        """Initialize UI components for project item."""
        layout = QVBoxLayout()
        self.name_label = SafeLabel(name)
        self.description_label = SafeLabel(description)
        layout.addWidget(self.name_label)
        layout.addWidget(self.description_label)
        self.setLayout(layout)
