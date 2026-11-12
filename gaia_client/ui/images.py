from pathlib import Path
from PyQt5.QtGui import QIcon

image_path = Path(__file__).parent / "static"
gaia_logo_svg_icon = QIcon(str(image_path / "gaia_logo.svg"))
gaia_logo_svg = str(image_path / "gaia_logo.svg")
gaia_logo_png = str(image_path / "gaia_logo.png")
