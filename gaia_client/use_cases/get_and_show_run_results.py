import os
import time
import shutil
import zipfile

from PyQt5.QtCore import QObject, Qt
from qgis._core import QgsRasterLayer, QgsVectorLayer
from qgis.core import QgsProject
from PyQt5.QtWidgets import QProgressDialog, QApplication

from gaia_client.api.models.ProjectRun import ProjectRun as ProjectRunModel
from gaia_client.api.requests.project_run import ProjectRunApi
from gaia_client.map.layer_handler import zoom_to_layer, set_crs

from gaia_client.ui.i18n.se import (
    project_run_download_results,
    project_run_download_hint,
    settings_dialog_cancel_button,
    project_run_download_results_starting,
    project_run_download_results_unzipping,
    project_run_download_results_downloaded,
    project_run_download_results_adding_layers,
)


MAX_ARCHIVE_ENTRIES = 10_000
MAX_ARCHIVE_MEMBER_BYTES = 2 * 1024**3
MAX_ARCHIVE_TOTAL_BYTES = 4 * 1024**3
MAX_EXTRACTION_SECONDS = 10 * 60
MAX_ARCHIVE_DEPTH = 8
MAX_LAYERS = 500


class GetAndShowRunResults(QObject):
    def __init__(self, iface, project_run: ProjectRunModel, output_path: str):
        super(GetAndShowRunResults, self).__init__()
        self.iface = iface
        self.project_run = project_run
        self.output_path = output_path
        self.progress_dialog = None

    def run(self) -> bool:
        QApplication.setOverrideCursor(Qt.WaitCursor)

        # Create progress dialog
        self.progress_dialog = QProgressDialog(
            project_run_download_hint,
            settings_dialog_cancel_button,
            0,
            100,
            self.iface.mainWindow(),
        )
        self.progress_dialog.setWindowTitle(project_run_download_results)
        self.progress_dialog.setWindowModality(Qt.WindowModal)
        self.progress_dialog.setAutoClose(True)
        self.progress_dialog.setMinimumDuration(0)  # Show immediately

        file_path = extraction_path = None
        try:
            directory_path = os.path.realpath(self.output_path)
            file_name = (
                f"project-result-{int(self.project_run.project_id)}"
                f"-run-{int(self.project_run.id)}"
            )
            # Never reuse an existing file or directory: pick the first free name.
            suffix = ""
            counter = 1
            while any(
                os.path.lexists(os.path.join(directory_path, file_name + suffix + ext))
                for ext in ("", ".zip")
            ):
                counter += 1
                suffix = f"-{counter}"
            file_path = self._contained_path(directory_path, file_name + suffix + ".zip")
            extraction_path = self._contained_path(directory_path, file_name + suffix)

            # streamed straight to disk, never held in memory
            if not self.fetch_run_results(file_path):
                print("Error occurred while fetching run results")
                self._remove(file_path, None)
                return False

            self.progress_dialog.setValue(50)
            self.progress_dialog.setLabelText(project_run_download_results_unzipping)
            self.unzip_qfile(file_path, output_folder=extraction_path)
            set_crs(self.iface, self.project_run.get_coordinate_system())

            self.progress_dialog.setValue(70)
            self.progress_dialog.setLabelText(project_run_download_results_adding_layers)
            self.add_files_as_layers(extraction_path, group_name=self.project_run.name)
            self.progress_dialog.setValue(100)
            return True
        except Exception:
            # do not leave a partial download or extraction behind
            self._remove(file_path, extraction_path)
            raise
        finally:
            self.progress_dialog.close()
            QApplication.restoreOverrideCursor()

    @staticmethod
    def _remove(file_path, extraction_path):
        if extraction_path:
            shutil.rmtree(extraction_path, ignore_errors=True)
        if file_path and os.path.isfile(file_path):
            try:
                os.remove(file_path)
            except OSError:
                pass

    def fetch_run_results(self, file_path: str) -> bool:
        project_run_api = ProjectRunApi()

        self.progress_dialog.setValue(10)
        self.progress_dialog.setLabelText(project_run_download_results_starting)

        ok = project_run_api.get_run_results_as_zip(
            self.project_run.id,
            file_path,
            # Cancel aborts the transfer
            on_started=lambda client: self.progress_dialog.canceled.connect(client.abort),
        )
        self.progress_dialog.setValue(30)
        self.progress_dialog.setLabelText(project_run_download_results_downloaded)
        return ok

    @staticmethod
    def _contained_path(root: str, name: str) -> str:
        """Resolve root/name and refuse anything that is not a direct child of root."""
        root = os.path.realpath(root)
        path = os.path.realpath(os.path.join(root, name))
        if os.path.dirname(path) != root:
            raise ValueError("Refusing to write outside the selected directory")
        return path

    @staticmethod
    def _check_archive_limits(zip_file, target_dir: str):
        """Bound entry count, sizes and depth, and require free disk space.

        No compression-ratio check: result rasters are mostly zeros and
        legitimately compress up to ~1000:1. Zip bombs are stopped by the size
        limits, which unzip_qfile enforces on the bytes actually written."""
        entries = zip_file.infolist()
        if len(entries) > MAX_ARCHIVE_ENTRIES:
            raise ValueError("Archive has too many entries")
        total = 0
        for info in entries:
            total += info.file_size
            if info.file_size > MAX_ARCHIVE_MEMBER_BYTES or total > MAX_ARCHIVE_TOTAL_BYTES:
                raise ValueError("Archive is too large when unpacked")
            if info.filename.count("/") > MAX_ARCHIVE_DEPTH:
                raise ValueError("Archive is nested too deeply")
        if shutil.disk_usage(target_dir).free < total * 2:
            raise ValueError("Not enough free disk space to unpack the archive")

    @staticmethod
    def unzip_qfile(input_file: str, output_folder: str):
        root_dir = os.path.dirname(os.path.realpath(output_folder))
        deadline = time.monotonic() + MAX_EXTRACTION_SECONDS
        with zipfile.ZipFile(input_file) as zip_file:
            GetAndShowRunResults._check_archive_limits(zip_file, root_dir)

            # Extract into a fresh directory only, so existing files can never
            # be overwritten, and reject members that resolve outside it.
            os.makedirs(output_folder, exist_ok=False)
            root = os.path.realpath(output_folder)
            written = 0
            for member in zip_file.infolist():
                target = os.path.realpath(os.path.join(root, member.filename))
                if target != root and not target.startswith(root + os.sep):
                    raise ValueError(f"Unsafe path in archive: {member.filename}")
                if member.is_dir():
                    os.makedirs(target, exist_ok=True)
                    continue
                os.makedirs(os.path.dirname(target), exist_ok=True)
                # Count the bytes actually written rather than trusting the
                # sizes declared in the archive headers.
                with zip_file.open(member) as src, open(target, "xb") as dst:
                    while chunk := src.read(1024 * 1024):
                        written += len(chunk)
                        if written > MAX_ARCHIVE_TOTAL_BYTES:
                            raise ValueError("Archive is too large when unpacked")
                        if time.monotonic() > deadline:
                            raise TimeoutError("Unpacking the archive took too long")
                        dst.write(chunk)
                QApplication.processEvents()

    @staticmethod
    def _looks_like(path: str, kind: str) -> bool:
        """Check the file's magic bytes so a renamed GDAL dataset (VRT, a
        /vsicurl reference, ...) is never opened just because of its suffix."""
        with open(path, "rb") as f:
            head = f.read(16)
        if kind == "tif":
            return head[:4] in (b"II*\x00", b"MM\x00*", b"II+\x00", b"MM\x00+")
        if kind == "gpkg":
            return head == b"SQLite format 3\x00"
        return False

    def add_files_as_layers(self, extraction_path, group_name="Project Results"):
        project_instance = QgsProject.instance()
        root = project_instance.layerTreeRoot()
        base_group = root.insertGroup(0, group_name)
        group_dictionary = {
            "geopackage": base_group.insertGroup(0, "GeoPackages"),
            "result": base_group.insertGroup(1, "Merged"),
            "bit": base_group.insertGroup(2, "With Confidence"),
            "seg": base_group.insertGroup(2, "Segmentation"),
            "tile": base_group.insertGroup(3, "Tile"),
        }

        # Add the files as layers
        for file in sorted(os.listdir(extraction_path))[:MAX_LAYERS]:
            full_path = os.path.join(extraction_path, file)
            if os.path.islink(full_path) or not os.path.isfile(full_path):
                continue
            if file.endswith(".tif") and not self._looks_like(full_path, "tif"):
                print(f"{file} is not a TIFF file - skipped")
                continue
            if file.endswith(".gpkg") and not self._looks_like(full_path, "gpkg"):
                print(f"{file} is not a GeoPackage - skipped")
                continue
            if file.endswith(".tif"):
                print(f"{file} added to the group images")
                # magic bytes verified above, so GDAL opens it as a TIFF
                layer = QgsRasterLayer(full_path, file)
                # layer = QgsVectorLayer(os.path.join(extraction_path, file), file, 'ogr')
                project_instance.addMapLayer(layer, False)
                if file.startswith("tile"):
                    group_dictionary["tile"].addLayer(layer)
                elif file.startswith("bit"):
                    layer_tree_group = group_dictionary["bit"].addLayer(layer)
                    # hiding the layer
                    layer_tree_group.setItemVisibilityChecked(False)
                elif file.startswith("seg"):
                    group_dictionary["seg"].addLayer(layer)
                elif file.startswith("result"):
                    layer_tree_group = group_dictionary["result"].addLayer(layer)
                    layer_tree_group.setItemVisibilityChecked(False)
            elif file.endswith(".gpkg"):
                print(f"{file} added to the group GeoPackages")
                layer = QgsVectorLayer(full_path, file, "ogr")
                project_instance.addMapLayer(layer, False)
                group_dictionary["geopackage"].addLayer(layer)
                # zoom to the layer
                zoom_to_layer(self.iface, layer)

        print("Layers added to the project")

    @staticmethod
    def hide_layer(layer):
        project_instance = QgsProject.instance()
        layer_tree = project_instance.layerTreeRoot()
        layer_node = layer_tree.findLayer(layer.id())
        if layer_node:
            layer_node.setItemVisibilityChecked(False)
