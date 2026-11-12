# Security policy

## Reporting a vulnerability

**This repository is not maintained**

This code is provided as-is under its licence, with no maintainer. Vulnerability
reports will not be received, triaged or fixed. Anyone who deploys or forks this
code is solely responsible for its security, including keeping dependencies
patched.

## Scope

This repository contains the QGIS plugin. It runs on an
operator workstation inside QGIS and talks to a GAIA server over HTTP.

The most security-relevant surfaces are:

* **The stored API key.** Held in `QgsSettings` under `gaia-plugin/gaia_api_key`
  as plain text, like the backend URL. It is a shared server secret, not a
  per-user credential.
* **Transport.** The plugin sends the API key only over HTTPS, or over plain
  `http://` to a literal loopback/private IP address (or `localhost`). Plain
  HTTP to a hostname is refused, because a DNS answer can change between the
  check and the connection. Redirects are never followed. Rotate any key that has previously been used over untrusted HTTP.
* **Downloaded results.** Run results are ZIP archives extracted locally and
  loaded as QGIS layers.

## Deployment security

GAIA is deployed as a whole. The hardening guidance for a running installation —
API key, exposed ports, TLS, GeoServer credentials — lives with the backend:

**[gaia-backend/SECURITY.md](https://github.com/aiprojektgaia/gaia-backend/blob/main/SECURITY.md)**

Read it before putting any part of GAIA on a network.

## Known limitations

* The plugin cannot patch its own dependencies. It uses the
  Python libraries inside QGIS, so fixing a vulnerability in Pillow or urllib3
  means upgrading QGIS — the supported baseline is **QGIS 3.44 LTR**.
* The API key is stored unencrypted in the QGIS user profile.
* There is a single shared key for all users; it cannot identify who did what.

## Audit history

Dependency vulnerabilities and their dispositions, including confirmed false
positives, are recorded in [docs/security-fixes-260817.md](docs/security-fixes-260817.md).
