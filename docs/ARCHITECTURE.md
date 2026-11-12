# Plugin architecture

How the QGIS plugin is put together. For the system-level view see
[gaia-backend/docs/ARCHITECTURE.md](https://github.com/aiprojektgaia/gaia-backend/blob/main/docs/ARCHITECTURE.md).

## Entry point

QGIS loads a plugin by importing the package and calling `classFactory(iface)`.
`gaia_client/__init__.py` checks that `metadata.txt` is present, then returns a
`GaiaClientPlugin`:

| Method | Called when |
|---|---|
| `initGui()` | Plugin is enabled — registers the toolbar action and menu entry |
| `run()` | User activates it — builds and shows the main dialog |
| `unload()` | Plugin is disabled or reloaded — must remove everything `initGui` added |

`unload()` matters during development: the Plugin Reloader calls it before
re-importing, and anything left registered accumulates duplicate toolbar
buttons.

## Layout

```
gaia_client/
  __init__.py        classFactory - QGIS entry point
  plugin.py          GaiaClientPlugin lifecycle
  api/               talking to gaia-backend
    requests/        HttpClient, one module per endpoint group
    models/          typed response objects
    helpers/         casting JSON to those objects
  ui/
    views/           screens, one per step of the flow
      dialogs/       modal dialogs
      components/    reusable widgets
    widgets/         custom controls
    utils/           router, timers, window helpers
    i18n/se.py       all user-facing strings
    static/          icons and images
  storage/           persisted settings and project state
  map/               QGIS layer and canvas interaction
  use_cases/         multi-step operations spanning API, storage and map
```

## The API layer

**Everything goes through `HttpClient`** (`api/requests/http_client.py`). It
wraps `QNetworkAccessManager` and blocks on a `QEventLoop`, because PyQt5 has no
async support and the plugin runs on the UI thread.

All four verbs build their request through `_build_request()`, which sets the
JSON content type and attaches the `X-API-Key` header from stored settings. A
request constructed any other way is rejected by the backend with 401 — so add
new calls through `HttpClient`, never by building a `QNetworkRequest` directly.

`HttpClient(api_key=...)` overrides the stored key, which the settings dialog
uses to validate a key the user has typed but not yet saved.

`BaseRequest` supplies the base URL from stored settings; `ProjectApi`,
`ProjectRunApi` and `ModelsApi` extend it, one per endpoint group. Responses are
raw strings, converted by `api/helpers/casting.py` into the typed objects in
`api/models/`.

Blocking on an event loop means a slow backend freezes the QGIS UI. That is why
the download flow reports progress through the `download_progress` signal and
warns the user that QGIS may become unresponsive.

## Storage

Two singletons over `QgsSettings`, so values survive QGIS restarts:

| Store | Holds |
|---|---|
| `PluginStore` | `gaia_backend_url`, `geoserver_url`, `gaia_api_key` |
| `ProjectStorage` | Current project and run selection |

Keys are namespaced under `gaia-plugin/`. `QgsSettings` is QGIS's own settings
backend, so values land in the user profile rather than a plugin-local file.

> The API key is stored as plain text in QGIS settings, like the backend URL. It
> is a shared secret, not a user credential — see the backend `SECURITY.md`.

## UI flow

Screens are plain `QWidget`s swapped by `ui/utils/router.py` rather than
separate windows:

```
project_start  →  project  →  project_run_create
 (list/create)    (runs)      (parameters, execute)
```

Dialogs (`settings_dialog`, `create_project_dialog`,
`project_run_info_dialog`) are modal and sit outside the router.

`timer_manager.py` drives run-status polling — the backend has no push channel,
so an active run is polled via `GET /runs/{id}/status` until it finishes.

**All user-facing text lives in `ui/i18n/se.py`.** Strings are Swedish. Import a
constant rather than hardcoding text in a widget; it is the only reason
translating this plugin would be tractable.

## Object-type selector

`ModelTypeSelectorQGroupBox` renders one checkbox per model returned by
`GET /models/segmentation`. It is fully data-driven — if the backend returns an
empty list, the group box renders empty with no error. That is the usual cause
of "Välj objektyper" appearing to vanish; the fault is server-side.

## Dependencies

The plugin declares no installable dependencies. It uses the Python environment
inside QGIS, so `requirements.txt` documents that environment rather than
listing things to install.

The plugin itself imports only `PyQt5`, the `qgis` API, and the standard
library. `PIL` is imported in one file but unused.

Consequence: **the plugin cannot patch its own dependencies.** A vulnerability in
Pillow or urllib3 is fixed by upgrading QGIS, not by changing this repository.

## Known rough edges

- **Three files import the private `qgis._core` / `qgis._gui`** instead of the
  public `qgis.core` / `qgis.gui`: `map/layer_handler.py`,
  `ui/handlers/select_bounding_box.py`, `use_cases/get_and_show_run_results.py`.
  This works but is unsupported API and likely to break on a future QGIS.
- **Two different `layer_handler.py` files** exist, under `map/` and
  `ui/handlers/`. They are not the same module.
- **Blocking HTTP on the UI thread** freezes QGIS for the duration of every
  request.
- **`ui/handlers/layer_handler.py` imports `PIL.Image` without using it.**
