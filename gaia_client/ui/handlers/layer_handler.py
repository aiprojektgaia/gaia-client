# layer_handler.py
from gaia_client.ui.config import OrthoConfig
from gaia_client.ui.images import gaia_logo_png
from qgis.core import QgsRasterLayer, QgsProject, QgsRectangle
from gaia_client.ui.utils.window_utils import WindowUtils
from qgis.PyQt.QtWidgets import QMessageBox
from PIL import Image

class LayerHandler:
    """Handles loading and managing layers in QGIS."""

    def __init__(self):
        # Access the singleton WindowUtils instance
        self.window_utils = WindowUtils()
        self.iface = self.window_utils.get_iface()  # Get the iface from WindowUtils

        # Initialize a dictionary to keep references to layers
        self.layers = {}

    def load_logo_layer(self) -> None:
        """Load logo layer and make it active, then zoom to it."""
        existing_layers = QgsProject.instance().mapLayersByName("Gaia Logo")
        if existing_layers:
            logo_layer = existing_layers[0]
            # Make the WMS layer active
            self.iface.setActiveLayer(logo_layer)
            self.iface.zoomToActiveLayer()

        else:
            logo_layer = QgsRasterLayer(gaia_logo_png, "Gaia Logo")
            if not logo_layer.isValid():
                print("Failed to load the logo layer!")
                QMessageBox.critical(None, "Layer Load Error", "Failed to load the Gaia Logo layer.")
                return
            # Add the layer to the project without adding it to the legend
            QgsProject.instance().addMapLayer(logo_layer)

    def load_ortho_layer(self) -> None:
        """Load and setup WMS layer, make it active, then zoom to it."""
        existing_layers = QgsProject.instance().mapLayersByName("Orthophoto")
        if existing_layers:
            wms_layer = existing_layers[0]
            logo_layers = QgsProject.instance().mapLayersByName("Gaia Logo")
            if logo_layers:
                QgsProject.instance().layerTreeRoot().findLayer(logo_layers[0].id()).setItemVisibilityChecked(False)
            # Make the WMS layer active
            self.iface.setActiveLayer(wms_layer)
            self.iface.zoomToActiveLayer()

        else:
            wms_url = self._build_ortho_url()
            wms_layer = QgsRasterLayer(wms_url, "Orthophoto", "wms")

            if not wms_layer.isValid():
                print("Failed to load the WMS layer!")
                QMessageBox.critical(None, "Layer Load Error", "Failed to load the Orthophoto WMS layer.")
                return
            
            logo_layers = QgsProject.instance().mapLayersByName("Gaia Logo")
            if logo_layers:
                QgsProject.instance().layerTreeRoot().findLayer(logo_layers[0].id()).setItemVisibilityChecked(False)

            wms_layer.setExtent(QgsRectangle(*OrthoConfig.INITIAL_EXTENT))
            QgsProject.instance().addMapLayer(wms_layer, addToLegend=True)
            self.iface.setActiveLayer(wms_layer)
            self.iface.zoomToActiveLayer()

    def _build_ortho_url(self) -> str:
        """Build WMS URL with parameters."""
        config = OrthoConfig.WMS_CONFIG
        width, height = self.window_utils.get_inner_main_window_dimensions()
        return (
            f"{config['base_url']}?"
            f"bbox={','.join(map(str, OrthoConfig.INITIAL_EXTENT))}&"
            f"width={width}&"
            f"height={height}&"
            f"crs={config['proj']}&"
            f"dpiMode={config['dpi_mode']}&"
            f"format={config['format']}&"
            f"layers={config['layer']}&"
            f"styles=&"
            f"tilePixelRatio=0&"
            f"url={config['base_url']}?servicename%3D{config['service']}"
        )