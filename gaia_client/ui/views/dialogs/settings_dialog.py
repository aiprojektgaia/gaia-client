from PyQt5.QtWidgets import (
    QLabel,
    QLineEdit,
    QMessageBox,
    QVBoxLayout,
    QDialog,
    QHBoxLayout,
    QPushButton,
)
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication

from gaia_client.api.requests.http_client import (
    HttpClient,
    url_origin,
    is_transport_safe_for_key,
)
from gaia_client.storage.plugin_storage import PluginStore
from gaia_client.ui.i18n.se import (
    settings_dialog_title,
    settings_dialog_backend_url,
    settings_dialog_local_geoserver_url,
    settings_dialog_api_key,
    project_settings_validate_empty_api_key_error,
    project_settings_validate_api_key_error,
    project_settings_reenter_api_key_error,
    project_settings_https_required_error,
    project_settings_validate_empty_url_error,
    project_settings_validate_invalid_url_error,
    project_settings_validate_ping_error,
    project_settings_validate_geoserver_ping_error,
    project_settings_validate_and_save_button,
    settings_dialog_cancel_button,
    settings_dialog_clear_wms_approvals,
)
from gaia_client.map.layer_handler import clear_approved_wms_origins
from gaia_client.ui.utils.safe_text import SafeLabel


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super(SettingsDialog, self).__init__(parent)

        self.backend_url_input: QLineEdit | None = None
        self.geoserver_url_input: QLineEdit | None = None
        self.api_key_input: QLineEdit | None = None
        self.button_box = None

        # self.setup_interface()
        self.initUI()
        self._load_settings()

    # def setup_interface(self):
    def initUI(self):
        layout = QVBoxLayout()
        self.setWindowTitle(settings_dialog_title)
        self.setFixedSize(400, 280)

        # title
        title_label = SafeLabel(settings_dialog_title)
        title_label.setAlignment(QtCore.Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 30px; font-weight: bold")
        title_label.setMaximumHeight(50)
        layout.addWidget(title_label)

        label_width = 120
        # Gaia backend url input
        pair_one_hl = QHBoxLayout()
        backend_url_label = SafeLabel(settings_dialog_backend_url + "*")
        backend_url_label.setFixedWidth(label_width)
        pair_one_hl.addWidget(backend_url_label)
        self.backend_url_input = QLineEdit()
        self.backend_url_input.setPlaceholderText("https://gaia.example.se:8443")
        pair_one_hl.addWidget(self.backend_url_input)
        layout.addLayout(pair_one_hl)

        # Geoserver url input
        pair_two_hl = QHBoxLayout()
        geoserver_url_label = SafeLabel(settings_dialog_local_geoserver_url)
        geoserver_url_label.setFixedWidth(label_width)
        pair_two_hl.addWidget(geoserver_url_label)
        self.geoserver_url_input = QLineEdit()
        self.geoserver_url_input.setPlaceholderText("http://127.0.0.1:9600")
        pair_two_hl.addWidget(self.geoserver_url_input)
        layout.addLayout(pair_two_hl)

        # API key input. Required - the backend rejects unauthenticated
        # requests with 401. Echoed as password characters since it is a
        # shared secret.
        pair_three_hl = QHBoxLayout()
        api_key_label = SafeLabel(settings_dialog_api_key + "*")
        api_key_label.setFixedWidth(label_width)
        pair_three_hl.addWidget(api_key_label)
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.Password)
        self.api_key_input.setPlaceholderText("GAIA_API_KEY")
        pair_three_hl.addWidget(self.api_key_input)
        layout.addLayout(pair_three_hl)

        # WMS servers the user approved when opening shared projects
        self.clear_wms_button = QPushButton(settings_dialog_clear_wms_approvals)
        self.clear_wms_button.clicked.connect(self._on_clear_wms_clicked)
        layout.addWidget(self.clear_wms_button)

        # Create button container
        button_container = QHBoxLayout()

        # Save button
        self.save_button = QPushButton(project_settings_validate_and_save_button)
        self.save_button.clicked.connect(self._on_save_clicked)
        button_container.addWidget(self.save_button)

        # Cancel button
        self.cancel_button = QPushButton(settings_dialog_cancel_button)
        self.cancel_button.clicked.connect(self._on_cancel_clicked)
        button_container.addWidget(self.cancel_button)

        layout.addLayout(button_container)

        self.setLayout(layout)

    def _on_save_clicked(self):
        QApplication.setOverrideCursor(Qt.WaitCursor)
        if self._validate_inputs():
            self._store_settings()
            self.close()
        QApplication.restoreOverrideCursor()

    def _on_clear_wms_clicked(self):
        clear_approved_wms_origins()
        self.clear_wms_button.setEnabled(False)

    def _on_cancel_clicked(self):
        QApplication.restoreOverrideCursor()
        self.close()

    def _store_settings(self):
        # no trailing slash: paths are appended as "/projects" etc.
        gaia_url = self.backend_url_input.text().strip().rstrip("/")
        geoserver_url = self.geoserver_url_input.text().strip().rstrip("/")

        store = PluginStore()
        store.set("gaia_backend_url", gaia_url)
        store.set("geoserver_url", geoserver_url)
        store.set("gaia_api_key", self.api_key_input.text().strip())

    def _load_settings(self):
        store = PluginStore()
        gaia_url = store.get("gaia_backend_url", "")
        geoserver_url = store.get("geoserver_url", "")

        self.backend_url_input.setText(gaia_url)
        self.geoserver_url_input.setText(geoserver_url)
        self.api_key_input.setText(store.get("gaia_api_key", ""))

    def _validate_inputs(self):
        gaia_url = self.backend_url_input.text().strip().rstrip("/")
        geoserver_url = self.geoserver_url_input.text().strip().rstrip("/")
        api_key = self.api_key_input.text().strip()

        # Never carry the stored key over to a different server: the user has
        # to type it again for the new origin.
        store = PluginStore()
        stored_url = store.get("gaia_backend_url", "")
        stored_key = store.get("gaia_api_key", "")
        if (
            stored_url
            and stored_key
            and url_origin(gaia_url) != url_origin(stored_url)
            and api_key == stored_key
        ):
            show_warning_messagebox(project_settings_reenter_api_key_error)
            self.api_key_input.clear()
            return False

        if not validate_backend_url(gaia_url):
            return False

        if not validate_api_key(gaia_url, api_key):
            return False

        if len(geoserver_url) > 0 and not validate_geoserver_url(geoserver_url):
            return False

        return True


def validate_backend_url(url: str):
    if len(url) <= 0:
        show_warning_messagebox(project_settings_validate_empty_url_error)
        return False
    if not url.startswith(("http://", "https://")):
        show_warning_messagebox(project_settings_validate_invalid_url_error)
        return False
    if not is_transport_safe_for_key(url):
        show_warning_messagebox(project_settings_https_required_error)
        return False

    http_client = HttpClient(send_api_key=False)
    http_client.get(f"{url}/status/ping")
    if not http_client.success():
        show_warning_messagebox(project_settings_validate_ping_error)
        return False

    return True


def validate_api_key(url: str, api_key: str):
    """Check the key against a protected endpoint.

    validate_backend_url() only reaches /status/ping, which is deliberately
    public so the URL can be tested before a key exists. This calls a protected
    route so a wrong key is reported here rather than as a mystery failure
    later on.
    """
    if len(api_key) <= 0:
        show_warning_messagebox(project_settings_validate_empty_api_key_error)
        return False

    if not is_transport_safe_for_key(url):
        show_warning_messagebox(project_settings_https_required_error)
        return False

    http_client = HttpClient(api_key=api_key)
    http_client.get(f"{url}/projects")

    if http_client.status_code() == 401:
        show_warning_messagebox(project_settings_validate_api_key_error)
        return False

    if not http_client.success():
        show_warning_messagebox(project_settings_validate_ping_error)
        return False

    return True


def validate_geoserver_url(url: str):
    if len(url) <= 0:
        show_warning_messagebox(project_settings_validate_empty_url_error)
        return False
    if not url.startswith("http"):
        show_warning_messagebox(project_settings_validate_invalid_url_error)
        return False

    if not geoserver_wms_reachable(url):
        show_warning_messagebox(project_settings_validate_geoserver_ping_error)
        return False

    return True


def geoserver_wms_reachable(url: str) -> bool:
    """Ask the WMS endpoint for its capabilities - the service the plugin
    actually uses - rather than the admin UI, which always redirects.

    Accepts the server root ("http://host:9600"), the GeoServer context
    ("https://host/geoserver") or the WMS endpoint itself (".../wms")."""
    base = url.rstrip("/")
    if base.lower().endswith(("/wms", "/ows")):
        candidates = [base]
    else:
        candidates = [f"{base}/wms", f"{base}/geoserver/wms"]
    for candidate in candidates:
        http_client = HttpClient(send_api_key=False)
        http_client.get(f"{candidate}?SERVICE=WMS&REQUEST=GetCapabilities")
        if http_client.success():
            return True
    return False


def show_warning_messagebox(message: str):
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Icon.Warning)
    msg.setText(message)
    msg.setWindowTitle("Warning")
    msg.setStandardButtons(QMessageBox.StandardButton.Ok)
    msg.exec()
