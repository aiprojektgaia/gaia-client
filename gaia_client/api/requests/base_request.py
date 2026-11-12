from gaia_client.api.requests.http_client import HttpClient

from gaia_client.storage.plugin_storage import PluginStore


def _get_base_url():
    plugin_store = PluginStore()

    #base_url ="http://127.0.0.1:8000"
    return (plugin_store.get("gaia_backend_url") or "").strip().rstrip("/")


class BaseRequest:
    def __init__(self):
        self.base_url = _get_base_url()
        self.http_client = HttpClient()
