# pylint: disable=E0611,W0611,C0103,C0303,R0903
"""
This module contains the ChatWindow class, which represents a chat window widget.
"""
import asyncio
import datetime

from PyQt5.QtWidgets import (
    QScrollArea,
    QWidget,
    QVBoxLayout,
    QLabel,
    QHBoxLayout,
    QApplication,
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QTimer
from src.config import load_config
from src.chat_bubble import ChatBubble
from src.chat_logger import ChatLogger
from src.llm import LLM


class ChatWindow(QScrollArea):
    """
    Represents a chat window widget.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.initUI()
        # Define image paths as class member variables
        self.config = load_config()
        self.avatar_dst_gpt = self.config.get("AVATAR_DST_GPT")
        self.avatar_user = self.config.get("AVATAR_USER")
        self.chatWithLLM_Demo()

    def initUI(self):
        """
        Initializes the user interface of the chat window.
        """
        self.setWidgetResizable(True)
        # Content container for the chat window
        self.chatWindowWidgetContents = QWidget()
        # Set layout on the content container
        self.chat_layout = QVBoxLayout(self.chatWindowWidgetContents)
        # Set the content container as the viewport of the chat window
        self.setWidget(self.chatWindowWidgetContents)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        current_datetime = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        self.log_filepath = f"log/chatlog_{current_datetime}.txt"
        self.chat_logger = ChatLogger(self.log_filepath)

    def chatWithLLM_Demo(self):
        """
        Demonstrates chatting with LLM.
        """
        self.addMessage("Hi! I am DST-GPT, what can I help you?", "left")

    def removeMessage(self, target_text):
        """
        Removes a message from the chat window.

        Args:
            target_text (str): The text of the message to be removed.

        Returns:
            None
        """
        bubbles_to_remove = []
        for i in range(self.chat_layout.count() - 1, -1, -1):
            layout_item = self.chat_layout.itemAt(i)
            if layout_item is not None:
                layout = layout_item.layout()
                if layout is not None:
                    bubble_widget = layout.itemAt(1).widget()
                    if (
                        isinstance(bubble_widget, ChatBubble)
                        and bubble_widget.text() == target_text
                    ):
                        bubbles_to_remove.append(layout)

        for bubble_layout in bubbles_to_remove:
            bubble_layout.setParent(None)

    def addMessage(self, text, side, tokens=0, cost=0):
        """
        Adds a message to the chat window with the avatar based on the current configuration.

        Args:
            text (str): The text of the message.
            side (str): The side of the chat window where the message should be displayed.
            tokens (int): Number of tokens used by the message (optional).
            cost (float): Cost of the message (optional).

        Returns:
            None
        """
        bubble = ChatBubble(text)
        hbox = QHBoxLayout()
        avatar = QLabel(self)

        if side == "left":
            avatar.setPixmap(
                QPixmap(self.avatar_dst_gpt).scaled(
                    100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation
                )
            )
            hbox.addWidget(avatar)
            hbox.addWidget(bubble)
        elif side == "right":
            avatar.setPixmap(
                QPixmap(self.avatar_user).scaled(
                    100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation
                )
            )
            hbox.addWidget(bubble)
            hbox.addWidget(avatar)

        hbox.setSpacing(10)
        # Align the bubble to the left or right
        hbox.setAlignment(Qt.AlignLeft if side == "left" else Qt.AlignRight)
        # Check if there is only one bubble in the chat layout
        if self.chat_layout.count() <= 1:
            self.chat_layout.setAlignment(Qt.AlignTop)

        self.chat_layout.addLayout(hbox)

        # Use QTimer.singleShot to delay the scroll bar update
        # and give time for the layout to update
        # Call scrollToBottom after 100 milliseconds
        QTimer.singleShot(100, self.scrollToBottom)

        # Add the message to the log
        self.chat_logger.add_chat_to_log(text, side, tokens, cost)
        # Update meta data in the log
        self.chat_logger.log_meta_update()

    def scrollToBottom(self):
        """
        Scrolls the chat window to the bottom.
        """
        scroll_bar = self.verticalScrollBar()
        if scroll_bar.maximum() >= scroll_bar.value():
            scroll_bar.setValue(scroll_bar.maximum())

    def update_avatar(self):
        """
        Updates the avatar paths with new values.

        Returns:
            None
        """
        self.config = load_config()
        self.avatar_dst_gpt = self.config.get("AVATAR_DST_GPT")
        self.avatar_user = self.config.get("AVATAR_USER")
