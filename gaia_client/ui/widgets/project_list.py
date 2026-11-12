from typing import Optional
from PyQt5.QtWidgets import QWidget, QListWidget, QListWidgetItem
from gaia_client.ui.widgets.project_item import ProjectItemWidget


class ProjectListWidget(QListWidget):
    """Widget to display list of projects."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

    def add_project(self, name: str, description: str) -> None:
        """Add a project to the list."""
        item = QListWidgetItem(self)
        widget = ProjectItemWidget(name, description)
        item.setSizeHint(widget.sizeHint())
        self.addItem(item)
        self.setItemWidget(item, widget)
