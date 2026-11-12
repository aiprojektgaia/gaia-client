import time
import traceback
from typing import Optional

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QLabel,
    QFileDialog,
    QLineEdit,
    QVBoxLayout,
    QMessageBox,
    QWidget,
)

from gaia_client.api.models import ProjectRun as ProjectRunModel, ProjectRunStatus
from gaia_client.api.models.Project import Project as ProjectModel
from gaia_client.api.requests.project_run import ProjectRunApi
from gaia_client.map.layer_handler import add_layer_to_qgis
from gaia_client.ui.i18n.se import (
    project_save_result_dialog,
    project_description,
    project_wms_url,
    project_coordinate_system,
    project_mpp,
    project_layer_name,
    product_delete_run_title,
    product_delete_run_description,
    project_create_new_run,
    project_run_status_pending,
    project_run_status_title,
    project_run_status_calculating,
)
from gaia_client.ui.utils.task_status_helper import get_status_str
from gaia_client.ui.utils.task_status_helper import is_task_status_finished
from gaia_client.ui.utils.timer_manager import TimerManager
from gaia_client.ui.utils.view import goto_view
from gaia_client.ui.views.base_view import BaseView
from gaia_client.ui.views.dialogs.project_run_info_dialog import (
    ProjectRunInformationDialog,
)
from gaia_client.ui.widgets.button import make_blue_button
from gaia_client.ui.widgets.header import HeaderWidget
from gaia_client.ui.widgets.id_widget import remove_widget_by_id
from gaia_client.ui.widgets.notification_area import NotificationArea
from gaia_client.ui.widgets.project_run_table import ProjectRunTable
from gaia_client.use_cases.get_and_show_run_results import GetAndShowRunResults
from gaia_client.ui.utils.safe_text import SafeLabel, ask_yes_no, show_plain_warning


MAX_RUNS_POLLED_PER_TICK = 25
MAX_POLLING_SECONDS = 12 * 60 * 60

class ViewProject(BaseView):
    _polling_started = 0.0
    def __init__(self, iface, **kwargs):
        super().__init__(iface)

        self.notification_area_widget = None

        self.timer_manager = TimerManager()
        self.timer_manager.timer_started_signal.connect(
            lambda project_id: self.show_notification_area(project_id)
        )
        self.timer_manager.timer_stopped_signal.connect(
            lambda project_id: self.hide_notification_area(project_id)
        )

        self.layout.setSpacing(5)  # Reduced spacing between widgets
        self.project: ProjectModel | None = None
        self.project_runs: list[ProjectRunModel] = []
        self.save_as_dialog = None
        self.run_table = None

        # getting the project information
        project = kwargs.get(
            "project", ProjectModel("Test project", "This is test", 1, True)
        )  # Extract project from kwargs
        self.project = project

        self.render_view()
        print("ViewProject - [setup done]")

    def clean_up(self):
        super().clean_up()
        self.timer_manager.clean_up()

    def render_view(self):
        self.render_header()
        self.render_body()
        #self.render_footer()

    def render_header(self):
        header_widget = HeaderWidget(
            self.project.name, "project_start", title_hint=self.project.description
        )
        self.layout.addWidget(header_widget)

    def render_body(self):
        body_widget = QWidget(self.widget)
        body_layout = QVBoxLayout(body_widget)
        body_layout.setContentsMargins(0, 0, 0, 0)

        project = self.project
        self.add_information(body_layout, project_description, project.description)
        self.add_information(body_layout, project_wms_url, project.get_wms_url())
        self.add_information(body_layout, project_layer_name, project.get_layer_name())
        self.add_information(
            body_layout, project_coordinate_system, project.get_coordinate_system()
        )
        self.add_information(
            body_layout, project_mpp, f"{project.get_meters_per_pixel()} m/px"
        )

        self.add_new_run_button(body_layout)
        notification_area = self.add_notification_area(body_widget)
        body_layout.addWidget(notification_area)

        table_widget = self.get_and_show_project_runs(body_widget)
        body_layout.addWidget(table_widget)

        # add wms layer to the layers view
        add_layer_to_qgis(
            self.iface,
            project.get_wms_url(),
            project.get_layer_name(),
            project.get_coordinate_system(),
        )

        # Add body to the layout
        body_widget.setLayout(body_layout)
        self.layout.addWidget(body_widget)

        #body_widget.setStyleSheet("background-color: pink;")

    def render_footer(self):
        footer_widget = QWidget(self.widget)
        footer_layout = QVBoxLayout()
        footer_layout.setContentsMargins(0, 0, 0, 0)
        footer_layout.setAlignment(Qt.AlignBottom)

        footer = SafeLabel("GAIA")
        footer_layout.addWidget(footer)

        footer_widget.setLayout(footer_layout)
        self.layout.addWidget(footer_widget)

        footer_widget.setStyleSheet("background-color: orange;")


    def hide_notification_area(self, project_id: int):
        self.notification_area_widget.hide()
        self.timer_manager.progress_message_signal.disconnect()

    def show_notification_area(self, project_id: int):
        self.notification_area_widget.show()
        self.timer_manager.progress_message_signal.connect(
            lambda data: self.update_notification_area(data)
        )

    def update_notification_area(self, status: dict):
        if status is None or status == {}:
            return

        calculating = status.get("calculating", False)
        total_finished_tasks = status.get("total_finished_step", status.get("finished_tasks", 0))
        total_tasks = status.get("total_steps", status.get("total_tasks", 0))

        if calculating:
            message = f"{project_run_status_calculating} ..."
        else:
            message = f"{get_status_str(status['status'])} ({total_finished_tasks}/{total_tasks})"

        self.notification_area_widget.update_notification_message(message)

        if calculating:
            total_finished_tasks = 0
            total_tasks = 1

        self.notification_area_widget.update_progress(
            total_finished_tasks, total_tasks)

    def add_notification_area(self, parent_widget):
        self.notification_area_widget = NotificationArea(
            project_run_status_title,
            project_run_status_pending + "...",
            parent=parent_widget,
        )
        return self.notification_area_widget

    @staticmethod
    def add_information(info_layout, label_text, value):
        title_label = SafeLabel(label_text)
        info_layout.addWidget(title_label)

        input_box = QLineEdit()
        input_box.setText(value)
        input_box.setReadOnly(True)
        input_box.setStyleSheet("background-color: #F0F0F0;")
        # input_box.setAlignment(Qt.AlignRight)
        info_layout.addWidget(input_box)

    def add_new_run_button(self, layout):
        new_run_button = make_blue_button(project_create_new_run)
        new_run_button.clicked.connect(
            lambda: goto_view("project_create_run", project=self.project)
        )
        layout.addWidget(new_run_button)

    def download_and_show_run_info(self, index: int, run: ProjectRunModel):
        self.save_as_dialog = QFileDialog(self.widget)
        self.save_as_dialog.setWindowTitle(project_save_result_dialog)
        # to select a directory
        self.save_as_dialog.setFileMode(QFileDialog.FileMode.Directory)
        self.save_as_dialog.setViewMode(QFileDialog.ViewMode.List)

        if run is None:
            print(f"could not find run with id: {index}")
            return

        if self.save_as_dialog.exec():
            selected_file = self.save_as_dialog.selectedFiles()[0]
            print("Selected File for Saving:", selected_file)
            # self._save_and_attach_file(selected_file, project_run)
            self.run_table.show_download_spinner(run.id)
            try:
                save_result_use_case = GetAndShowRunResults(self.iface, run, selected_file)
                if not save_result_use_case.run():
                    show_plain_warning(self.widget, "Could not download the run results.")
            except Exception as e:
                # partial files are already cleaned up by the use case
                print(traceback.format_exc())
                show_plain_warning(self.widget, f"Could not open the run results.\n\n{e}")
            finally:
                self.run_table.hide_download_spinner(run.id)

    def get_and_show_project_runs(self, parent_widget):
        self.project_runs = self.fetch_project_runs()
        # order them by id descending
        self.project_runs.sort(key=lambda x: x.id, reverse=True)

        #return scroll
        self.run_table = ProjectRunTable(
                            self.project_runs,
                            self.delete_run,
                            self.download_and_show_run_info,
                            self.show_run_param_information,
                            parent=parent_widget,
        )

        # evaluate runs
        print("Evaluating runs")
        self.check_on_running_runs(self.project_runs)

        return self.run_table

    def show_run_param_information(self, index:int, run: ProjectRunModel):
        run_info_dialog = ProjectRunInformationDialog(run, self.widget)
        run_info_dialog.exec()

    def fetch_project_runs(self):
        api = ProjectRunApi()
        all_runs = api.get_all_runs(self.project.id)
        return all_runs

    def delete_run(self, index: int, run: ProjectRunModel, **kwargs):
        # print kwargs
        for key, value in kwargs.items():
            print(f"Delete_run: k/v -> {key} = {value}")

        confirmed = ask_yes_no(
            self.run_table,
            product_delete_run_title,
            f"{product_delete_run_description} \n  * {run.name}?",
        )
        if not confirmed:
            return
        else:
            api = ProjectRunApi()
            success = api.delete_run(run.id)
            if success:
                self.project_runs.remove(run)
                remove_widget_by_id(self.run_table.table_layout, run.id)

            # remove run from list
            widget_to_remove = None
            for i in range(self.run_table.table_layout.count()):
                widget = self.run_table.table_layout.itemAt(i).widget()
                if widget.accessibleName() == f"{run.id}":
                    widget_to_remove = widget
                    break

            if widget_to_remove is not None:
                self.run_table.table_layout.removeWidget(widget_to_remove)
                widget_to_remove.deleteLater()

    def check_on_running_runs(self, project_runs):
        has_running_runs = False
        for run in project_runs:
            if not is_task_status_finished(run.status):
                self.run_table.show_download_spinner(run.id)
                has_running_runs = True

        if not has_running_runs:
            return

        print("Timer will be created")
        self._polling_started = time.monotonic()
        self.timer_manager.start_timer(self.project.id, self.update_run_status)

    def update_run_status(self):
        try:
            return self._update_run_status()
        except Exception as e:
            print(traceback.format_exc())
            print(f"Error in update_run_status: {e}")
            # stop the timer
            self.timer_manager.stop_timer(self.project.id)
            raise e

    def _update_run_status(self):
        print("Updating run status")
        has_running_runs = False

        # Bound the work per tick (one synchronous request per run) and the
        # lifetime of the poller, however many runs the backend reports.
        if time.monotonic() - self._polling_started > MAX_POLLING_SECONDS:
            print("polling lifetime exceeded, stopping the timer")
            self.timer_manager.stop_timer(self.project.id)
            return None
        runs_to_check = [
            run for run in self.project_runs if not is_task_status_finished(run.status)
        ][:MAX_RUNS_POLLED_PER_TICK]
        project_run_status: ProjectRunStatus = None
        api = ProjectRunApi()
        for run in runs_to_check:
            run_running = True
            # get the status from the api
            project_run_status = api.get_run_status(run.id)
            if project_run_status is None:
                print(f"Could not get status for run {run.id}")
                continue
            print(f"Run {run.id} status: {str(project_run_status)}")
            if project_run_status.status != run.status:
                print(
                    f"Run {run.id} status changed from {run.status} to {project_run_status.status}"
                )
                run.status = project_run_status.status
                # update the status in the table
                self.run_table.update_run_status(run, run.status)

                if is_task_status_finished(project_run_status.status):
                    run_running = False
                    self.run_table.hide_download_spinner(run.id)

            has_running_runs = has_running_runs or run_running

        # if there are no more running things, then stop the timer
        if not has_running_runs:
            print("no more runs to check on, killing the timer")
            self.timer_manager.stop_timer(self.project.id)

        print(
            "finished running update_run_status, has running runs? ", has_running_runs
        )
        if project_run_status:
            return project_run_status.__dict__
        return None
