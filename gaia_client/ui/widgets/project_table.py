from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QScrollArea,
    QGroupBox,
)
from PyQt5.QtCore import Qt, QObject

from gaia_client.api.models.Project import Project
from gaia_client.ui.i18n.se import (
    project_start_open_button,
    project_table_name,
    project_table_timestamp,
    project_table_delete_run,
)
from gaia_client.ui.utils.view import goto_view
from gaia_client.ui.widgets.button import (
    create_icon_button,
    make_blue_button_with_icon,
)
from gaia_client.ui.widgets.id_widget import QIdWidget
from gaia_client.ui.utils.safe_text import SafeLabel, safe_tooltip


class ProjectTable(QObject):
    def __init__(self, layout, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.parent_layout = layout

        # components widget and layout
        self.widget = QWidget()
        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignLeft)
        self.layout.setSpacing(10)

        # specific for the table part
        self.table_widget = QScrollArea()
        # self.table_widget.setStyleSheet("background-color: red;")
        self.table_layout = QVBoxLayout()

        self.group_box = QGroupBox()
        self.group_box.setLayout(self.table_layout)

        # defining the scroll area
        self.table_widget.setWidget(self.group_box)
        self.table_widget.setWidgetResizable(True)
        self.table_widget.setMaximumHeight(700)
        self.table_widget.setFrameShape(QScrollArea.NoFrame)
        self.group_box.setStyleSheet("""
            QGroupBox {
                border: none;
            }
        """)

        self.setUI()
        self.layout.addWidget(self.table_widget)
        self.widget.setLayout(self.layout)
        self.parent_layout.addWidget(self.widget)

    def setUI(self):
        table_header = self._create_table_header()
        self.table_layout.addWidget(table_header)

    def add_table_row(self, project: Project, delete_callback):
        row_widget = QIdWidget(project.id)
        row_widget.setStyleSheet("""
            QIdWidget {
                background-color: white;
                border-bottom: 1px solid #aaa;
                padding: 8px;
            }
        """)
        row_layout = QHBoxLayout()
        row_layout.setContentsMargins(8, 8, 8, 8)  # Add horizontal padding
        row_widget.setLayout(row_layout)
        row_layout.setAlignment(Qt.AlignLeft)

        name = SafeLabel(project.name)
        name.setStyleSheet("border:none;")
        name.setFixedWidth(100)
        name.setToolTip(safe_tooltip(project.description))
        row_layout.addWidget(name)

        timestamp = SafeLabel(project.created_at.strftime("%Y-%m-%d %H:%M"))
        timestamp.setFixedWidth(100)
        timestamp.setStyleSheet("border:none;")
        row_layout.addWidget(timestamp)
        row_layout.addStretch(1)

        delete_button = create_icon_button(
            ":images/themes/default/mActionDeleteSelected.svg",
            project_table_delete_run,
            lambda: delete_callback(project),
        )
        row_layout.addWidget(delete_button)

        goto_button = make_blue_button_with_icon(
            project_start_open_button,
            ":images/themes/default/mActionArrowRight.svg",
        )
        goto_button.clicked.connect(lambda: goto_view("project", project=project))
        row_layout.addWidget(goto_button)
        self.table_layout.addWidget(row_widget)

    @staticmethod
    def _create_table_header() -> QWidget:
        """Create a table header."""
        widget = QWidget()
        widget.setStyleSheet("""
            QWidget {
                border-bottom: 1px solid #aaa;
                padding: 8px 0;
            }
        """)
        layout = QHBoxLayout()
        layout.setContentsMargins(8, 8, 8, 8)  # Match row padding
        widget.setLayout(layout)
        layout.setAlignment(Qt.AlignLeft)

        name = SafeLabel(project_table_name)
        name.setStyleSheet("font-weight: bold; border: none;")
        name.setFixedWidth(100)
        layout.addWidget(name)

        timestamp = SafeLabel(project_table_timestamp)
        timestamp.setStyleSheet("font-weight: bold; border: none;")
        timestamp.setFixedWidth(100)
        layout.addWidget(timestamp)

        return widget
