from dataclasses import dataclass
from typing import Tuple

@dataclass
class OrthoConfig:
    """Map configuration constants."""
    INITIAL_EXTENT: Tuple[float, float, float, float] = (
        15.5, 58.3, 16.0, 58.5)  # Linköping bbox
    WMS_CONFIG = {
        'proj': 'EPSG:4326',
        'dpi_mode': 7,
        'format': 'image/png',
        'layer': 'satellitbild_ostergotaland',
        'base_url': 'https://kartan.linkoping.se/wms',
        'service': 'wms_ortofoto'
    }
