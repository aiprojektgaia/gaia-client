"""Display helpers for text that may come from the backend.

Qt guesses whether a label, tooltip or message box string is HTML. Project and
run names come from the server, so a name such as "<b>Delete ALL</b>" or one
with links/images would otherwise be rendered as rich text. Everything here is
shown as plain text and length-limited.
"""

import html

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel, QMessageBox

MAX_DISPLAY_LENGTH = 2000


def clip(text) -> str:
    text = "" if text is None else str(text)
    if len(text) > MAX_DISPLAY_LENGTH:
        return text[:MAX_DISPLAY_LENGTH] + "…"
    return text


class SafeLabel(QLabel):
    """QLabel that never interprets its text as HTML."""

    def __init__(self, text="", parent=None):
        super().__init__(parent)
        self.setTextFormat(Qt.PlainText)
        self.setText(text)

    def setText(self, text):
        super().setText(clip(text))


def safe_tooltip(text) -> str:
    """Tooltips have no plain-text switch, so escape instead."""
    return html.escape(clip(text))


def ask_yes_no(parent, title: str, text: str) -> bool:
    box = QMessageBox(parent)
    box.setIcon(QMessageBox.Question)
    box.setWindowTitle(clip(title))
    box.setTextFormat(Qt.PlainText)
    box.setText(clip(text))
    box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
    box.setDefaultButton(QMessageBox.No)
    return box.exec() == QMessageBox.Yes


def show_plain_warning(parent, text: str, title: str = "GAIA") -> None:
    box = QMessageBox(parent)
    box.setIcon(QMessageBox.Warning)
    box.setWindowTitle(clip(title))
    box.setTextFormat(Qt.PlainText)
    box.setText(clip(text))
    box.exec()
