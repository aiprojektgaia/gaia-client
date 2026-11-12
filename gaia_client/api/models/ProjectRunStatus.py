from PyQt5.QtCore import QObject
from gaia_client.api.models.ProjectRun import TaskStatusEnum


class ProjectRunStatus(QObject):
    def __init__(
        self,
        message: str,
        status: TaskStatusEnum,
        finished_tasks: int,
        total_tasks: int,
        calculating: bool = False,
        current_task_name: str = "",
        total_finished_step: int = 0,
        total_steps: int = 0,
    ):
        super(ProjectRunStatus).__init__()

        self.message = message
        self.status = TaskStatusEnum(status)
        self.finished_tasks = finished_tasks
        self.total_tasks = total_tasks

        # calculating: is used to indicate that the calculation of tiles
        # is not done and no valid numbers of steps can be given until
        # that step is finished
        self.calculating = calculating
        self.current_task_name = current_task_name
        self.total_finished_step = total_finished_step
        self.total_steps = total_steps

    def __str__(self):
        return (
            f"ProjectRunStatus(message={self.message} \n"
            f"Status={self.status.name}, \n"
            f"Finished_tasks={self.finished_tasks}, \n"
            f"Total_tasks={self.total_tasks}), \n"
            f"Calculating={self.calculating}, \n"
            f"Current_task_name={self.current_task_name}, \n"
            f"Total_finished_step={self.total_finished_step}, \n"
            f"Total_steps={self.total_steps}"
        )
