from qgis._core import Qgis, QgsMessageLog, QgsPointXY

from gaia_client.ui.utils.window_utils import WindowUtils
from qgis.gui import QgsMapTool, QgsMapToolEmitPoint, QgsRubberBand
#from qgis.core import QgsRasterLayer, QgsProject, QgsRectangle
from qgis.PyQt.QtGui import QColor
from PyQt5.QtCore import pyqtSignal

'''Early attempt to create a bounding box selection tool
    This is so the user can create a box and then drag it to resize it
    Still work in progress.
    The dragging is not the best, as figuring out if it is close to a vertex is not the best way to do it.
'''

class PointTool(QgsMapToolEmitPoint):
    canvasClicked = pyqtSignal(QgsPointXY, name="QgsPointXY")
    canvasMoving = pyqtSignal(QgsPointXY, name="MovingPoint")
    canvasPressed = pyqtSignal(QgsPointXY, name="PressedPoint")

    def __init__(self, canvas):
        super(QgsMapTool, self).__init__(canvas)

    def canvasReleaseEvent(self, event):
        point_canvas_crs = event.mapPoint()

        self.canvasClicked.emit(point_canvas_crs)
        QgsMessageLog.logMessage('canvasReleaseEvent '+point_canvas_crs.asWkt())

    def canvasMoveEvent(self, event):
        point_canvas_crs = event.mapPoint()

        #print(f"canvasMoveEvent: {point_canvas_crs.asWkt()}")
        self.canvasMoving.emit(point_canvas_crs)
        #QgsMessageLog.logMessage('canvasMoveEvent '+point_canvas_crs.asWkt())

    def canvasPressEvent(self, event):
        point_canvas_crs = event.mapPoint()

        #print(f"canvasMoveEvent: {point_canvas_crs.asWkt()}")
        self.canvasPressed.emit(point_canvas_crs)


class SelectBoundingBox:
    def __init__(self):
        # Access the singleton WindowUtils instance
        self.window_utils = WindowUtils()
        self.iface = self.window_utils.get_iface()  # Get the iface from WindowUtils
        print(f"iface from select-bounding-box {self.iface}")
        self.canvas = self.iface.mapCanvas()

        self.map_tool = None
        self.rubber_band = None
        self.rubber_band_points = None
        self.current_points = []
        self.wkt_input = None
        self._affected_point = -10

    def start_drawing(self):
        self.map_tool = PointTool(self.canvas)
        #self.map_tool = QgsMapToolEmitPoint(self.canvas)
        self.old_map_tool = self.canvas.mapTool()
        print(f"old map-tool: {self.old_map_tool}")
        self.canvas.setMapTool(self.map_tool)
        print(f"new-map-tool from canvas: {self.canvas.mapTool()}")
        self.map_tool.canvasClicked.connect(self.mouse_click_release)
        self.map_tool.canvasMoving.connect(self.moving_mouse)
        self.map_tool.canvasPressed.connect(self.dragging_mouse)
        print(f"start_drawing - {self.canvas}")


        self.rubber_band = QgsRubberBand(self.canvas, Qgis.GeometryType.Polygon)
        self.rubber_band.setColor(QColor(0, 255, 150)) # red with 150 alpha
        self.rubber_band.setIcon(QgsRubberBand.IconType.ICON_CIRCLE)
        self.rubber_band.setIconSize( 20 )
        self.rubber_band.setWidth(2)
        #self.rubber_band_points = QgsRubberBand(self.canvas, Qgis.GeometryType.Point)
        #self.rubber_band_points.setIcon(QgsRubberBand.IconType.ICON_CIRCLE)
        #self.rubber_band_points.setIconSize( 10 )
        #self.rubber_band_points.setColor( QColor( 200, 50, 0, 150 ) )

        self.rubber_band.show()
        #self.rubber_band_points.show()

        #self.map_tool.activate()

    def mouse_click_release(self, point, button=None):
        print(f'onMapClick-release: {point.asWkt()}')

        if self._affected_point >= 0:
            self.current_points[self._affected_point] = point
            self._affected_point = -10
        else:
            self.current_points.append(point)

        self.rubber_band.addPoint(point, True)
        #self.rubber_band_points.addPoint(point, True)

        print(f'[Release] current points: {len(self.current_points)}')
        if len(self.current_points) == 2:
            #self.rubber_band.closePoints(True)
            self.show_wkt()

    def show_wkt(self):
        geom = self.rubber_band.asGeometry()
        wkt = geom.asWkt()
        #self.wkt_input.setText(wkt)
        print(f"Bounding box is: {wkt}")
        #self.rubber_band.reset(True)
        #self.rubber_band.reset()

    def moving_mouse(self, point):
        #print(f'on mouse move: {point.asWkt()}')
        if len(self.current_points) >= 1:
            #affected_position = self._affected_point if self._affected_point >= 0 else len(self.current_points) - 1
            self.rubber_band.removeLastPoint()
            #print(self.rubber_band.asGeometry().asWkt())
            self.rubber_band.addPoint(point, True)
            #self.rubber_band.movePoint(affected_position, point)
            print(f'[Moving] current points: {len(self.current_points)}, {point.asWkt()}')


    def dragging_mouse(self, point):
        print(f'on dragging mouse: {point.asWkt()}')
        if self.is_edge_move(point):
            print(f'removing affected point: {self._affected_point}')
            #self.rubber_band.removeLastPoint(True)
            #print(self.rubber_band.asGeometry().asWkt())
            #self.rubber_band.movePoint(self._affected_point, point)
            self.rubber_band.removePoint(self._affected_point, True)
            #self.rubber_band_points.removePoint(self._affected_point, True)
            #self.rubber_band.addPoint(point, True)

        print(f'[Dragging] current points: {len(self.current_points)}')

    def is_edge_move(self, point):
        # Check if the movement is on one of the rectangle's edges
        for i, p in enumerate(self.current_points):
            if point.distance(p) < 20:
                self._affected_point = i
                print(f"distance: {point.distance(p)} - Position: {i}")
                return True
        # (e.g., distance from the new click point to the edge < some threshold)
        return False