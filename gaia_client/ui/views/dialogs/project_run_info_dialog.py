from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QDialogButtonBox

from gaia_client.api.models import ProjectRun as ProjectRunModel
from gaia_client.api.requests.models import ModelsApi
from gaia_client.ui.i18n.se import project_run_info_title, project_run_info_status, \
    project_run_info_selected_area, project_run_info_confidence_level, project_run_info_overlap, \
    project_run_info_chosen_models, project_run_info_name
from gaia_client.ui.utils.task_status_helper import get_status_str
from gaia_client.ui.views import h1_size
from gaia_client.ui.utils.safe_text import SafeLabel


class ProjectRunInformationDialog(QDialog):

    def __init__(self, run: ProjectRunModel, parent = None):
        super(ProjectRunInformationDialog, self).__init__(parent)

        self.project_run:ProjectRunModel = run
        self.setWindowTitle(project_run_info_title)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.setFixedSize(400, 400)

        # title
        header_widget = self.get_header(project_run_info_title)
        layout.addWidget(header_widget)

        # body
        self.get_body(layout)

        # footer
        footer = self.get_footer()
        layout.addWidget(footer)

    @staticmethod
    def get_header(title):
        header_widget = SafeLabel(title)
        header_widget.setStyleSheet(f"font-size: {h1_size}; font-weight: bold;")
        return header_widget

    def get_footer(self):
        button_box = QDialogButtonBox()
        button_box.setStandardButtons(QDialogButtonBox.StandardButton.Close)
        button_box.clicked.connect(self.button_box_clicked)
        return button_box

    def button_box_clicked(self, button):
        self.close()

    def get_body(self, body_layout):
        # Add information
        self.add_information(body_layout, project_run_info_name, self.project_run.name)
        self.add_information(body_layout, project_run_info_status, get_status_str(self.project_run.status))
        self.add_information(body_layout, project_run_info_selected_area, self.project_run.attributes["bbox"])
        self.add_information(body_layout, project_run_info_confidence_level, self.project_run.attributes["confidence_level"])
        self.add_information(body_layout, project_run_info_overlap, self.project_run.attributes["overlap"])

        # segmented models
        models = ModelsApi().get_segmentation_models()
        self.add_segmented_models(body_layout, project_run_info_chosen_models, models)

    @staticmethod
    def add_information(info_layout, label_text, value):
        title_label = SafeLabel(label_text)
        info_layout.addWidget(title_label)

        input_box = QLineEdit()
        input_box.setText(str(value))
        input_box.setReadOnly(True)
        #input_box.setDisabled(True)
        input_box.setStyleSheet("background-color: #F0F0F0;")
        info_layout.addWidget(input_box)

    def add_segmented_models(self, info_layout, label_text, models):
        title_label = SafeLabel(label_text)
        info_layout.addWidget(title_label)

        models_str = ""
        selected_model_ids = self.project_run.attributes["interface_to_use"]
        for model in models:
            if model.id in selected_model_ids:
                models_str += f"* {model.name} \n"
        models_label = SafeLabel(models_str)
        info_layout.addWidget(models_label)
