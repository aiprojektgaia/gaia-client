from gaia_client.api.helpers.casting import cast_to_list_of_type, cast_to_type
from gaia_client.api.requests.base_request import BaseRequest
from gaia_client.api.models.Project import Project

from gaia_client.storage.plugin_storage import PluginStore


def _get_base_url():
    plugin_store = PluginStore()

    # base_url ="http://127.0.0.1:8000"
    return (plugin_store.get("gaia_backend_url") or "").strip().rstrip("/")


class ProjectApi(BaseRequest):
    def get_projects(self) -> list[Project]:
        url = f"{self.base_url}/projects"
        print(f"about to make a request: {url}")
        self.http_client.get(url)
        if self.http_client.success():
            result_str = self.http_client.get_response_as_string()
            try:
                return cast_to_list_of_type(result_str, Project)
            except (ValueError, TypeError) as e:
                print(f"Unexpected response while fetching projects: {e}")
                return []
        else:
            print("Error occurred while fetching projects")
            return []

    def create_project(
        self,
        name: str,
        description: str,
        epsg: str,
        mpp: int,
        wms_url: str,
        layer_name: str,
    ) -> Project | None:
        url = f"{self.base_url}/projects"
        self.http_client.put(
            url,
            {
                "name": name,
                "description": description,
                "created_by": "gaia_client",
                "attributes": {
                    "epsg": epsg,
                    "mpp": float(mpp),
                    "wms_server_url": wms_url,
                    "layer_name": layer_name,
                },
            },
        )
        if self.http_client.success():
            try:
                return cast_to_type(self.http_client.get_response_as_string(), Project)
            except (ValueError, TypeError) as e:
                # json.JSONDecodeError is a ValueError
                print(f"Unexpected response while creating project: {e}")
                return None
        else:
            print("Error occurred while creating project")
            return None

    def delete_project(self, project_id: int) -> bool:
        url = f"{self.base_url}/projects/{project_id}"
        self.http_client.delete(url)
        return self.http_client.success()
