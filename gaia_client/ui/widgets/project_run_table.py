from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QVBoxLayout,
    QLabel,
    QHBoxLayout,
    QPushButton,
    QWidget,
    QScrollArea, )

from gaia_client.api.models.ProjectRun import ProjectRun as ProjectRunModel
from gaia_client.api.models.ProjectRun import TaskStatusEnum
from gaia_client.ui.i18n.se import (
    project_run_table_header,
    project_run_table_header_name,
    project_run_table_header_last_update,
    project_run_table_header_status,
    project_run_table_download_results,
    project_run_table_delete_run,
    project_run_execution_ongoing,
    project_run_param_information,
)
from gaia_client.ui.utils.task_status_helper import get_status_str
from gaia_client.ui.views import h2_size, h2_height
from gaia_client.ui.widgets.button import create_icon_button
from gaia_client.ui.widgets.id_widget import QIdWidget
from gaia_client.ui.widgets.widget_with_id import QidLabel
from gaia_client.ui.utils.safe_text import SafeLabel, safe_tooltip


class ProjectRunTable(QWidget):
    def __init__(self, run_list:list[ProjectRunModel],
                 delete_callback, download_callback, information_callback,
                 parent=None):
        super().__init__(parent)

        self.run_list = run_list
        self.delete_callback = delete_callback
        self.download_callback = download_callback
        self.information_callback = information_callback
        # inner gui elements
        self.table_scroll = None
        self.table_widget = None
        self.table_layout = None

        # components widget and layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        #self.setStyleSheet("background-color: aqua; padding: 0px;")

        self.render_view()

    def render_view(self):
        self.render_header()
        self.render_body()
        #self.render_footer()

    def render_header(self):
        # adding the header
        header = self.create_header(project_run_table_header)
        self.layout.addWidget(header)

    def render_body(self):
        # table header
        table_header = self.create_table_header()
        self.layout.addWidget(table_header)

        # table body
        table_widget = self.create_table_run()
        self.layout.addWidget(table_widget)

    def create_table_run(self):
        self.table_scroll = QScrollArea(self)
        #self.table_scroll.setStyleSheet("QWidget { background: green; }")
        self.table_widget = QWidget(self)
        #self.table_widget.setStyleSheet("QWidget { background: blue; }")
        self.table_layout = QVBoxLayout(self.table_widget)

        for run in self.run_list:
            row_widget = self.add_table_row(
                run,
                delete_callback=self.delete_callback,
                download_callback=self.download_callback,
                information_callback=self.information_callback
            )
            self.table_layout.addWidget(row_widget)

        # Set the properties of the QScrollArea
        self.table_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.table_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.table_scroll.setWidgetResizable(True)
        self.table_scroll.setWidget(self.table_widget)

        # NOTE: do NOT use addStretch here, it will break the expand and will not fill the space
        #self.table_layout.addStretch()

        return self.table_scroll

    @staticmethod
    def create_header(header_text: str):
        header = SafeLabel(header_text)
        header.setStyleSheet(f"font-size: {h2_size}px; font-weight: bold;")
        header.setFixedHeight(h2_height)
        return header

    def render_footer(self):
        final_widget = QWidget(self)
        final_layout = QVBoxLayout(final_widget)
        final_widget.setLayout(final_layout)
        final_layout.setAlignment(Qt.AlignBottom)

        footer = SafeLabel("Hola señor, como estás? -> 2")
        final_layout.addWidget(footer)

        #final_layout.addStretch() # NO!
        final_widget.setStyleSheet("background-color: purple;")
        self.layout.addWidget(final_widget)

    def create_table_header(self):
        header_widget = QWidget(self)
        header_widget.setAccessibleName("table-run-header")
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(12, 0, 2, 0)

        name = SafeLabel(project_run_table_header_name)
        name.setStyleSheet("font-weight: bold; border:none;")
        name.setFixedWidth(150)
        header_layout.addWidget(name)

        timestamp = SafeLabel(project_run_table_header_last_update)
        timestamp.setStyleSheet("font-weight: bold; border:none;")
        timestamp.setFixedWidth(120)
        header_layout.addWidget(timestamp)

        status = SafeLabel(project_run_table_header_status)
        status.setStyleSheet("font-weight: bold; border:none;")
        #status.setFixedWidth(80)
        header_layout.addWidget(status)

        header_widget.setLayout(header_layout)
        return header_widget

    def add_table_row(
        self, project_run: ProjectRunModel,
            delete_callback, download_callback, information_callback
    ):
        row_widget = QIdWidget(project_run.id)
        row_widget.setStyleSheet("""
            QIdWidget {
                background-color: white;
                border-bottom: 1px solid #aaa;
                padding: 2px;
            }
        """)
        row_layout = QHBoxLayout()
        row_layout.setContentsMargins(0, 0, 0, 0)

        # adding name
        name_label = SafeLabel(project_run.name)
        name_label.setToolTip(safe_tooltip(f"{project_run.name} ({project_run.id})"))
        name_label.setFixedWidth(150)
        name_label.setStyleSheet("font-weight: bold; border:none;")
        row_layout.addWidget(name_label)

        # adding timestamp
        timestamp_label = SafeLabel(self._get_last_modified_time(project_run))
        timestamp_label.setFixedWidth(100)
        timestamp_label.setStyleSheet("border:none;")
        row_layout.addWidget(timestamp_label)

        # adding status
        status_label = QidLabel(
            project_run.id, get_status_str(project_run.status)
        )
        status_label.setFixedWidth(80)
        status_label.setStyleSheet("border:none;")
        status_label.setAlignment(Qt.AlignCenter)
        row_layout.addWidget(status_label)

        # NOTE: For some reason, the lambda functions definitions call the
        # function with the first parameter as a true/false value.
        # So I am sending an index as first parameter and then the run object as second parameter
        # this way, we still can use the run object in the lambda function

        # adding action buttons
        # delete
        delete_button = create_icon_button(
            ":images/themes/default/mActionDeleteSelected.svg",
            project_run_table_delete_run,
            callback=lambda r=1, r_obj=project_run: delete_callback(r, r_obj),
            description="delete",
        )
        row_layout.addWidget(delete_button)

        # download
        download_button = create_icon_button(
            ":images/themes/default/downloading_svg.svg",
            project_run_table_download_results,
            callback=lambda r=1, r_obj=project_run: download_callback(r, r_obj),
            description="download",
        )
        row_layout.addWidget(download_button)

        # spinner
        spinner_button = create_icon_button(
            ":images/themes/default/mActionRefresh.svg",
            project_run_table_download_results,
            callback=None,
            description="spinner",
        )
        spinner_button.setToolTip(project_run_execution_ongoing)
        spinner_button.hide()
        row_layout.addWidget(spinner_button)

        info_button = create_icon_button(
            ":images/themes/default/mActionPropertiesWidget.svg",
            project_run_table_download_results,
            callback=lambda r=1, r_obj=project_run: information_callback(r, r_obj),
            description="info"
        )
        info_button.setToolTip(project_run_param_information)
        row_layout.addWidget(info_button)

        row_widget.setLayout(row_layout)

        return row_widget

    @staticmethod
    def _get_last_modified_time(project_run):
        if project_run.finished_at:
            return project_run.finished_at.strftime("%Y-%m-%d %H:%M")
        # else
        return project_run.created_at.strftime("%Y-%m-%d %H:%M")

    def _get_row_with_id(self, row_id):
        row_widgets = get_layout_children(self.table_layout, QIdWidget)
        if len(row_widgets) == 0:
            print("No run QIdWidgets found")
            return None
        print(f"found {len(row_widgets)} run qid-widgets")
        row_widget = next((wId for wId in row_widgets if wId.id == row_id), None)
        return row_widget

    def update_run_status(self, run: ProjectRunModel, status: TaskStatusEnum):
        run_widget = self._get_row_with_id(run.id)
        if run_widget is None:
            print(f"Could not find run with id: {run.id} to update to {status}")
            return

        old_status_text = get_status_str(run.status)
        print(f"old_status_text: {old_status_text}")
        if run_widget is not None:
            labels = run_widget.findChildren(QidLabel)
            for label in labels:
                print(f"label: '{label.text()}'")
            status_label = next((la for la in labels if la.id == run.id), None)
            if status_label is not None:
                status_label.setText(get_status_str(status))
            else:
                print(f"Could not find label with with status: {old_status_text}")
        else:
            print(f"Could not find label with with status: {old_status_text}")

    def show_download_spinner(self, row_id):
        self.show_hide_spinner(row_id, "spinner", "download")

    def hide_download_spinner(self, row_id):
        self.show_hide_spinner(row_id, "download", "spinner")

    def show_hide_spinner(self, row_id, show_element_name, hide_element_name):
        run_widget = self._get_row_with_id(row_id)
        button_widgets = run_widget.findChildren(QPushButton)
        for button in button_widgets:
            if button.accessibleName() == show_element_name:
                button.show()
            if button.accessibleName() == hide_element_name:
                button.hide()


def get_layout_children(layout, e_type):
    children = []
    for i in range(layout.count()):
        child = layout.itemAt(i).widget()
        if isinstance(child, e_type):
            children.append(child)
    return children
