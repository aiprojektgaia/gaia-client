from qgis.core import QgsSettings

from gaia_client.ui.utils.window_utils import Singleton


class PluginStore(metaclass=Singleton):
    def __init__(self):
        # if hasattr(self, "initialized") and self.initialized:
        #    print("PluginStore - using the singleton version")
        #    return

        self.store = QgsSettings()
        self.prefix = "gaia-plugin"
        # self.initialized = True
        print("PluginStore - initialized")

    def _get_inner_key(self, key):
        return f"{self.prefix}/{key}"

    def set(self, key: str, value):
        inner_key = self._get_inner_key(key)
        #print(f"storing setting {inner_key} - {value}")
        self.store.setValue(inner_key, value)

    def get(self, key: str, default_value=None):
        inner_key = self._get_inner_key(key)
        #print(f"getting setting {inner_key}")
        return self.store.value(inner_key, default_value)
