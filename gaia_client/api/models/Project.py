from datetime import datetime

from PyQt5.QtCore import QObject


class Project(QObject):
    def __init__(self, name: str, description: str, id: int = 0,
                 is_active: bool = False,
                 created_by: str = None, created_at: str = None,
                 updated_at: str = None, attributes: dict = None):
        super(Project, self).__init__()
        self.name = name
        self.description = description
        self.id = id
        self.is_active = is_active

        self.created_by = created_by

        if created_at is not None:
            self.created_at = datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%S.%f")
        else:
            self.created_at = None

        if updated_at is not None:
            self.updated_at = datetime.strptime(updated_at, "%Y-%m-%dT%H:%M:%S.%f")
        else:
            self.updated_at = None

        self.attributes = attributes

    def __str__(self):
        return f"{self.name}: {self.description} -> [Active: {self.is_active}]"

    def get_wms_url(self):
        if "wms_server_url" not in self.attributes:
            return ""
        return self.attributes["wms_server_url"]

    def get_layer_name(self):
        if "layer_name" not in self.attributes:
            return ""
        return self.attributes["layer_name"]

    def get_coordinate_system(self):
        if "epsg" not in self.attributes:
            return ""
        return self.attributes["epsg"]

    def get_meters_per_pixel(self):
        if "mpp" not in self.attributes:
            return ""
        return self.attributes["mpp"]
