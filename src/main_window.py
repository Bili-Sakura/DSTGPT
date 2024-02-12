# pylint: disable=E0611,W0611,C0103,C0303,R0903,W0201
"""
This module represents the main window GUI using PyQt5.
"""
import asyncio
import functools
from qasync import QEventLoop, asyncSlot
from langchain_community.callbacks import get_openai_callback, openai_info
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QScrollBar, QLabel
from PyQt5.QtGui import QPixmap, QPalette, QBrush, QImage, QPainter, QColor
from PyQt5.QtCore import Qt, QTimer
from src.chat_window import ChatWindow
from src.input_line import InputLine
from src.llm import LLM
from config import global_variables as GLOBAL


class MainWindow(QWidget):
    """
    Represents the main window GUI using PyQt5.
    """

    def __init__(self):
        super().__init__()
        self.initUI()
        # Create an instance of LLM class
        self.llm = LLM(
            corpus_filepath=GLOBAL.COURPUS_FILEPATH, base_model=GLOBAL.BASE_MODEL
        )

    def initUI(self):
        """
        Initializes the user interface of the main window.
        """
        self.setWindowTitle("DST-GPT")
        self.setFixedSize(1820, 1024)

        self.createChatWindow()
        self.createLabels()
        self.createInputLine()
        self.createLayout()
        self.setBackgroundImage()

    def createChatWindow(self):
        """
        Creates and initializes the chat window widget.
        """
        self.chatWindow = ChatWindow(self)
        self.chatWindow.setFixedSize(1700, 700)
        self.chatWindow.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.chatWindow.setStyleSheet("background-color: rgba(255, 255, 255, 0.5);")

    def createLabels(self):
        """
        Creates and initializes the description label widget.
        """
        text_header = (
            "     DST-GPT: Start Chatting with a Don't Starve(Together) Expert!"
        )
        self.headerLabel = QLabel("label_header")
        self.headerLabel.setText(text_header)
        self.headerLabel.setStyleSheet(
            "font-weight: bold; font-size: 48px; text-align: center; color: white; font-family: 'Microsoft YaHei';"
        )

        text_description = " Ctrl + Enter: Switch to a new line in input box.\n\tEnter: Send a message to chat with DST-GPT."
        self.descriptionLabel = QLabel("label_description")
        self.descriptionLabel.setText(text_description)
        self.descriptionLabel.setStyleSheet(
            "font-weight: bold; font-size: 24px; background-color: rgba(255, 255, 255, 0.6); padding: 10px;"
        )

    def createInputLine(self):
        """
        Creates and initializes the input line widget.
        """
        self.input_line = InputLine()
        self.input_line.returnPressed.connect(self.onReturnPressed)
        self.input_line.setPlaceholderText("Message DST-GPT...")

    def createLayout(self):
        """
        Creates and initializes the layout for the main window.
        """
        self.layout = QVBoxLayout()
        # Align the layout to the center
        self.layout.setAlignment(Qt.AlignCenter)

        vertical_layout = QVBoxLayout()
        # Align the vertical layout to the center
        vertical_layout.setAlignment(Qt.AlignCenter)
        vertical_layout.addWidget(self.headerLabel)
        vertical_layout.addWidget(self.chatWindow)
        vertical_layout.addWidget(self.descriptionLabel)
        vertical_layout.addWidget(self.input_line)

        self.layout.addStretch()
        self.layout.addLayout(vertical_layout)
        self.layout.addStretch()

        self.setLayout(self.layout)

    def setBackgroundImage(self):
        """
        Sets the background image of the main window.
        """
        self.setAutoFillBackground(True)
        pixmap = QPixmap("assets/BG.png")
        image = pixmap.toImage()
        background = QPixmap.fromImage(image)
        palette = self.palette()
        palette.setBrush(self.backgroundRole(), QBrush(background))
        self.setPalette(palette)

    @asyncSlot()
    async def onReturnPressed(self):
        """
        Handles the event when the return key is pressed
        in the input line.
        """
        user_text = self.input_line.toPlainText()
        self.askLLM(user_text)
        self.input_line.clear()
        await self.getLLMAnswer(user_text)

    def askLLM(self, user_text):
        """
        Adds the user's text to the chat window on the right side
        and displays a "Thinking..." message on the left side.
        """
        self.chatWindow.addMessage(user_text, "right")
        self.chatWindow.addMessage("Thinking...", "left")

    async def getLLMAnswer(self, user_text):
        """
        Retrieves the answer from LLM asynchronously.

        Args:
            user_text (str): The user's input text.

        Returns:
            str: The answer to the question.
        """
        with get_openai_callback() as cb:
            llm_answer = await self.llm.get_answer_async(user_text)
            tokens = cb.total_tokens
            cost = cb.total_cost

        self.chatWindow.addMessage(llm_answer, "left", tokens, cost)

        return llm_answer
