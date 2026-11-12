# Security fixes — audit 2026-08-17

Remediation of `vulnerability_audit_260817.json` (OWASP Dependency-Track 4.14.1
/ Trivy). The audit reported **~50 vulnerabilities across 16 packages**, the
largest being pillow (19), urllib3 (12) and requests (6).

## The fix: raise the supported QGIS baseline

The GAIA client is a QGIS plugin. It does **not** install its own dependencies —
every package in `requirements.txt` is supplied by the Python environment that
ships inside QGIS. Pinning newer versions there would not change a single byte
of what QGIS actually loads at runtime; it would only make the SBOM scan look
clean while the vulnerable libraries stayed in place.

The only real remedy is to move the supported QGIS version forward, so the
plugin runs on an environment that already contains patched libraries.

**Baseline moved from QGIS 3.28.15 LTR to QGIS 3.44.13 LTR "Solothurn".**

This clears **every** advisory in the audit. The versions in `requirements.txt`
are now transcribed from the OSGeo4W package index for the 3.44 LTR bundle, so
the file documents the supported runtime rather than an installable pin set.

Regenerate from <https://download.osgeo.org/osgeo4w/v2/x86_64/setup.ini> when the
supported QGIS version changes.

## Representative upgrades (all QGIS-supplied)

| Package | QGIS 3.28.15 | QGIS 3.44.13 | Advisories cleared |
|---|---|---|---|
| pillow | 11.0.0 | 12.3.0 | 19 |
| urllib3 | 2.2.1 | 2.7.0 | 12 |
| requests | 2.31.0 | 2.34.2 | 6 |
| setuptools | 69.2.0 | 84.0.0 | 5 |
| GDAL | 3.9.3 | 3.13.2 | 10 |
| Jinja2 | 3.1.3 | 3.1.6 | 4 |
| lxml | 5.2.1 | 6.1.1 | 2 |
| certifi | 2024.2.2 | 2026.10.23 | 1 (+ emSign, see below) |
| httplib2 | 0.22.0 | 0.32.0 | 1 |
| Pygments | 2.17.2 | 2.20.0 | 2 |
| fonttools | 4.51.0 | 4.63.0 | 2 |
| idna | 3.7 | 3.18 | 1 |
| geopandas | 1.0.0 | 1.1.4 | 2 |

## Packages removed from the baseline

These are no longer part of the QGIS bundle and are not imported by the plugin:

`PyPDF2`, `PyQt5-stubs`, `cattrs`, `docstring-to-markdown`,
`jedi-language-server`, `lsprotocol`, `pygls`

`PyPDF2` matters specifically: it is abandoned upstream (superseded by `pypdf`)
and its remaining advisory **GHSA-4vvm-4w3v-6mr8** has no fixed version in the
PyPDF2 line. Dropping it is the only resolution. Nothing in the plugin used it.

## Also fixed: the plugin could not run on the old baseline

`metadata.txt` previously declared `qgisMinimumVersion=3.0`, which was wrong.
The plugin uses `enum.StrEnum` (Python 3.11+) and PEP 604 `X | None`
annotations (Python 3.10+), while QGIS 3.28.15 ships **Python 3.9**. Six modules
fail to import there, including `gaia_client.plugin` — the plugin could not load
at all. QGIS 3.44.13 ships Python 3.12.14, on which all modules import cleanly.

`metadata.txt` now declares:

```
qgisMinimumVersion=3.44
qgisMaximumVersion=3.99
```

The maximum is deliberate. QGIS 4.x is built on Qt6/PyQt6; this plugin imports
`PyQt5` throughout and would break. The bound keeps it from being installed
into QGIS 4 until it is ported.

## Verification

- `requirements.txt` — 0 outstanding advisories against OSV (64 pins checked).
- All 13 pure-Python / PyQt5 modules import on Python 3.12; `RunTypesEnum`
  (`StrEnum`) resolves correctly.
- Release archive validated against QGIS's own `installFromZipFile` logic:
  single `gaia_client/` root, `metadata.txt` discovered, no `__pycache__`,
  `.pyc` or `test/` content.

## Follow-up audit 2026-08-18 — three residual findings, none fixable

`vulnerability_audit_260818.json` reports 3 findings on 2 packages. **None can
be resolved by a version change: both packages are already at the newest release
that has ever existed.** They are answered with a VEX document instead —
`vex_260818.json`, ready to upload to Dependency-Track.

| Package | Finding | Rated | Disposition |
|---|---|---|---|
| future 1.0.0 | GHSA-xqrq-4mgf-ff32 | high | `false_positive` — **withdrawn by GitHub on 2025-10-06** |
| future 1.0.0 | CVE-2025-50817 | medium | `not_affected` — disputed, no fix exists, not reachable |
| ply 3.11 | CVE-2025-56005 | critical 9.8 | `not_affected` — disputed, no fix exists, not reachable |

**GHSA-xqrq-4mgf-ff32 should not be reported at all.** GitHub withdrew it on
2025-10-06 (it is an alias of CVE-2025-50817). Dependency-Track is matching
against a stale mirror of the GitHub Advisory Database — refreshing that mirror
should clear this finding without any VEX entry.

**Neither package has an upgrade path.** `future` 1.0.0 is the final release of
a dormant project, and OSV records the advisory as `introduced: 0.14.0` with no
`fixed` event. `ply` 3.11 dates from 2018 and is likewise the latest. Bumping
the pins is not an option.

**Both CVEs are disputed at NVD.** CVE-2025-50817 is described by multiple third
parties as documented CPython `sys.path` import behaviour rather than a flaw in
python-future. CVE-2025-56005 carries a third-party assertion that it should be
rejected because the proof of concept does not demonstrate code execution.

**Neither is reachable from this plugin.** The client imports only PIL, PyQt5,
the `qgis` API and the standard library — never `future`, never `ply`. Both are
present solely because the QGIS bundle pulls them in. Verified against the
OSGeo4W package index for QGIS 3.44.13:

- `python3-future` is required by `qgis-ltr-common` — it is in the core QGIS
  bundle and cannot be removed.
- `python3-ply` is required by `grass` and `python3-spdx-tools` — it arrives
  only with the GRASS component of the standalone "full" installer.

The same index confirms `python3-pypdf2` is absent from the bundle, which
independently validates dropping PyPDF2 above.

Exploiting the `future` issue also requires the attacker to already be able to
write `test.py` onto `sys.path` — i.e. they already have code execution, so it
grants no new capability.

## Follow-up 2026-11-03 — certifi emSign ECC Root CA - G3

Certifi versions before **2026.10.18** trust the `emSign ECC Root CA - G3` root.
Eight eMudhra intermediates chaining to it have compromised private keys (now
revoked), so an on-path attacker holding one could impersonate any hostname to
clients using the certifi bundle. 2026.10.18 removed all emSign roots;
**2026.10.19** restored the unaffected ones. Fixed in `>= 2026.10.19`.

The previous pin, `certifi==2026.7.22`, was affected. It is now
`certifi==2026.10.23`, the current `python3-certifi` in the OSGeo4W index
(previous release there: 2026.10.19).

**Practical exposure of the plugin is low.** All of its HTTP traffic goes through
`QNetworkAccessManager` (`gaia_client/api/requests/http_client.py`), which uses
Qt's TLS stack and the OS trust store, not certifi. Certifi matters only for
Python tooling in the QGIS environment (`requests`, `urllib3`, `pip`).

As with the other pins, the file documents the runtime; it does not change what
QGIS loads. Users need a QGIS install whose bundled certifi is >= 2026.10.19
(update via the OSGeo4W installer). The OSGeo4W index shows only the latest
package, so confirm the certifi shipped with the exact QGIS 3.44.x build you
support before relying on this pin.

## Known issue (not introduced here, not fixed here)

Three modules import from the **private** `qgis._core` / `qgis._gui` modules
rather than the public `qgis.core` / `qgis.gui`:

- `gaia_client/map/layer_handler.py`
- `gaia_client/ui/handlers/select_bounding_box.py`
- `gaia_client/use_cases/get_and_show_run_results.py`

This works on 3.44 but is unsupported API and a likely source of breakage on
future QGIS upgrades. Worth switching to the public modules.

Also: `gaia_client/ui/handlers/layer_handler.py` imports `PIL.Image` but never
uses it — that dead import is why the Pillow 11 -> 12 major bump carries no risk.
