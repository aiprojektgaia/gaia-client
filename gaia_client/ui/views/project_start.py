from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QPushButton, QHBoxLayout, QVBoxLayout, QLabel, QMessageBox

from gaia_client.storage.plugin_storage import PluginStore

from gaia_client.api.requests.project import ProjectApi
from gaia_client.ui.utils.view import goto_view
from gaia_client.ui.views.base_view import BaseView
from gaia_client.ui.views.dialogs.settings_dialog import SettingsDialog
from gaia_client.ui.utils.window_utils import WindowUtils
from gaia_client.ui.widgets.project_table import ProjectTable
from gaia_client.ui.widgets.id_widget import remove_widget_by_id
from gaia_client.api.models.Project import Project
from gaia_client.ui.i18n.se import (
    project_start_create_button,
    project_start_settings_button,
    project_start_help_title,
    project_start_help_description,
    project_start_help_description_pt2,
    generic_error_title,
    project_error_message,
    project_delete_title,
    project_delete_description,
    project_delete_error_message,
)
from gaia_client.ui.views.dialogs.create_project_dialog import (
    show_create_project_dialog,
)
from gaia_client.ui.utils.safe_text import SafeLabel, ask_yes_no


class ProjectStart(BaseView):
    def __init__(self, iface, **kwargs):
        super().__init__(iface)

        window_utils_config = WindowUtils(self.iface).config
        self._setup_toolbar(window_utils_config)
        self._setup_project_table(self.layout)

        print("ProjectStart - [setup done]")

    def _is_plugin_setup(self):
        store = PluginStore()
        gaia_url = store.get("gaia_backend_url", "")
        return gaia_url

    def clean_up(self):
        super().clean_up()

    def _setup_toolbar(self, window_utils_config):
        horizontal_layout = QHBoxLayout()

        # settings
        settings_button = QPushButton(project_start_settings_button)
        settings_icon = QIcon(
            ":images/themes/default/console/iconProcessingConsole.svg"
        )
        settings_button.setIcon(settings_icon)
        settings_button.setFixedHeight(window_utils_config.BUTTON_HEIGHT)
        settings_button.clicked.connect(self._show_settings_dialog)
        horizontal_layout.addWidget(settings_button)

        # create new project
        create_project_button = QPushButton(project_start_create_button)
        create_project_button.setFixedHeight(window_utils_config.BUTTON_HEIGHT)
        add_icon = QIcon(":images/themes/default/symbologyAdd.svg")
        create_project_button.setIcon(add_icon)
        horizontal_layout.addWidget(create_project_button)

        if not self._is_plugin_setup():
            create_project_button.setCursor(Qt.ForbiddenCursor)
            create_project_button.setDisabled(True)
            create_project_button.setToolTip(project_start_help_description)

        create_project_button.clicked.connect(self.create_project_clicked)

        self.layout.addLayout(horizontal_layout)

    def create_project_clicked(self):
        show_create_project_dialog(self.create_project_callback)

    def create_project_callback(self, inputs):
        project_api = ProjectApi()
        project = project_api.create_project(
            name=inputs["name"],
            description=inputs["description"],
            wms_url=inputs["wms_url"],
            layer_name=inputs["layer_name"],
            epsg=inputs["epsg"],
            mpp=inputs["resolution"],
        )
        if project:
            goto_view("project", project=project)
        else:
            QMessageBox.critical(
                None,
                generic_error_title,
                project_error_message,
            )

    def _delete_project(self, project: Project):
        confirmed = ask_yes_no(
            None,
            project_delete_title,
            f"{project_delete_description} \n  * {project.name}?",
        )

        if confirmed:
            api = ProjectApi()
            success = api.delete_project(project.id)
            if success:
                remove_widget_by_id(self.project_table.table_layout, project.id)
            else:
                QMessageBox.critical(
                    None,
                    generic_error_title,
                    project_delete_error_message,
                )

    def _show_help(self):
        help_layout = QVBoxLayout()
        help_layout.setContentsMargins(0, 20, 0, 0)
        help_title = SafeLabel(project_start_help_title)
        help_title.setStyleSheet("font-size: 16px; font-weight: bold;")
        help_layout.addWidget(help_title)
        help_description = SafeLabel(
            project_start_help_description + "\n\n" + project_start_help_description_pt2
        )
        help_description.setWordWrap(True)
        help_description.setStyleSheet("font-size: 14px;")
        help_layout.addWidget(help_description)
        help_layout.addStretch(1)
        self.layout.addLayout(help_layout)

    def _setup_project_table(self, layout):
        """Setup project table widget."""
        print("Setting up project table")
        if not self._is_plugin_setup():
            self._show_help()
            return

        project_api = ProjectApi()
        existing_projects = project_api.get_projects()
        self.project_table = ProjectTable(layout)
        for project in existing_projects:
            self.project_table.add_table_row(project, self._delete_project)

        layout.addWidget(self.project_table.widget)
        layout.addStretch(1)

    def _show_settings_dialog(self):
        print("calling to start dialog")
        dialog = SettingsDialog(self.widget)
        response = dialog.exec()
        goto_view("project_start")
        print("dialog finished", response)
