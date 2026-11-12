# Copyright (C) 2024-2026 Decerno AB
#
# This file is part of the GAIA QGIS client plugin.
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# this program. If not, see <https://www.gnu.org/licenses/>.

import os
from qgis.PyQt.QtWidgets import QMessageBox

def classFactory(iface):
    metadata_file = os.path.join(os.path.dirname(__file__), 'metadata.txt')
    if not os.path.exists(metadata_file):
        QMessageBox.critical(None, "Error", "Missing metadata file")
        return None

    from .plugin import GaiaClientPlugin
    return GaiaClientPlugin(iface)
