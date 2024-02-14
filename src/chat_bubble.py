# pylint: disable=E0611,W0611,C0103,C0303,R0903
"""
This module provides a chat bubble widget for displaying text messages.
"""
from PyQt5.QtWidgets import QLabel, QWidget, QVBoxLayout, QSizePolicy
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt


class ChatBubble(QWidget):
    """
    Represents a chat bubble widget for displaying text messages.
    """

    def __init__(self, text, parent=None):
        super(ChatBubble, self).__init__(parent)
        self.text = text

        self.initUI()

    def initUI(self):
        """
        Initializes the user interface for the chat bubble widget.
        """
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        label = QLabel(self.text)
        label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        label.setWordWrap(True)
        label.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        layout.addWidget(label)

        label.setStyleSheet(
            "QLabel {"
            "font-weight: bold; "
            "font-size: 30px; "
            "background-color: rgba(255, 255, 255, 0.6);"
            "margin: 0px; padding: 8px; border-radius: 5px;"
            "}"
        )

        self.setStyleSheet(
            "ChatBubble {"
            "background-color: lightgrey; "
            "color: black; "
            "padding: 0px; "
            "border-radius: 10px; "
            "}"
        )
        self.adjustSize()  # Adjust the size of the chat bubble to fit the contents
