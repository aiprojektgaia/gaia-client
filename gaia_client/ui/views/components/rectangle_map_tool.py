from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QColor
from qgis.core import QgsPointXY
from qgis.gui import QgsMapToolEmitPoint, QgsRubberBand
from qgis.core import QgsRectangle, QgsWkbTypes

class RectangleMapTool(QgsMapToolEmitPoint):
    on_area_selected = pyqtSignal(str, name="AreaSelected")
    def __init__(self, canvas):
        self.endPoint = None
        self.isEmittingPoint = None
        self.startPoint = None
        self.canvas = canvas
        QgsMapToolEmitPoint.__init__(self, self.canvas)
        self.rubberBand = QgsRubberBand(self.canvas, QgsWkbTypes.PolygonGeometry)

        area_color = QColor(62, 177, 200, 100)
        self.rubberBand.setColor(area_color)  # Set the color to blue-green
        self.reset()

    def reset(self):
        self.startPoint = self.endPoint = None
        self.isEmittingPoint = False
        self.rubberBand.reset(QgsWkbTypes.PolygonGeometry)

    def canvasPressEvent(self, e):
        self.startPoint = self.toMapCoordinates(e.pos())
        self.endPoint = self.startPoint
        self.isEmittingPoint = True
        self.showRect(self.startPoint, self.endPoint)

    def canvasReleaseEvent(self, e):
        self.isEmittingPoint = False
        r = self.rectangle()
        if r is not None:
            print("Rectangle:", r.xMinimum(), r.yMinimum(), r.xMaximum(), r.yMaximum())
            self._handle_selection(r)

    def canvasMoveEvent(self, e):
        if not self.isEmittingPoint:
            return

        self.endPoint = self.toMapCoordinates(e.pos())
        self.showRect(self.startPoint, self.endPoint)

    def showRect(self, start_point, end_point):
        self.rubberBand.reset(QgsWkbTypes.PolygonGeometry)
        if start_point.x() == end_point.x() or start_point.y() == end_point.y():
            return

        point1 = QgsPointXY(start_point.x(), start_point.y())
        point2 = QgsPointXY(start_point.x(), end_point.y())
        point3 = QgsPointXY(end_point.x(), end_point.y())
        point4 = QgsPointXY(end_point.x(), start_point.y())

        self.rubberBand.addPoint(point1, False)
        self.rubberBand.addPoint(point2, False)
        self.rubberBand.addPoint(point3, False)
        self.rubberBand.addPoint(point4, True)  # true to update canvas
        self.rubberBand.show()

    def rectangle(self):
        if self.startPoint is None or self.endPoint is None:
            return None
        elif (self.startPoint.x() == self.endPoint.x() or
              self.startPoint.y() == self.endPoint.y()):
            return None

        return QgsRectangle(self.startPoint, self.endPoint)


    def _handle_selection(self, rect):
        # translated: min_x, max_y, max_x, min_y
        expected_bbox_format = f"{rect.xMinimum()}, {rect.yMaximum()}, {rect.xMaximum()}, {rect.yMinimum()}"

        self.on_area_selected.emit(expected_bbox_format)
