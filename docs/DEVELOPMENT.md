# Development

Working on the QGIS plugin. For what it does, see the
[README](../README.md); for how it is structured, see
[ARCHITECTURE.md](ARCHITECTURE.md).

## Prerequisites

- **QGIS 3.44 LTR or later** in the 3.x series. The plugin runs inside QGIS and
  uses its bundled Python (3.12), so there is no separate virtual environment.
- An editor with Python support. The notes below assume VS Code.

You cannot develop this against a plain Python install — `qgis.core` only exists
inside a QGIS installation.

## Editor setup

For autocompletion and go-to-definition on the `qgis` and `PyQt5` packages, add
QGIS's library paths to your workspace `settings.json`:

```json
"python.analysis.extraPaths": [
  "C:\\Program Files\\QGIS 3.44\\apps\\qgis-ltr\\python",
  "C:\\Program Files\\QGIS 3.44\\apps\\Python312\\Lib\\site-packages"
]
```

Adjust the version and Python folder to match your install — QGIS 3.44 ships
Python 3.12, earlier versions differ.

Useful references:

- [QGIS Python API](https://qgis.org/pyqgis/master/)
- [Qt for Python (PyQt5)](https://doc.qt.io/qtforpython-5/contents.html)

## The edit–reload loop

QGIS loads plugins from a fixed profile directory, so development means copying
your working tree there and reloading.

**1. Copy on save.** `copy_gaia_client.py` copies `gaia_client/` into the QGIS
plugins directory. Edit the `destination_dir` in it to match your machine:

| OS | Plugins directory |
|---|---|
| Windows | `C:\Users\<user>\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins` |
| macOS | `~/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins` |
| Linux | `~/.local/share/QGIS/QGIS3/profiles/default/python/plugins` |

Automate it with the `emeraldwalk.runonsave` VS Code extension:

```json
"emeraldwalk.runonsave": {
  "commands": [
    { "match": "gaia_client/*.*", "cmd": "python copy_gaia_client.py" }
  ]
}
```

**2. Reload in QGIS.** Install the **Plugin Reloader** plugin, point it at
`gaia_client`, then after each save:

1. Close the plugin window
2. Click **Reload plugin: gaia_client**
3. Reopen the plugin

This is not a fast loop, and occasionally QGIS gets into a state where a full
restart is the only way out — usually after changing module-level code or
imports.

**3. Watch the log.** The plugin writes to the QGIS Python console
(**Plugins → Python Console**). Network failures, including a rejected API key,
are reported there rather than in the UI.

## Testing

There is no automated test suite. `gaia_client/test/` holds a PyQt scratch area
for experimenting with widgets outside QGIS, and `main.py` in the repository
root opens a bare PyQt window for layout work — neither exercises the plugin.

What can be checked without QGIS:

```bash
python -m compileall gaia_client     # syntax across the package
```

Everything else needs manual verification in QGIS. When changing the API layer,
the highest-value checks are: settings validation accepts a good URL and key and
rejects a bad key; the object-type selector populates; a run completes and its
results load as layers.

## Building a release

```bash
python create_release.py
```

Produces `release/GaiaClient_<version>_<date>.zip`, reading name and version
from `gaia_client/metadata.txt`.

The archive has a **single `gaia_client/` root** containing `metadata.txt`,
which is what QGIS's installer looks for. `README.md` and `requirements.txt` are
placed *inside* that folder rather than beside it — QGIS extracts the whole
archive into the plugins directory, so anything at the root would be dropped
loose among other plugins.

Excluded: `test/`, `__pycache__/`, `.pyc`/`.pyo`/`.pyd`.

Bump `version` in `gaia_client/metadata.txt` before building a release.

## Conventions

- **UI strings live in `gaia_client/ui/i18n/se.py`.** Do not hardcode text in
  widgets; add a constant and import it.
- **All HTTP goes through `HttpClient`.** It attaches the `X-API-Key` header in
  `_build_request()` — a request built any other way will be rejected with 401.
- **Prefer the public `qgis.core` / `qgis.gui` modules.** Three files still
  import the private `qgis._core`; that works but is unsupported API and a
  likely source of breakage on future QGIS versions.

## Adding a feature

1. Branch from `main`.
2. Add UI strings to `se.py`.
3. Implement the view under `ui/views/`, request code under `api/requests/`.
4. Verify manually in QGIS — reload, exercise the path, watch the Python console.
5. Open a pull request.
