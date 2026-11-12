from typing import Any

from PyQt5.QtCore import QObject

from gaia_client.api.models.ProjectRun import RunTypesEnum


class CreateProjectRun(QObject):
    def __init__(self,
                 name: str,
                 run_type: str,
                 project_id: int,
                 attributes: dict = None):
        super(CreateProjectRun, self).__init__()

        self.name: str = name
        self.run_type: str = run_type
        self.project_id: int = project_id
        self.attributes: dict[str, Any] = attributes

    def __str__(self):
        return f"{self.name}: {self.run_type} -> [Active: {self.is_active}]"
