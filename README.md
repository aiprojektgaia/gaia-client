**This repository is not maintained**

This code is provided as-is under its licence, with no maintainer. Vulnerability
reports will not be received, triaged or fixed. Anyone who deploys or forks this
code is solely responsible for its security, including keeping dependencies
patched.

# gaia-client

QGIS plugin for GAIA. Select an area on the map, choose which object types to
detect, and load the resulting vector layers straight back into QGIS.

## Where this fits

GAIA is three repositories. This one is the user interface; the processing
happens on a GAIA server you connect to.

| Repository | Role |
|---|---|
| **gaia-backend** | REST API, database, scheduling |
| **gaia-engine** | Tiling, segmentation, vectorisation |
| **gaia-client** (this one) | QGIS plugin |

See **[gaia-backend/docs/ARCHITECTURE.md](https://github.com/aiprojektgaia/gaia-backend/blob/main/docs/ARCHITECTURE.md)**
for how they fit together.

## Requirements

| | |
|---|---|
| **QGIS** | **3.44 LTR or later, in the 3.x series** |
| GAIA server | A reachable `gaia-backend` and its API key |

> **QGIS 3.44 or later is required, and QGIS 4.x is not supported.**
>
> The plugin uses `enum.StrEnum` (Python 3.11+) and PEP 604 type unions, so it
> cannot load on QGIS 3.28 or earlier, which ship Python 3.9. QGIS 4.x moved to
> Qt6/PyQt6 while this plugin imports PyQt5 throughout — `metadata.txt` sets
> `qgisMaximumVersion=3.99` to block installation there.

The plugin installs no dependencies of its own. It uses the libraries inside
QGIS — which is why patching them means upgrading QGIS.

## Installation

**Plugins → Manage and Install Plugins → Install from ZIP**, then select
`GaiaClient_<version>_<date>.zip`

Then open the plugin, go to **Inställningar**, and enter:

| Field | Value |
|---|---|
| Gaia backend URL | `https://<server>:8443` (the HTTPS proxy shipped with gaia-backend; plain `http://` is accepted only for a literal loopback/private IP address or `localhost`, for development) |
| API-nyckel | The server's `GAIA_API_KEY` |
| Local GeoServer URL | `http://<server>:9600` (optional) |

The plugin verifies both the URL and the key before saving.

If the server uses the proxy's internal certificate authority, import its root
certificate (`gaia-root.crt`, from the server operator) first: either in QGIS
under *Settings → Options → Authentication → Manage certificates → Authorities*,
or in the operating system's trusted root store.

A step-by-step guide for operators is in
**[docs/ANVANDARGUIDE.md](docs/ANVANDARGUIDE.md)** (Swedish).

## Usage

1. The plugin opens as a sidebar next to the map canvas.
2. Use the project list to open an existing project, or **Skapa projekt**.
3. Inside a project, create a run: name it, select an area on the map, choose
   object types and a confidence level, then **Kör**.
4. When the run finishes, download the result to load it as QGIS layers.

## Documentation

| Document | Contents |
|---|---|
| [docs/ANVANDARGUIDE.md](docs/ANVANDARGUIDE.md) | Operator guide (Swedish) |
| [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) | Dev environment, live reload, building a release |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | Plugin structure, API layer, storage |
| [docs/security-fixes-260817.md](docs/security-fixes-260817.md) | Vulnerability audit record |

## Building a release

```bash
python create_release.py
```

Produces `release/GaiaClient_<version>_<date>.zip`, laid out the way QGIS
"Install from ZIP" expects — a single `gaia_client/` root containing
`metadata.txt`, with tests and bytecode excluded.

## License

Copyright (C) 2024-2026 Decerno AB

**GNU General Public License v3.0 or later (GPL-3.0-or-later).** Full text in
[LICENSE](LICENSE).

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version. It is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE. See the GNU General Public License for more details.

This is not a free choice. The plugin imports PyQt5 (**GPL v3**) and the QGIS
API (**GPL-2.0-or-later**), and a QGIS plugin is a derivative work of QGIS.
Combining GPLv3 code means the resulting work must be distributed under GPLv3
or later — a permissive licence such as MIT or Apache-2.0 is not available here.

Practical consequences:

- Anyone distributing this plugin, modified or not, must make the source
  available under the same terms.
- The other GAIA repositories are separate works and may carry different
  licences. `gaia-backend` communicates with this plugin over HTTP, which does
  not create a derivative work.
