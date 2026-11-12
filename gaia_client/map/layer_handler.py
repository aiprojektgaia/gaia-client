import ipaddress
import re
from urllib.parse import quote, urlsplit

from gaia_client.ui.utils.safe_text import ask_yes_no
from qgis._core import QgsRasterLayer
from qgis.core import QgsProject, QgsCoordinateReferenceSystem

from gaia_client.api.requests.http_client import HttpClient, url_origin
from gaia_client.storage.plugin_storage import PluginStore

_SAFE_LAYER_NAME = re.compile(r"^[A-Za-z0-9_][A-Za-z0-9_:.\-]{0,127}$")
_SAFE_CRS = re.compile(r"^EPSG:\d{3,6}$")
APPROVED_ORIGINS_KEY = "approved_wms_origins"


def _origin_text(url: str) -> str:
    scheme, host, port = url_origin(url)
    return f"{scheme}://{host}:{port}"


def _literal_ip(host: str):
    try:
        return ipaddress.ip_address(host.strip("[]").split("%")[0])
    except ValueError:
        return None


def _wms_redirects(wms_url: str) -> bool:
    """Probe the server once without following redirects. QGIS's WMS provider
    would follow them, which could take the workstation from an approved
    origin to an unapproved one, so a redirecting server is refused."""
    probe = HttpClient(send_api_key=False, max_response_bytes=4 * 1024 * 1024,
                       total_timeout_ms=30 * 1000)
    sep = "&" if "?" in wms_url else "?"
    probe.get(f"{wms_url}{sep}SERVICE=WMS&REQUEST=GetCapabilities")
    status = probe.status_code()
    return status is not None and 300 <= int(status) < 400


def clear_approved_wms_origins():
    PluginStore().set(APPROVED_ORIGINS_KEY, "")


def _wms_origin_approved(wms_url: str) -> bool:
    """Project data comes from the backend and may be shared between users, so
    the WMS address in it is untrusted. Contact only the configured GeoServer
    or an origin the operator has explicitly approved."""
    store = PluginStore()
    origin = _origin_text(wms_url)
    configured = store.get("geoserver_url", "")
    if configured and origin == _origin_text(configured):
        return True
    approved = store.get(APPROVED_ORIGINS_KEY, "") or ""
    approved_list = [o for o in str(approved).split(",") if o]
    if origin in approved_list:
        return True
    addr = _literal_ip(url_origin(wms_url)[1])
    if addr is not None and (addr.is_link_local or addr.is_multicast
                             or addr.is_unspecified or addr.is_reserved):
        # e.g. 169.254.169.254, cloud metadata - never a map server
        print(f"Refusing WMS origin {origin}")
        return False
    warning = ""
    if addr is not None and (addr.is_loopback or addr.is_private):
        warning = "Note: this is an address on your own computer or internal network.\n"
    answer = ask_yes_no(
        None,
        "WMS",
        f"The project wants to load map data from\n{origin}\n\n"
        "This is not your configured GeoServer. Only continue if you trust it.\n"
        f"{warning}"
        "Your answer is remembered; clear approvals under Inställningar.",
    )
    if answer:
        store.set(APPROVED_ORIGINS_KEY, ",".join(approved_list + [origin]))
        return True
    return False


def zoom_to_layer(iface, layer):
    canvas = iface.mapCanvas()
    canvas.setExtent(layer.extent())
    canvas.refresh()

def set_crs(iface, epsg: str = 'EPSG:3006'):
    """Set the project CRS to the runs CRS."""
    project_instance = QgsProject.instance()
    print("Current crs:", project_instance.crs().description())
    print("Current crs authority:", project_instance.crs().authid())

    crs = QgsCoordinateReferenceSystem(epsg)
    if crs.isValid():
        print("CRS Description: {}".format(crs.description()))
        print("To set EPSG: {}".format(crs.authid()))
        project_instance.setCrs(crs)
        # do I really need this?
        canvas = iface.mapCanvas()
        canvas.setDestinationCrs(crs)
        print(f"Project CRS set to {epsg}")
    else:
        print("Invalid CRS!")

def add_layer_to_qgis(iface, wms_url:str, layer_name:str, coordinate_system: str) -> bool:
    qgis_instance = QgsProject.instance()
    layers = qgis_instance.mapLayers()
    for layer in layers:
        layer_name_in_qgis_list = layer_name.replace(':', '_')
        if str(layer).startswith(layer_name_in_qgis_list):
            print(f"Layer {layer} already added to QGIS")
            map_layer = qgis_instance.mapLayer(layer)
            set_crs(iface, coordinate_system)
            zoom_to_layer(iface, map_layer)
            return True

    # If I am here => the layer is not in QGIS
    # add wms layer to the layers view
    # Create a QgsRasterLayer object
    # Danke meine Freund: https://www.youtube.com/watch?v=QB_3KEOlftk
    parts = urlsplit(str(wms_url))
    if parts.scheme not in ("http", "https") or not parts.hostname or parts.username or parts.password:
        print("Refusing WMS layer: the url must be http(s) without credentials")
        return False
    if not _SAFE_LAYER_NAME.match(str(layer_name)) or not _SAFE_CRS.match(str(coordinate_system)):
        print("Refusing WMS layer: invalid layer name or coordinate system")
        return False
    # Same rule as the engine's tiler: a URL that does not end in "wms" is the
    # GeoServer base, and the WMS endpoint is "<url>/wms". Without this the
    # probe and QGIS would hit e.g. "/geoserver", which redirects.
    wms_url = str(wms_url).rstrip("/")
    if not wms_url.lower().endswith("wms"):
        wms_url = f"{wms_url}/wms"
    if not _wms_origin_approved(wms_url):
        print("WMS origin not approved")
        return False
    if _wms_redirects(wms_url):
        print("Refusing WMS layer: the server redirects elsewhere")
        return False
    # Values are percent-encoded so a crafted url cannot inject extra
    # provider parameters (the provider string is '&'-separated).
    source = (
        f"crs={coordinate_system}&dpiMode=7&featureCount=10&format=image/png"
        f"&layers={quote(layer_name, safe=':')}&styles&tilePixelRatio=0"
        f"&url={quote(str(wms_url), safe=':/?=')}"
    )
    wms_layer = QgsRasterLayer(source, layer_name, "wms")

    # Add the layer to the map canvas
    if wms_layer.isValid():
        qgis_instance.addMapLayer(wms_layer)
        set_crs(iface, coordinate_system)
        zoom_to_layer(iface, wms_layer)
    else:
        print("Failed to add WMS layer")
        return False

    return True
