from PyQt5.QtCore import Qt, QRegExp
from PyQt5.QtGui import QIcon, QIntValidator, QRegExpValidator
from PyQt5.QtWidgets import (
    QPushButton,
    QLabel,
    QLineEdit,
    QVBoxLayout,
    QMessageBox,
    QWidget,
    QGroupBox,
)

from gaia_client.api.models.Project import Project as ProjectModel
from gaia_client.api.requests.models import ModelsApi
from gaia_client.ui.i18n.se import (
    project_create_run_back_button,
    project_create_run_execute_button,
    project_create_run_body_header,
    project_create_run_map_source,
    project_create_run_name_label,
    project_create_run_name_hint,
    project_create_run_confidence_level_label,
    project_create_run_confidence_level_hint,
    project_create_run_choose_model_label,
    project_create_run_name_error,
    project_create_run_confidence_level_error,
    project_create_run_select_input_label,
    project_create_run_overlap_label,
    project_create_run_overlap_error,
    project_create_run_overlap_hint,
)
from gaia_client.ui.utils.view import goto_view
from gaia_client.ui.views import h1_size, title_height, h2_size
from gaia_client.ui.views.base_view import BaseView
from gaia_client.ui.views.components.area_selector import AreaSelector
from gaia_client.ui.views.components.validated_input import ValidatedInput
from gaia_client.ui.widgets.header import HeaderWidget
from gaia_client.ui.widgets.model_type_selector import ModelTypeSelectorQGroupBox
from gaia_client.use_cases.create_project_run import create_project_run
from gaia_client.ui.widgets.button import make_blue_button
from gaia_client.ui.utils.safe_text import SafeLabel, clip, safe_tooltip


class CreateProjectRunView(BaseView):
    def __init__(self, iface, **kwargs):
        super().__init__(iface)

        self.project: ProjectModel = kwargs.get(
            "project", ProjectModel("Test project", "This is test", 1, True)
        )  # Extract project from kwargs

        self.area_selector = None
        self.render_view()
        self.layout.setAlignment(Qt.AlignTop)
        print("View CreateProjectRun - [setup done]")

    def clean_up(self):
        super().clean_up()

        if self.area_selector:
            self.area_selector.disable_select_box()

    def render_view(self):
        self.render_header()
        self.render_body()
        self.render_footer()

    def render_header(self):
        header_widget = HeaderWidget(
            self.project.name,
            self._go_back_clicked,
            project_create_run_back_button,
            title_hint=self.project.description,
        )
        self.layout.addWidget(header_widget)

    def render_footer(self):
        footer_widget = QWidget(self.widget)
        footer_layout = QVBoxLayout()
        footer_layout.setContentsMargins(0, 0, 0, 0)
        footer_layout.setAlignment(Qt.AlignBottom)

        run_button = make_blue_button(project_create_run_execute_button)
        run_button.clicked.connect(self._create_run_clicked)

        footer_layout.addWidget(run_button)
        footer_widget.setLayout(footer_layout)
        self.layout.addWidget(footer_widget)

    def render_body(self):
        body_widget = QWidget(self.widget)
        body_layout = QVBoxLayout()
        body_layout.setContentsMargins(0, 0, 0, 0)

        header = self.get_body_header(project_create_run_body_header)
        body_layout.addWidget(header)

        self.add_information(
            body_layout, project_create_run_map_source, self.project.get_layer_name()
        )

        self.run_name_input = ValidatedInput(
            project_create_run_name_label,
            project_create_run_name_error,
            project_create_run_name_hint,
            validator=QRegExpValidator(QRegExp(r"^.{3,}$")),
        )
        # project_create_run_name_hint, validator=QRegExpValidator(QRegExp(r"^(?! ).{3,}(?<! )$")))
        body_layout.addWidget(self.run_name_input)

        area_selector_box = self.create_select_area_group(
            project_create_run_select_input_label, is_flat=True
        )
        body_layout.addWidget(area_selector_box)

        self.confidence_input = ValidatedInput(
            project_create_run_confidence_level_label,
            project_create_run_confidence_level_error,
            project_create_run_confidence_level_hint,
            validator=QIntValidator(0, 100),
        )
        body_layout.addWidget(self.confidence_input)

        self.overlap_input = ValidatedInput(
            project_create_run_overlap_label,
            project_create_run_overlap_error,
            project_create_run_overlap_hint,
            validator=QIntValidator(0, 50),
        )
        body_layout.addWidget(self.overlap_input)

        models = ModelsApi().get_segmentation_models()
        self.model_selector = ModelTypeSelectorQGroupBox(
            project_create_run_choose_model_label, models
        )
        body_layout.addWidget(self.model_selector)

        # Add body to the layout
        body_widget.setLayout(body_layout)
        self.layout.addWidget(body_widget)

        # stretches the layout all the way to the bottom (because it is a vertical layout)
        body_layout.addStretch(1)

    @staticmethod
    def get_body_header(header_text: str):
        header_label = SafeLabel(header_text)
        header_label.setStyleSheet(f"font-size: {h2_size}px; font-weight: bold;")
        header_label.setAlignment(Qt.AlignLeft)
        header_label.setFixedHeight(title_height)

        return header_label

    @staticmethod
    def add_information(info_layout, label_text, value):
        title_label = SafeLabel(label_text)
        info_layout.addWidget(title_label)

        input_box = QLineEdit()
        input_box.setText(value)
        input_box.setReadOnly(True)
        info_layout.addWidget(input_box)

    @staticmethod
    def add_input_box(info_layout, label_text: str, label_hint: str = None):
        title_label = SafeLabel(label_text)
        info_layout.addWidget(title_label)

        input_box = QLineEdit()
        input_box.setPlaceholderText(label_hint)
        info_layout.addWidget(input_box)

    @staticmethod
    def get_title(title_text, description):
        title_label = SafeLabel(title_text)
        title_label.setStyleSheet(f"font-size: {h1_size}px; font-weight: bold;")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFixedHeight(title_height)
        title_label.setToolTip(safe_tooltip(description))

        return title_label

    def get_back_button(self, text: str):
        back_button = QPushButton(text)
        back_button.clicked.connect(self._go_back_clicked)
        button_icon = QIcon(":images/themes/default/mActionArrowLeft.svg")
        back_button.setIcon(QIcon(button_icon))
        back_button.setContentsMargins(0, 0, 0, 0)

        return back_button

    def _go_back_clicked(self):
        goto_view("project", project=self.project)

    def _create_run_clicked(self):
        # validate the inputs
        name, name_valid = self.run_name_input.get_input()
        bbox, bbox_valid = self.area_selector.get_input()
        confidence, conf_valid = self.confidence_input.get_input()
        overlap, overlap_valid = self.overlap_input.get_input()
        selected_models, models_valid = self.model_selector.get_input()

        if name_valid and bbox_valid and conf_valid and overlap_valid and models_valid:
            # create the run
            # self.create_run(name, bbox, confidence, selected_models_as_str)
            self.area_selector.disable_select_box()
            message = (
                f"Run created with name: {name}, bbox: {bbox}, "
                f"confidence: {confidence}, models: {selected_models}, "
                f"overlap: {overlap}"
            )
            print(message)

            # TODO: create the run call
            created, error = create_project_run(
                self.project, name, bbox, int(confidence), int(overlap), selected_models
            )
            if created:
                goto_view("project", project=self.project)
            else:
                # the server's reason is backend text: show it as plain text
                box = QMessageBox(self.widget)
                box.setIcon(QMessageBox.Warning)
                box.setWindowTitle("Error")
                box.setTextFormat(Qt.PlainText)
                box.setText(clip(f"Failed to create run.\n\n{error}" if error else "Failed to create run"))
                box.exec()

    def create_select_area_group(self, title: str, is_flat=False):
        groupbox = QGroupBox(title)
        groupbox.setFlat(is_flat)
        vbox = QVBoxLayout()

        self.area_selector = AreaSelector(self.iface, vbox, self.project)

        vbox.addStretch(1)
        groupbox.setLayout(vbox)
        return groupbox
