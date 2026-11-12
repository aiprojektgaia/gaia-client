from PyQt5.QtWidgets import QLabel


#class QidWidget(QWidget):
#    """
#    A QWidget that has an ID attribute.
#    """
#
#    def __init__(self, id: int, *args, **kwargs):
#        super().__init__(*args, **kwargs)
#        self.id = id


class QidLabel(QLabel):
    """
    A QLabel that has an ID attribute.
    """

    def __init__(self, id: int, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.id = id

