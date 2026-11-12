from gaia_client.api.helpers.casting import cast_to_list_of_type
from gaia_client.api.models.GaiaModel import GaiaModel
from gaia_client.api.requests.base_request import BaseRequest


class ModelsApi(BaseRequest):
    """
    ModelsApi class to handle requests to the models API.
    """
    def get_segmentation_models(self) -> list:
        """
        Get all segmentation models.
        """
        url = f"{self.base_url}/models/segmentation"
        print(f"Fetching models from {url}")
        request = self.http_client.get(url)
        if self.http_client.success():
            result_str = self.http_client.get_response_as_string()
            try:
                run_list = cast_to_list_of_type(result_str, GaiaModel)
            except (ValueError, TypeError) as e:
                print(f"Unexpected response while fetching models: {e}")
                return []
            return run_list
        else:
            print("Error occurred while fetching project runs")
            return []
