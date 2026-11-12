from PyQt5.QtCore import QObject


class GaiaModel(QObject):
    def __init__(self, id: int, name: str, description: str):
        super(GaiaModel, self).__init__()

        self.id = id
        self.name = name
        self.description = description
