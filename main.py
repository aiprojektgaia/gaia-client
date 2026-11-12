"""
This is not the real main file for the plugin, but only used to start up
a basic PyQt window with zero support for QGIS functionality.

It can only be used to play with layouting and basic PyQt widgets.
"""

from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QMessageBox
from PyQt5.QtCore import Qt


# Only needed for access to command line arguments
import sys


from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout

from gaia_client.test.test_view import TestView


# You need one (and only one) QApplication instance per application.
# Pass in sys.argv to allow command line arguments for your app.
# If you know you won't use command line arguments QApplication([]) works too.

app = QApplication(sys.argv)
# Create a Qt widget, which will be our window.
window = QWidget()
window.setWindowTitle("Gaia Test View")
window.resize(1920, 1080)

# Create main horizontal layout
main_layout = QHBoxLayout()

# Create left section (80% width) with QGIS placeholder
left_widget = QWidget()
left_widget.setStyleSheet(
    "border-right: 2px solid black;"
)  # Add border to the right side
left_layout = QVBoxLayout()
qgis_label = QLabel("QGIS Placeholder")
qgis_label.setAlignment(Qt.AlignCenter)
left_layout.addWidget(qgis_label)
left_widget.setLayout(left_layout)

# Create right section (20% width) with TestView
right_widget = QWidget()
right_layout = QVBoxLayout()
test_view = TestView(window)
right_layout.addWidget(test_view.get_widget())
right_widget.setLayout(right_layout)

# Add widgets to main layout with size constraints
main_layout.addWidget(left_widget, stretch=80)
main_layout.addWidget(right_widget, stretch=20)

window.setLayout(main_layout)
window.show()

# QMessageBox.critical(
#     None,
#     "Något gick fel",
#     "Det gick inte att skapa projektet, försök igen om några minuter.",
# )

# Start the event loop.
app.exec()
