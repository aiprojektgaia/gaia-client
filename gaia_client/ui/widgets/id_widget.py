from PyQt5.QtWidgets import QLayout, QFrame


class QIdWidget(QFrame):
    def __init__(self, id: int, parent=None):
        super().__init__(parent)
        self.id = id
        self.setFrameShape(QFrame.NoFrame)

    def get_id(self) -> int:
        return self.id


def remove_widget_by_id(layout: QLayout, id: int):
    for i in range(layout.count()):
        widget = layout.itemAt(i).widget()
        if not hasattr(widget, "id") or not isinstance(widget, QIdWidget):
            continue

        if widget.id == id:
            layout.removeWidget(widget)
            widget.deleteLater()
            return
