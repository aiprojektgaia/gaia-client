from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QSizePolicy,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QValidator
from gaia_client.ui.utils.safe_text import SafeLabel


class FocusLineEdit(QLineEdit):
    """
    A QLineEdit that calls a validation callback when the user focuses out of it.
    This is because the QLineEdit's focusOutEvent is not called on inputs that haven't
    been edited first.
    """

    def __init__(self, parent=None, validation_callback=None):
        super().__init__(parent)
        self.validation_callback = validation_callback

    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        if self.validation_callback:
            self.validation_callback()


class ValidatedInput(QWidget):
    def __init__(
        self,
        label_text,
        error_message="This field cannot be empty",
        text_hint=None,
        validator=None,
        parent=None,
    ):
        super().__init__(parent)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.error_message = error_message
        self.hint = text_hint
        self.input_widget = None
        self.error_label = None
        self.validator = validator

        self.setup_input(label_text)

    def setup_input(self, label_text):
        # Main vertical layout to stack input row and error message
        container_layout = QVBoxLayout()
        container_layout.setSpacing(0)
        container_layout.setContentsMargins(0, 0, 0, 0)

        # Create the input with a reference to our validation method
        self.input_widget = FocusLineEdit(
            parent=self, validation_callback=self.validate_input_on_blur
        )
        if self.hint:
            self.input_widget.setPlaceholderText(self.hint)

        # Apply validator if one was provided
        # this will apply on_change
        # TODO: This should remain uncommented, until we figure out how to do on_change validation
        # if self.validator and isinstance(self.validator, QValidator):
        #     self.input_widget.setValidator(self.validator)

        # Add label and input to the horizontal row
        if label_text:
            label = SafeLabel(label_text)
            container_layout.addWidget(label)

        container_layout.addWidget(self.input_widget)

        # Create error label with minimal height and no margins
        self.error_label = SafeLabel(self.error_message)
        self.error_label.setStyleSheet("""
            color: red;
        """)
        self.error_label.setContentsMargins(0, 0, 0, 0)
        self.error_label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
        self.error_label.hide()

        # Add the input row and error label to the container
        container_layout.addWidget(
            self.error_label, 0, Qt.AlignTop
        )  # Align to top with no stretch

        # Set the main widget's layout properties
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addLayout(container_layout)

    def validate_input_on_blur(self):
        text = self.input_widget.text().strip()
        if not text:
            self.error_label.show()
            return False

        # If we have a validator, check if the input is valid
        if self.validator:
            state, the_text, other_value = self.validator.validate(text, 0)

            if state != QValidator.Acceptable:
                self.error_label.show()
                return False

        self.error_label.hide()
        return True

    def get_value(self):
        return self.input_widget.text()

    def set_value(self, value: str):
        self.input_widget.setText(value)

    def get_input(self) -> (str, bool):
        return self.input_widget.text().strip(), self.validate_input_on_blur()

    def clear(self):
        self.input_widget.clear()
