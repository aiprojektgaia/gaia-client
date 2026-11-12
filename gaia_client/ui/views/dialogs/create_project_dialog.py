from PyQt5.QtWidgets import QDialog, QVBoxLayout, QDialogButtonBox
from PyQt5.QtGui import QIcon
from gaia_client.ui.views.components.validated_input import ValidatedInput
from gaia_client.storage.plugin_storage import PluginStore
from gaia_client.ui.i18n.se import (
    project_mpp,
    project_coordinate_system,
    project_layer_name,
    project_wms_url,
    project_description,
    project_name,
    project_wms_url_error,
    project_coordinate_system_error,
    project_layer_name_error,
    project_mpp_error,
    project_name_error,
    project_description_error,
    project_wms_url_hint,
    project_layer_name_hint,
    project_coordinate_system_hint,
    project_mpp_hint,
    project_create_dialog_title,
)


class CreateProjectDialog(QDialog):
    def __init__(self, on_save_callback, parent=None):
        super().__init__(parent)

        self.on_save_callback = on_save_callback
        self.setWindowTitle(project_create_dialog_title)
        self.setWindowIcon(QIcon(":images/themes/default/iconProcessingConsole.svg"))
        self.setFixedSize(400, 300)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        self.name_input = ValidatedInput(project_name, project_name_error)
        self.description_input = ValidatedInput(
            project_description, project_description_error
        )
        self.wms_url_input = ValidatedInput(
            project_wms_url,
            project_wms_url_error,
            project_wms_url_hint,
        )
        self.layer_name_input = ValidatedInput(
            project_layer_name, project_layer_name_error, project_layer_name_hint
        )
        self.epsg_input = ValidatedInput(
            project_coordinate_system,
            project_coordinate_system_error,
            project_coordinate_system_hint,
        )
        self.resolution_input = ValidatedInput(
            project_mpp, project_mpp_error, project_mpp_hint
        )

        # Add all inputs to layout
        layout.addWidget(self.name_input)
        layout.addWidget(self.description_input)
        layout.addWidget(self.wms_url_input)
        layout.addWidget(self.layer_name_input)
        layout.addWidget(self.epsg_input)
        layout.addWidget(self.resolution_input)

        # Set initial values
        self.wms_url_input.set_value(self.get_wms_url_from_settings())

        self.button_box = QDialogButtonBox()
        self.button_box.setStandardButtons(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel
        )
        self.button_box.clicked.connect(self.on_save_clicked)
        layout.addWidget(self.button_box)

        self.setLayout(layout)

    def get_wms_url_from_settings(self):
        store = PluginStore()
        geoserver_url = store.get("geoserver_url", "")
        return geoserver_url

    def on_save_clicked(self, button):
        role = self.button_box.standardButton(button)
        if role == QDialogButtonBox.StandardButton.Save:
            inputs, valid = self.validate_fields()
            if valid:
                self.on_save_callback(inputs)
                self.close()
        else:
            self.close()

    def validate_fields(self) -> (dict[str, any], bool):
        name_value, name_valid = self.name_input.get_input()
        description_value, description_valid = self.description_input.get_input()
        wms_value, wms_valid = self.wms_url_input.get_input()
        layer_value, layer_valid = self.layer_name_input.get_input()
        epsg_value, epsg_valid = self.epsg_input.get_input()
        resolution_value, resolution_valid = self.resolution_input.get_input()

        valid = all(
            [
                name_valid,
                description_valid,
                wms_valid,
                layer_valid,
                epsg_valid,
                resolution_valid,
            ]
        )

        if not valid:
            return None, False

        return (
            {
                "name": name_value,
                "description": description_value,
                "wms_url": wms_value,
                "layer_name": layer_value,
                "epsg": epsg_value,
                "resolution": resolution_value,
            },
            valid,
        )


def show_create_project_dialog(on_save_callback):
    dialog = CreateProjectDialog(on_save_callback)
    response = dialog.exec()
    return response
