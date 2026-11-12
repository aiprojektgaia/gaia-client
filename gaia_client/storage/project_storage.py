from qgis.core import QgsProject

from gaia_client.ui.utils.window_utils import Singleton


class ProjectStore(metaclass=Singleton):
    def __init__(self):
        if hasattr(self, "initialized") and self.initialized:
            return

        self.project_instance = QgsProject.instance()
        self.prefix = "gaia-plugin"

    def _get_inner_key(self, key):
        return f"{self.prefix}/{key}"

    def set(self, key: str, value):
        self.project_instance.writeEntry(self.prefix, key, value)

    def get_str(self, key: str, default_value: str = ""):
        self.project_instance.readEntry(self.prefix, key, default_value)

    def get_int(self, key: str, default_value: int = 0):
        self.project_instance.readNumEntry(self.prefix, key, default_value)

    def get_double(self, key: str, default_value: float = 0.0):
        self.project_instance.readDoubleEntry(self.prefix, key, default_value)

    def get_boolean(self, key: str, default_value: bool = False):
        self.project_instance.readBoolEntry(self.prefix, key, default_value)
