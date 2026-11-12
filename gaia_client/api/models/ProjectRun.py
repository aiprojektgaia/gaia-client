from datetime import datetime
from enum import StrEnum, Enum
from typing import Any

from PyQt5.QtCore import QObject


class TaskStatusEnum(Enum):
    PENDING = 0
    QUEUED = 1
    RUNNING = 2
    FINISHED = 3
    ERROR = 4
    KILLED = 5

    @classmethod
    def has_member_key(self, key):
        return key in self.__members__


class RunTypesEnum(StrEnum):
    SegmentArea = "SegmentArea"
    CompareToBaseImage = "CompareToBaseImage"
    Vectorize = "Vectorize"
    # TODO: this should be removed or have a nicer name
    RunItAll = "RunItAll"

    def __str__(self):
        return "%s" % self.value


def _require_positive_int(value, field: str) -> int:
    # bool is an int subclass; strings such as "../x" must never get through.
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"Invalid {field} in backend response")
    return value


class ProjectRun(QObject):
    def __init__(
        self,
        id: int,
        name: str,
        run_type: RunTypesEnum,
        project_id: int,
        is_active: bool = False,
        created_at: str = None,
        finished_at: str = None,
        status: TaskStatusEnum = TaskStatusEnum.PENDING,
        attributes: dict = None,
        **kwargs,
    ):
        super(ProjectRun, self).__init__()

        # Identifiers end up in local file names, so they must be real
        # integers; anything else from the backend is rejected outright.
        self.id = _require_positive_int(id, "id")
        self.name: str = name
        self.run_type: RunTypesEnum = run_type
        self.project_id: int = _require_positive_int(project_id, "project_id")
        self.is_active: bool = is_active
        self.attributes: dict[str, Any] = attributes
        self.status = TaskStatusEnum[status]

        if created_at is not None:
            self.created_at = datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%S.%f")
        else:
            self.created_at = None

        if finished_at is not None:
            self.finished_at = datetime.strptime(finished_at, "%Y-%m-%dT%H:%M:%S.%f")
        else:
            self.finished_at = None

    def __str__(self):
        return f"{self.name}: {self.run_type} -> [Active: {self.is_active}]"

    def get_coordinate_system(self, default="EPSG:4326"):
        return self.attributes.get("epsg", default)
