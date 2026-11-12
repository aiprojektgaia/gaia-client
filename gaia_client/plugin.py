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

# plugin.py
import os
from PyQt5.QtWidgets import QAction
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
from gaia_client.ui.utils.window_utils import Singleton, WindowUtils
from .ui.main_dialog import MainDockWidget  # Updated import


class GaiaClientPlugin:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
                      which provides the hook by which you can manipulate the
                      QGIS application at run time.
        """
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        self.action = None
        self.dock_widget = None  # Renamed from dlg to dock_widget
        self.window_utils = None

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""
        icon_path = os.path.join(self.plugin_dir, "ui", "static", "gaia_logo.svg")
        if not os.path.exists(icon_path):
            print(f"Icon file does not exist: {icon_path}")
        else:
            print(f"Icon file found: {icon_path}")

        icon = QIcon(icon_path)
        self.action = QAction(icon, "Gaia Client", self.iface.mainWindow())
        self.action.triggered.connect(self.run)
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu("&Gaia Client", self.action)

    def unload(self):
        """Remove everything the plugin added to QGIS. Each step runs even if
        an earlier one fails, so disabling the plugin never leaves its dock
        or status polling behind."""
        steps = [
            lambda: self.iface.removePluginMenu("&Gaia Client", self.action),
            lambda: self.iface.removeToolBarIcon(self.action),
        ]
        if self.dock_widget is not None:
            dock = self.dock_widget
            steps += [
                dock.shutdown,
                lambda: self.iface.removeDockWidget(dock),
                dock.close,
                dock.deleteLater,
            ]
        if self.action is not None:
            steps.append(self.action.deleteLater)
        # plugin-owned singletons (router, window utils, stores) start fresh
        steps.append(Singleton._instances.clear)

        for step in steps:
            try:
                step()
            except Exception as e:
                print(f"Error while unloading the GAIA plugin: {e}")

        self.dock_widget = None
        self.action = None
        self.window_utils = None

    def run(self):
        """Run method that performs all the real work."""
        try:
            # Instantiate WindowUtils singleton with iface
            self.window_utils = WindowUtils(iface=self.iface)
        except ValueError as e:
            print(e)
            return

        if self.dock_widget is None:
            # Create the dock_widget (after translation) and keep reference
            self.dock_widget = MainDockWidget(self.iface)
            # Add the dock_widget to the QGIS interface on the right side
            self.iface.addDockWidget(Qt.RightDockWidgetArea, self.dock_widget)
        else:
            # If the dock_widget already exists, bring it to the front
            self.dock_widget.raise_()

        self.dock_widget.show()
