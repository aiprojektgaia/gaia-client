from PyQt5.QtCore import QJsonDocument

from gaia_client.api.helpers.casting import cast_to_list_of_type, cast_to_type
from gaia_client.api.models.CreateProjectRun import CreateProjectRun
from gaia_client.api.models.ProjectRun import ProjectRun as ProjectRunModel
from gaia_client.api.models.ProjectRunStatus import ProjectRunStatus
from gaia_client.api.requests.base_request import BaseRequest
from gaia_client.api.requests.http_client import HttpClient, MAX_DOWNLOAD_BYTES, DOWNLOAD_TOTAL_TIMEOUT_MS


class ProjectRunApi(BaseRequest):
    def get_all_runs(self, project_id: int)-> list[ProjectRunModel]:
        url = f"{self.base_url}/runs?project_id={project_id}"
        print(f"Fetching project runs from {url}")
        request = self.http_client.get(url)
        if self.http_client.success():
            result_str = self.http_client.get_response_as_string()
            try:
                return cast_to_list_of_type(result_str, ProjectRunModel)
            except (ValueError, TypeError, KeyError) as e:
                print(f"Unexpected response while fetching project runs: {e}")
                return []
        else:
            print("Error occurred while fetching project runs")
            return []

    def get_run_results_as_zip(self, run_id: int, file_path: str, on_started=None) -> bool:
        """Stream the result archive into file_path (which must not exist)."""
        url = f"{self.base_url}/runs/{int(run_id)}/download"
        print(f"Fetching project run results from {url}")
        # result archives are large, but still bounded
        self.http_client = HttpClient(
            max_response_bytes=MAX_DOWNLOAD_BYTES,
            total_timeout_ms=DOWNLOAD_TOTAL_TIMEOUT_MS,
        )
        if on_started is not None:
            on_started(self.http_client)
        self.http_client.get(url, output_path=file_path)
        if not self.http_client.success():
            print("Error occurred while fetching project run result")
        return self.http_client.success()

    def delete_run(self, run_id:int) -> bool:
        url = f"{self.base_url}/runs/{run_id}"
        print(f"Fetching project runs from {url}")
        request = self.http_client.delete(url)
        return self.http_client.success()

    def create_run(self, create_project_run: CreateProjectRun) -> ProjectRunModel | None:
        url = f"{self.base_url}/runs"
        print(f"creating project runs from {url}")
        #json_doc = QJsonDocument.fromVariant(create_project_run)
        #data = json_doc.toJson()
        print(f"print dict: {create_project_run.__dict__}")
        request = self.http_client.post(url, create_project_run.__dict__)
        if self.http_client.success():
            return self.http_client.get_response()
        else:
            self.last_error = self.http_client.error_message()
            print(f"Error occurred while creating project run: {self.last_error}")
            return None

    def get_run_status(self, run_id:int) -> ProjectRunStatus | None:
        url = f"{self.base_url}/runs/{run_id}/status"
        self.http_client.get(url)

        if self.http_client.success():
            result_str = self.http_client.get_response_as_string()
            try:
                return cast_to_type(result_str, ProjectRunStatus)
            except (ValueError, TypeError, KeyError) as e:
                print(f"Unexpected response while fetching run status: {e}")
                return None
        else:
            print("Error occurred while fetching project run result")
            return None

