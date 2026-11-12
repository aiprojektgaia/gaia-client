from PyQt5.QtWidgets import QCheckBox


class QidCheckBox(QCheckBox):
    """
    A QCheckBox that has an ID attribute.
    """

    def __init__(self, id: int, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.id = id