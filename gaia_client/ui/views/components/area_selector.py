from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QPushButton, QLineEdit

from gaia_client.ui.i18n.se import project_create_run_select_area_button, \
    project_create_run_select_area_error
from gaia_client.ui.validators.bbox_validator import BboxValidator
from gaia_client.ui.views.components.rectangle_map_tool import RectangleMapTool
from gaia_client.ui.views.components.validated_input import ValidatedInput


class AreaSelector(QObject):
    def __init__(self, iface, layout, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.iface = iface
        self.layout = layout
        self.rect_tool = None
        self.bbox_input = None

        self._add_area_selector_button()
        print("AreaSelector - [set]")

    def _add_area_selector_button(self):
        """Setup create project button."""

        self.draw_bbox_button = QPushButton(project_create_run_select_area_button)
        self.draw_bbox_button.clicked.connect(self._draw_bbox)
        self.layout.addWidget(self.draw_bbox_button)

        self.bbox_validated_input = ValidatedInput("",
                                                   project_create_run_select_area_error,
                                                   text_hint="minX, maxY, maxX, minY",
                                                   validator=BboxValidator(self),
                                                   )
        self.layout.addWidget(self.bbox_validated_input)

        self.layout.setSpacing(2)  # Reduce spacing between label and input

    def _draw_bbox(self):
        print("Draw bbox - [start call]")
        canvas = self.iface.mapCanvas()
        self.rect_tool = RectangleMapTool(canvas)
        canvas.setMapTool(self.rect_tool)
        self.rect_tool.on_area_selected.connect(self._on_area_selected)
        print("Draw bbox - [end call]")

    def _on_area_selected(self, bbox_str):
        self.bbox_validated_input.set_value(bbox_str)

    def get_bbox(self):
        bbox_text = self.bbox_validated_input.get_value().strip()
        return bbox_text

    def get_input(self):
        return self.bbox_validated_input.get_input()

    def disable_select_box(self):
        if self.rect_tool:
            self.rect_tool.reset()
            self.rect_tool = None
