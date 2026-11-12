import ipaddress
import json

from PyQt5 import QtCore, QtGui, QtNetwork
from PyQt5.QtCore import QByteArray, QUrl, QJsonDocument, QEventLoop, pyqtSignal

from gaia_client.storage.plugin_storage import PluginStore

# Sent on every request; the backend rejects anything without it with 401.
# Configured under Instaellningar -> API key and stored as "gaia_api_key".
API_KEY_HEADER = b"X-API-Key"
API_KEY_SETTING = "gaia_api_key"


def url_origin(url: str) -> tuple:
    """(scheme, host, port) of a URL, for comparing whether two URLs share an origin."""
    qurl = QtCore.QUrl(str(url).strip())
    scheme = qurl.scheme().lower()
    default_ports = {"http": 80, "https": 443}
    port = qurl.port(default_ports.get(scheme, -1))
    return (scheme, qurl.host().lower(), port)


def is_transport_safe_for_key(url: str) -> bool:
    """True if the API key may be sent to url.

    HTTPS always qualifies. Plain HTTP only qualifies for a *literal* loopback
    or private IP address (or "localhost"). Hostnames over HTTP are refused:
    checking what a name resolves to and then connecting is a race - DNS can
    answer differently the second time - so the key could end up in clear text
    on a public host."""
    qurl = QtCore.QUrl(str(url).strip())
    scheme = qurl.scheme().lower()
    if scheme == "https":
        return True
    if scheme != "http":
        return False
    host = qurl.host().strip("[]").lower()
    if host == "localhost":
        return True
    try:
        addr = ipaddress.ip_address(host.split("%")[0])
    except ValueError:
        return False
    # link-local (169.254.x.x, fe80::) counts as "private" in Python, but it
    # is where cloud metadata services live, never a GAIA backend
    return (addr.is_loopback or addr.is_private) and not (addr.is_global or addr.is_link_local)


def _add_qgis_trusted_cas(req: QtNetwork.QNetworkRequest) -> None:
    """Also trust the certificate authorities imported in QGIS (Settings ->
    Options -> Authentication -> Certificate manager). This client uses its
    own QNetworkAccessManager, which otherwise only knows the system's CAs -
    so a GAIA server using the proxy's internal CA would be rejected even
    after the operator trusted its root in QGIS."""
    try:
        from qgis.core import QgsApplication

        qgis_cas = QgsApplication.authManager().trustedCaCertsCache()
    except Exception:
        return
    if qgis_cas:
        conf = req.sslConfiguration()
        conf.setCaCertificates(list(conf.caCertificates()) + list(qgis_cas))
        req.setSslConfiguration(conf)


DEFAULT_MAX_RESPONSE_BYTES = 32 * 1024 * 1024
# Result archives are legitimately large.
MAX_DOWNLOAD_BYTES = 1024 * 1024 * 1024
# A request is aborted when no data moves for IDLE_TIMEOUT_MS, and in any case
# after its total deadline - a stalled server must not hang QGIS.
IDLE_TIMEOUT_MS = 60 * 1000
DEFAULT_TOTAL_TIMEOUT_MS = 5 * 60 * 1000
DOWNLOAD_TOTAL_TIMEOUT_MS = 60 * 60 * 1000


# There is no async support in PyQt5,
# so we have to use QEventLoop to block the execution of the code until
# the response is received.
# The responses are handled in the _handle_response method. And they are not
# cast to a type like in the requests library, so we have to handle the
# response manually. The response is stored in the _response_value attribute as a string.
# The conversion can be done outside per use case.
class HttpClient(QtCore.QObject):
    # Add a new signal for download progress
    download_progress = pyqtSignal(int, int)  # (bytes_received, total_bytes)

    def __init__(self, parent=None, api_key: str = None, send_api_key: bool = True,
                 max_response_bytes: int = DEFAULT_MAX_RESPONSE_BYTES,
                 total_timeout_ms: int = DEFAULT_TOTAL_TIMEOUT_MS):
        """api_key overrides the stored key. Used by the settings dialog to
        test a key the user has typed but not saved yet.

        send_api_key=False makes the client fully unauthenticated, for probing
        public endpoints and third-party hosts such as GeoServer.

        The *stored* key is only ever sent to the configured backend origin.
        An explicit api_key override is sent to whatever URL the caller asks
        for, so only pass one the user has just typed for that URL."""
        super(HttpClient, self).__init__(parent)

        self._loop = QEventLoop()
        self._request = QtNetwork.QNetworkAccessManager(self)
        self._request.finished.connect(self._handle_response)

        self._success = False
        self._response_value = None
        self._current_reply = None
        self._status_code = None
        self._api_key_override = api_key
        self._send_api_key = send_api_key
        self._max_response_bytes = max_response_bytes
        self._total_timeout_ms = total_timeout_ms
        self._output_file = None
        self._bytes_written = 0
        self._error_message = None

    def _build_request(self, url: str) -> QtNetwork.QNetworkRequest:
        """Build a request carrying the JSON content type and the API key."""
        req = QtNetwork.QNetworkRequest(QtCore.QUrl(url))
        req.setHeader(
            QtNetwork.QNetworkRequest.ContentTypeHeader, "application/json"
        )
        # Never follow redirects: one would carry the API key to wherever the
        # server points, without any of the origin checks below.
        req.setAttribute(
            QtNetwork.QNetworkRequest.RedirectPolicyAttribute,
            QtNetwork.QNetworkRequest.ManualRedirectPolicy,
        )
        if hasattr(req, "setTransferTimeout"):  # Qt >= 5.15
            req.setTransferTimeout(IDLE_TIMEOUT_MS)
        if req.url().scheme().lower() == "https":
            _add_qgis_trusted_cas(req)

        api_key = ""
        if self._send_api_key and not is_transport_safe_for_key(url):
            print("API key not sent: plain HTTP to a non-private address")
        elif self._send_api_key:
            if self._api_key_override is not None:
                api_key = self._api_key_override
            else:
                store = PluginStore()
                backend_url = store.get("gaia_backend_url", "")
                if backend_url and url_origin(url) == url_origin(backend_url):
                    api_key = store.get(API_KEY_SETTING, "")

        if api_key:
            req.setRawHeader(API_KEY_HEADER, str(api_key).encode("utf-8"))

        return req

    def status_code(self):
        """HTTP status of the last response, or None if the request failed
        before a response was received."""
        return self._status_code

    def _send(self, verb: str, url: str, parameters: dict = None,
              output_path: str = None):
        """Send one request and block (in a local event loop) until it ends.

        Every verb goes through here so they all get the same response-size
        cap, idle timeout, total deadline and abort handling. With output_path
        the body is streamed to a newly created file instead of memory."""
        self._success = False
        self._response_value = None
        self._status_code = None
        self._error_message = None
        self._bytes_written = 0
        self._output_file = None
        try:
            req = self._build_request(url)
            if output_path is not None:
                # "x": fail rather than overwrite an existing file
                self._output_file = open(output_path, "xb")

            body = None
            if parameters is not None:
                body = QJsonDocument.fromVariant(parameters).toJson()

            if verb == "GET":
                reply = self._request.get(req)
            elif verb == "POST":
                reply = self._request.post(req, body)
            elif verb == "PUT":
                reply = self._request.put(req, body)
            elif verb == "DELETE":
                reply = self._request.deleteResource(req)
            else:
                raise ValueError(f"unsupported verb {verb}")

            self._current_reply = reply
            reply.downloadProgress.connect(self._handle_progress)
            if self._output_file is not None:
                reply.readyRead.connect(self._write_available)
            print(f"{verb} request sent to {url}")

            deadline = QtCore.QTimer(self)
            deadline.setSingleShot(True)
            deadline.timeout.connect(self._on_deadline)
            deadline.start(self._total_timeout_ms)
            try:
                self._loop.exec()
            finally:
                deadline.stop()
                deadline.deleteLater()
        except Exception as e:
            print(e)
            self._success = False
        finally:
            self._current_reply = None
            if self._output_file is not None:
                self._output_file.close()
                self._output_file = None

    def get(self, url: str, output_path: str = None):
        self._send("GET", url, output_path=output_path)

    def post(self, url: str, parameters: dict):
        self._send("POST", url, parameters)

    def put(self, url: str, parameters: dict):
        self._send("PUT", url, parameters)

    def delete(self, url: str):
        self._send("DELETE", url)

    def abort(self):
        """Abort the request in flight (e.g. the user pressed Cancel)."""
        if self._current_reply is not None:
            self._current_reply.abort()

    def _on_deadline(self):
        print("Request exceeded its time limit - aborting")
        self.abort()

    def _write_available(self):
        reply = self._current_reply
        if reply is None or self._output_file is None:
            return
        chunk = bytes(reply.readAll())
        self._bytes_written += len(chunk)
        if self._max_response_bytes and self._bytes_written > self._max_response_bytes:
            print("Response exceeds the size limit - aborting")
            reply.abort()
            return
        self._output_file.write(chunk)

    def _handle_response(self, reply):
        print(f"Handling response - called for {reply.url()}")

        er = reply.error()

        self._status_code = reply.attribute(
            QtNetwork.QNetworkRequest.HttpStatusCodeAttribute
        )

        status = self._status_code
        if er == QtNetwork.QNetworkReply.NoError and status is not None \
                and not 200 <= int(status) < 300:
            # Qt reports an unfollowed redirect (and any other non-error
            # status) as NoError. Redirects are deliberately never followed,
            # so anything outside 2xx is a failure, not an empty success.
            location = reply.rawHeader(b"Location").data().decode("latin-1", "replace")
            if 300 <= int(status) < 400:
                print(
                    f"Server answered {status} redirect to '{location}' for "
                    f"{reply.url().toString()}. Redirects are not followed - "
                    "check the backend URL in Installningar (scheme, host, "
                    "trailing slash) or the reverse proxy configuration."
                )
            else:
                print(f"Unexpected HTTP status {status} for {reply.url().toString()}")
            self._success = False
        elif er == QtNetwork.QNetworkReply.NoError:
            if self._output_file is not None:
                self._write_available()
                # the write may itself have hit the cap
                self._success = reply.error() == QtNetwork.QNetworkReply.NoError
            else:
                byte_array: QByteArray = reply.readAll()
                if self._max_response_bytes and byte_array.size() > self._max_response_bytes:
                    print("Response exceeds the size limit")
                    self._success = False
                else:
                    self._response_value = byte_array
                    self._success = True

        else:
            self._error_message = self._read_error_message(reply)
            if self._status_code == 401:
                # Distinguish "wrong credential" from "server unreachable" -
                # otherwise a missing API key looks like a connectivity fault.
                print(
                    "Error occurred: 401 Unauthorized - the API key is missing "
                    "or incorrect. Check Installningar -> API key."
                )
            else:
                print("Error occurred: ", er)
                print(reply.errorString())

            self._success = False

        reply.deleteLater()
        self._loop.quit()

    def _handle_progress(self, bytes_received: int, total_bytes: int):
        # Abort a response that outgrows the cap instead of buffering it.
        if self._max_response_bytes and (
            bytes_received > self._max_response_bytes
            or total_bytes > self._max_response_bytes
        ):
            if self._current_reply is not None:
                print("Response exceeds the size limit - aborting")
                self._current_reply.abort()
            return
        # Emit the progress signal
        self.download_progress.emit(bytes_received, total_bytes)

    @staticmethod
    def _read_error_message(reply):
        """The backend explains refusals as {"error": ...} or {"detail": ...}.
        Read that (small, bounded) so the user sees the actual reason."""
        try:
            body = bytes(reply.read(64 * 1024))
            data = json.loads(body.decode("utf-8"))
        except Exception:
            return None
        if isinstance(data, dict):
            message = data.get("error") or data.get("detail")
            if isinstance(message, str):
                return message[:500]
        return None

    def error_message(self):
        """The server's reason for the last failed request, if it gave one."""
        return self._error_message

    def success(self):
        return self._success

    def get_response(self):
        return self._response_value

    def get_response_as_string(self):
        return str(self._response_value, "utf-8")
