from gaia_client.api.models.Project import Project
from gaia_client.api.models.ProjectRun import RunTypesEnum
from gaia_client.api.models.CreateProjectRun import CreateProjectRun
from gaia_client.api.requests.project_run import ProjectRunApi


def create_project_run(project: Project,
                       name: str,
                       bbox: str,
                       confidence: int,
                       overlap: int,
                       selected_model_ids: list[int],
                       max_confidence_value: int = 127, # this is the value used for the existing models
                       run_type: RunTypesEnum = RunTypesEnum.RunItAll,
                       ) -> tuple[bool, str | None]:
    """Returns (created, error message from the server if it refused)."""
    attributes = {
        "bbox": bbox,
        "confidence_level": confidence,
        "overlap": overlap,
        "interface_to_use": selected_model_ids,
        "wms_server_url": project.get_wms_url(),
        "layer_name": project.get_layer_name(),
        "mpp": project.get_meters_per_pixel(),
        "epsg": project.get_coordinate_system(),
        "max_confidence_value": max_confidence_value
    }
    new_project_run = CreateProjectRun(name, str(run_type), project.id, attributes)

    project_run_api = ProjectRunApi()
    created_project_run = project_run_api.create_run(new_project_run)
    if created_project_run:
        print(f"Project run {name} created successfully.")
        return True, None
    else:
        error = getattr(project_run_api, "last_error", None)
        print(f"Failed to create project run {name}: {error}")
        return False, error
