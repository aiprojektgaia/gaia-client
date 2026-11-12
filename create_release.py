#!/usr/bin/env python3
"""
Script to create a zipped release of the QGIS plugin.

The archive is laid out the way QGIS "Install from ZIP" expects: a single
top-level directory named after the plugin package, containing metadata.txt.
QGIS extracts the whole archive straight into the profile's plugins folder, so
anything left at the archive root would be dropped loose next to the other
installed plugins - hence the supporting files are packaged inside the plugin
directory rather than beside it.
"""

import os
import shutil
import stat
import subprocess
import zipfile
from datetime import datetime
import sys

# Plugin package that holds metadata.txt - becomes the archive root.
PLUGIN_DIR = "gaia_client"

# Repository files shipped inside the plugin directory.
# LICENSE is required: the plugin is GPL-3.0-or-later, and the licence must
# accompany every distributed copy.
EXTRA_FILES = ["LICENSE", "README.md", "requirements.txt"]

# Never shipped: development-only sources and build artefacts.
EXCLUDE_DIRS = {"test", "__pycache__", ".pytest_cache"}
EXCLUDE_SUFFIXES = (".pyc", ".pyo", ".pyd")


def read_metadata(path):
    """Parse metadata.txt into a dict, tolerating '=' inside values."""
    metadata = {}
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("[") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            metadata[key.strip()] = value.strip()
    return metadata


def tracked_files():
    """Paths (repo-relative, '/'-separated) tracked by Git. Only these may ship,
    so ignored or untracked local files (keys, .env, scratch) can never leak."""
    out = subprocess.run(["git", "ls-files", "-z"], check=True,
                         capture_output=True).stdout
    return {p for p in out.decode("utf-8").split("\0") if p}


def require_regular_tracked(path, tracked):
    """Reject symlinks and other non-regular files, and anything not tracked."""
    mode = os.lstat(path).st_mode
    if not stat.S_ISREG(mode):
        raise SystemExit(f"Error: {path} is not a regular file (symlink?); refusing to package it")
    if path.replace(os.sep, "/") not in tracked:
        raise SystemExit(f"Error: {path} is not tracked by Git; refusing to package it")


def copy_plugin_tree(src, dst, tracked):
    """Copy the plugin package, skipping dev-only files and artefacts."""
    copied = 0
    for root, dirs, files in os.walk(src):
        dirs[:] = sorted(d for d in dirs if d not in EXCLUDE_DIRS)
        for d in dirs:
            if os.path.islink(os.path.join(root, d)):
                raise SystemExit(f"Error: {os.path.join(root, d)} is a symlink; refusing to package it")
        rel_path = os.path.relpath(root, src)
        target_dir = os.path.join(dst, rel_path) if rel_path != "." else dst
        os.makedirs(target_dir, exist_ok=True)
        for file in sorted(files):
            if file.endswith(EXCLUDE_SUFFIXES):
                continue
            source = os.path.join(root, file)
            require_regular_tracked(source, tracked)
            shutil.copy2(source, os.path.join(target_dir, file), follow_symlinks=False)
            copied += 1
    return copied


def create_release():
    metadata_path = os.path.join(PLUGIN_DIR, "metadata.txt")
    if not os.path.exists(metadata_path):
        print("Error: metadata.txt not found!")
        sys.exit(1)

    metadata = read_metadata(metadata_path)
    plugin_name = metadata.get("name", PLUGIN_DIR)
    version = metadata.get("version", "0.0.0")
    qgis_min = metadata.get("qgisMinimumVersion", "?")

    current_date = datetime.now().strftime("%Y%m%d")
    zip_filename = f"{plugin_name}_{version}_{current_date}.zip"

    releases_dir = "release"
    os.makedirs(releases_dir, exist_ok=True)

    # Staging directory; the archive root is the plugin package itself.
    staging_dir = f"{plugin_name}_{version}_build"
    if os.path.exists(staging_dir):
        shutil.rmtree(staging_dir)
    plugin_root = os.path.join(staging_dir, PLUGIN_DIR)
    os.makedirs(plugin_root)

    tracked = tracked_files()
    copied = copy_plugin_tree(PLUGIN_DIR, plugin_root, tracked)

    for item in EXTRA_FILES:
        if os.path.exists(item):
            require_regular_tracked(item, tracked)
            shutil.copy2(item, os.path.join(plugin_root, item))
            copied += 1
        else:
            print(f"Warning: {item} not found, skipping")

    zip_path = os.path.join(releases_dir, zip_filename)
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(staging_dir):
            dirs[:] = sorted(dirs)
            for file in sorted(files):
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, staging_dir)
                zipf.write(file_path, arcname)

    # verify the archive holds exactly the expected, contained entries
    with zipfile.ZipFile(zip_path) as zipf:
        for name in zipf.namelist():
            if name.startswith("/") or ".." in name.split("/") \
                    or not name.startswith(PLUGIN_DIR + "/"):
                raise SystemExit(f"Error: unexpected entry in archive: {name}")

    shutil.rmtree(staging_dir)

    print(f"Release created successfully: {zip_path}")
    print(f"Plugin: {plugin_name}")
    print(f"Version: {version}")
    print(f"QGIS minimum version: {qgis_min}")
    print(f"Files packaged: {copied}")
    print(f"Date: {current_date}")


if __name__ == "__main__":
    create_release()
