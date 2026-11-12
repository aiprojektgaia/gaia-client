from PyQt5.QtWidgets import QGroupBox, QVBoxLayout, QLabel, QSizePolicy

from gaia_client.api.models.GaiaModel import GaiaModel
from gaia_client.ui.i18n.se import project_create_run_model_error
from gaia_client.ui.widgets.checkbox_with_id import QidCheckBox
from gaia_client.ui.utils.safe_text import SafeLabel, safe_tooltip


class ModelTypeSelectorQGroupBox(QGroupBox):
    def __init__(self, title: str, items: list[GaiaModel], parent=None, *__args):
        #super(ModelTypeSelectorQGroupBox).__init__(parent)
        super().__init__(*__args)
        self.setTitle(title)
        self.items = items
        self.model_error_label = None

        self.set_gui()

    def set_gui(self):
        self.setFlat(True)

        layout = QVBoxLayout()

        for model in self.items:
            widget = QidCheckBox(model.id, model.name)
            widget.setAccessibleName(str(model.id))
            widget.setToolTip(safe_tooltip(model.description))
            layout.addWidget(widget)

        # Create error label with minimal height and no margins
        self.model_error_label = SafeLabel(project_create_run_model_error)
        self.model_error_label.setStyleSheet("""
            color: red;
        """)
        self.model_error_label.setContentsMargins(0, 0, 0, 0)
        self.model_error_label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
        self.model_error_label.hide()
        layout.addWidget(self.model_error_label)

        layout.addStretch(1)
        self.setLayout(layout)

    def show_error(self):
        self.model_error_label.show()

    def hide_error(self):
        self.model_error_label.hide()

    def get_selected_models(self):
        selected_models = []
        #for i in range(self.layout().count() - 1):
        #    widget = self.layout().itemAt(i).widget()
        #    if isinstance(widget, QidCheckBox) and widget.isChecked():
        #        selected_models.append(widget.id)

        for checkbox in self.findChildren(QidCheckBox):
            if checkbox.isChecked():
                selected_models.append(checkbox.id)

        return selected_models

    def get_input(self) -> (list[str], bool):
        selected_models = self.get_selected_models()
        if len(selected_models) == 0:
            self.show_error()
            return selected_models, False
        else:
            self.hide_error()
            return selected_models, True