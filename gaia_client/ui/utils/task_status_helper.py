from gaia_client.api.models.ProjectRun import TaskStatusEnum
from gaia_client.ui.i18n.se import (
    project_run_status_pending,
    project_run_status_running,
    project_run_status_finished,
    project_run_status_error,
    project_run_status_killed,
    project_run_status_queued,
    project_run_status_unknown,
)


def get_status_str_from_string(status: str):
    try:
        task_status = TaskStatusEnum[status]
        return get_status_str(task_status)
    except KeyError:
        return project_run_status_unknown


def get_status_str(status: TaskStatusEnum):
    if status == TaskStatusEnum.PENDING:
        return project_run_status_pending
    elif status == TaskStatusEnum.RUNNING:
        return project_run_status_running
    elif status == TaskStatusEnum.FINISHED:
        return project_run_status_finished
    elif status == TaskStatusEnum.ERROR:
        return project_run_status_error
    elif status == TaskStatusEnum.KILLED:
        return project_run_status_killed
    elif status == TaskStatusEnum.QUEUED:
        return project_run_status_queued
    else:
        return project_run_status_unknown


task_status_finished_states = [
    TaskStatusEnum.FINISHED,
    TaskStatusEnum.ERROR,
    TaskStatusEnum.KILLED,
]


def is_task_status_finished(status: TaskStatusEnum) -> bool:
    """
    Check if the task status is finished.
    :param status: Task status
    :return: True if the task status is finished, False otherwise
    """
    return status in task_status_finished_states
