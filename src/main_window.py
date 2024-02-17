# pylint: disable=E0611,W0611,C0103,C0303,R0903,W0201,C0301
"""
This module represents the main window GUI using PyQt5.
"""
import asyncio
import functools
import re
import os
from dotenv import set_key, find_dotenv
from qasync import QEventLoop, asyncSlot
from langchain_community.callbacks import get_openai_callback, openai_info
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QScrollBar,
    QLabel,
    QMenuBar,
    QStatusBar,
    QActionGroup,
    QAction,
    QFileDialog,
    QMessageBox,
    QDialog,
    QGridLayout,
    QPushButton,
)
from PyQt5.QtGui import QPixmap, QPalette, QBrush, QImage, QPainter, QColor
from PyQt5.QtCore import Qt, QTimer
from src.menu_manager import MenuManager
from src.chat_window import ChatWindow
from src.input_line import InputLine
from src.llm import LLM
from src.config import load_config, update_config, configUpdater
from src.apikey_window import ApiKeyDialog
from src.prompt_window import PromptInputDialog


class MainWindow(QMainWindow):
    """
    Represents the main window GUI using PyQt5.
    """

    def __init__(self):
        super().__init__()
        self.config = load_config()
        configUpdater.configChanged.connect(self.displayConfigInfo)
        self.initUI()

        # Create an instance of LLM class
        self.llm = LLM()

    def closeEvent(self, event):
        """
        This method is called when the main window is closed.
        It quits the application.
        """
        QApplication.quit()

    def initUI(self):
        """
        Initializes the user interface of the main window.
        """
        self.setWindowTitle("DST-GPT")
        self.setFixedSize(1820, 1024)
        self.createMenus()
        self.createStatusBar()
        self.createChatWindow()
        self.createLabels()
        self.createInputLine()
        self.createLayout()
        self.setBackgroundImage()

    def createMenus(self):
        """
        Creates and initializes the menus for the main window.
        """
        self.menuManager = MenuManager(self.menuBar(), self)
        self.menuManager.createCheckableMenu(
            "Base Model",
            [
                (
                    "gpt-3.5-turbo-0125:Default",
                    self.config.get("BASE_MODEL") == "gpt-3.5-turbo-0125",
                ),
                (
                    "gpt-3.5-turbo-16k-0613",
                    self.config.get("BASE_MODEL") == "gpt-3.5-turbo-16k-0613",
                ),
                ("gpt-3.5-turbo", self.config.get("BASE_MODEL") == "gpt-3.5-turbo"),
            ],
        )
        self.menuManager.createCheckableMenu(
            "Temperature",
            [
                ("0: Deterministic", self.config.get("TEMPERATURE") == 0),
                ("0.7: Default", self.config.get("TEMPERATURE") == 0.7),
                ("1: Creative", self.config.get("TEMPERATURE") == 1),
            ],
        )
        self.menuManager.createActionMenu(
            "API Key",
            [
                ("Set API Key", self.setAPIKey),
            ],
        )
        self.menuManager.createActionMenu(
            "Vectorstore",
            [
                ("Initialize Vectorstore", self.initializeVectorstore),
                ("Add Corpus to Vectorstore", self.addCorpusToVectorstore),
                ("Clear Vectorstore", self.clearVectorstore),
            ],
        )
        self.menuManager.createActionMenu(
            "Prompt Template",
            [
                (
                    "Use Weak Prompt",
                    lambda: self.setPromptTemplate(template_type="weak"),
                ),
                (
                    "Use Strong Prompt:Default",
                    lambda: self.setPromptTemplate(template_type="default"),
                ),
                (
                    "Self-Defined Prompt",
                    lambda: self.setPromptTemplate(template_type="self-defined"),
                ),
            ],
        )
        self.menuManager.createActionMenu(
            "Icons",
            [
                ("Change User Icon", self.changeUserIcon),
                ("Change Model Icon", self.changeModelIcon),
            ],
        )
        self.menuManager.createCheckableMenu(
            "RAG",
            [
                (
                    "Enabled:Default",
                    self.config.get("RAG") == "enabled",
                ),
                (
                    "Disabled",
                    self.config.get("RAG") == "disabled",
                ),
                (
                    "Both:Compare Mode",
                    self.config.get("RAG") == "both",
                ),
            ],
        )
        self.menuManager.createCheckableMenu(
            "Log",
            [
                (
                    "Enabled:Default",
                    self.config.get("LOG") == "enabled",
                ),
                (
                    "Disabled",
                    self.config.get("LOG") == "disabled",
                ),
            ],
        )

    def handleMenuSelection(self):
        """
        Handles the selection of a menu item.
        """
        action = self.sender()
        if action:
            menuName = action.property("menuName")
            actionText = action.text()

            if menuName == "Base Model":
                model_name = actionText.split(":")[0]
                update_config("BASE_MODEL", model_name)
            elif menuName == "Temperature":
                temperature = actionText.split(":")[0]
                update_config("TEMPERATURE", float(temperature))

            elif menuName == "RAG":
                rag_status = actionText.split(":")[0].lower()
                update_config("RAG", rag_status)

            elif menuName == "Log":
                log_status = actionText.split(":")[0].lower()
                update_config("LOG", log_status)

    def setAPIKey(self):
        """
        Opens a dialog to allow the user to set the API Key.
        """
        apikey_dialog = ApiKeyDialog()
        api_key, base_url = apikey_dialog.setAPIKey()
        dotenv_path = find_dotenv()
        if api_key != "":
            set_key(dotenv_path, "OPENAI_API_KEY", api_key)
        if base_url != "":
            set_key(dotenv_path, "OPENAI_BASE_URL", base_url)

    def initializeVectorstore(self):
        """
        Opens a file dialog to allow the user to select a parent directory to create a new vectorstore.
        """
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        while True:
            directory = QFileDialog.getExistingDirectory(
                self, "Select Directory", options=options
            )
            if directory:
                vectorstore_directory = os.path.relpath(directory)
                vectorstore_filepath = os.path.join(
                    vectorstore_directory, "chroma.sqlite3"
                )
                if os.path.exists(vectorstore_filepath):
                    confirm = QMessageBox.question(
                        self,
                        "Confirm Overwrite",
                        "Already existing a database. Confirm to overwrite it?",
                        QMessageBox.Yes | QMessageBox.No,
                    )
                    if confirm == QMessageBox.Yes:
                        self.llm.init_vectorstore(vectorstore_directory)
                        update_config("VECTORSTORE_FILEPATH", vectorstore_filepath)
                        update_config("VECTORSTORE_DIRECTORY", vectorstore_directory)

                        break
                else:
                    self.llm.init_vectorstore(vectorstore_directory)
                    update_config("VECTORSTORE_FILEPATH", vectorstore_filepath)
                    update_config("VECTORSTORE_DIRECTORY", vectorstore_directory)

                    break
            else:
                break

    def addCorpusToVectorstore(self):
        """
        Opens a file dialog to allow the user to select a new source and updates the vectorstore.
        """
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(
            self,
            "Select Source File",
            "",
            "Source Files (*.txt *.json *.md *.py *.lua)",
            options=options,
        )
        if fileName:
            source_path = os.path.relpath(fileName)
            file_type = os.path.splitext(source_path)[1]
            self.llm.update_vectorstore(source_path, file_type)

    def clearVectorstore(self):
        """
        Clears the vectorstore by deleting the existing database if it exists.
        """
        vectorstore_filepath = self.config.get("VECTORSTORE_FILEPATH")
        if os.path.exists(vectorstore_filepath):
            confirm = QMessageBox.question(
                self,
                "Confirm Clear",
                "Confirm to Delete the Existing Database?",
                QMessageBox.Yes | QMessageBox.No,
            )
            if confirm == QMessageBox.Yes:
                os.remove(vectorstore_filepath)
                QMessageBox.information(
                    None, "File Deleted", "Database has been deleted."
                )
                update_config("VECTORSTORE_FILEPATH", "")
                update_config("VECTORSTORE_DIRECTORY", "")
                update_config("KNOWLEDGE_SOURCES", [])
        else:
            QMessageBox.information(None, "File Not Found", "The file does not exist.")

    def changeUserIcon(self):
        """
        Opens a file dialog to allow the user to select a new icon and updates the user icon configuration.
        """
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(
            self,
            "Select Image File",
            "",
            "Image Files (*.png *.jpg *.jpeg *.bmp)",
            options=options,
        )
        if fileName:
            relative_path = os.path.relpath(fileName)
            update_config("AVATAR_USER", relative_path)
            self.chatWindow.update_avatar()

    def changeModelIcon(self):
        """
        Opens a file dialog to allow the user to select a new icon and updates the model icon configuration.
        """
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(
            self,
            "Select Image File",
            "",
            "Image Files (*.png *.jpg *.jpeg *.bmp)",
            options=options,
        )
        if fileName:
            relative_path = os.path.relpath(fileName)
            update_config("AVATAR_DST_GPT", relative_path)
            self.chatWindow.update_avatar()

    def setPromptTemplate(self, template_type):
        """
        Sets the prompt template based on the specified type.

        Args:
            type (str): The type of prompt template to set.

        Returns:
            None
        """
        if template_type == "weak":
            new_template = (
                "Answer the following question: \n"
                "Question: {input}\n"
                "Pay close attention to the chat context. The provided knowledge is also supported. \n"
                "<knowledge>\n"
                "{context}\n"
                "</knowledge>"
            )

        elif template_type == "default":
            new_template = (
                "Answer the following question based on the provided knowledge: \n"
                "<knowledge>\n"
                "{context}\n"
                "</knowledge>\n"
                "Question: {input}"
            )
        elif template_type == "self-defined":
            dialog = PromptInputDialog()
            if dialog.exec_() == QDialog.Accepted:
                new_template = dialog.getNewTemplate()

        else:
            raise ValueError(f"Invalid prompt template type: {template_type}")

        update_config("PROMPT_TEMPLATE", new_template)
        update_config("TEMPLATE_TYPE", template_type)

    def createStatusBar(self):
        """
        Creates and initializes the status bar.
        """
        self.statusbar = self.statusBar()
        self.statusbar.setStyleSheet(
            "background-color: rgba(255, 255, 255, 0.8);color: black"
        )
        self.displayConfigInfo()

    def createChatWindow(self):
        """
        Creates and initializes the chat window widget.
        """
        self.chatWindow = ChatWindow(self)
        self.chatWindow.setFixedSize(1700, 700)
        self.chatWindow.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.chatWindow.setStyleSheet("background-color: rgba(255, 255, 255, 0.5);")
        # self.chatWindow.chatWithLLM_Demo()
        self.chatWindow.addMessage("Hi! I am DST-GPT, what can I help you?", "left")

        # Create the four buttons
        buttons = []
        button_texts = [
            "Tell me how characters hunger drains. You should give me an answer in 500 words.",
            "What is Wilson?",
            "How to craft an axe?",
            "...",
        ]

        async def buttonClicked(text):
            for button in buttons:
                button.hide()
            self.askLLM(text)
            await self.getLLMAnswer(text)

        # Create a grid layout for the buttons
        grid_layout = QGridLayout()

        # Add the buttons to the grid layout
        for i, text in enumerate(button_texts):
            button = QPushButton(text)
            button.clicked.connect(lambda checked, text=text: asyncio.ensure_future(buttonClicked(text)))
            buttons.append(button)
            grid_layout.addWidget(button, i // 2, i % 2)

        # Set spacing between the buttons
        grid_layout.setSpacing(10)
        # Add a stretch to separate the chat bubble and the buttons
        self.chatWindow.chat_layout.addStretch()
        # Add the grid layout to the chat layout
        self.chatWindow.chat_layout.addLayout(grid_layout)

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
        # 创建中心部件并设置布局
        centralWidget = QWidget(self)  # 创建一个 QWidget 作为中心部件
        self.setCentralWidget(centralWidget)  # 设置中心部件

        # 在中心部件上创建并设置布局
        self.layout = QVBoxLayout(centralWidget)  # 创建布局并将中心部件作为父对象

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

    def displayConfigInfo(self):
        """
        Displays the configuration information in the status bar.
        """
        self.config = load_config()  # Reload the config to get the latest updates
        config_info = (
            "Base Model: "
            + self.config.get("BASE_MODEL")
            + " | Temperature: "
            + str(self.config.get("TEMPERATURE"))
            + " | Vectorstore Directory: "
            + self.config.get("VECTORSTORE_DIRECTORY")
            + " | Template Type: "
            + self.config.get("TEMPLATE_TYPE")
            + " | RAG: "
            + self.config.get("RAG")
            + (
                " (You are using a pure LLM foundation model!)"
                if self.config.get("RAG") == "disabled"
                else ""
            )
            + "| Log: "
            + self.config.get("LOG")
        )
        QTimer.singleShot(0, self.statusbar.show)
        self.statusbar.showMessage(config_info)
        QTimer.singleShot(20000, self.statusbar.hide)  # 20s

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
        self.chatWindow.removeMessage("Thinking... (Retry if no feedback in 10 seconds due to occasional request error)")

    def askLLM(self, user_text):
        """
        Adds the user's text to the chat window on the right side
        and displays a "Thinking... (Retry if no feedback in 10 seconds due to occasional request error)" message on the left side.
        """
        self.chatWindow.addMessage(user_text, "right")
        self.chatWindow.addMessage("Thinking... (Retry if no feedback in 10 seconds due to occasional request error)", "left")

    async def getLLMAnswer(self, user_text):
        """
        Retrieves the answer from LLM asynchronously.

        Args:
            user_text (str): The user's input text.

        Returns:
            str: The answer to the question.
        """

        load_config()
        rag_status = self.config.get("RAG")
        with get_openai_callback() as cb:
            llm_answers = await self.llm.get_answer_async(user_text, rag_status)
            tokens = cb.total_tokens
            dict_tokens = {
                "prompt_tokens": cb.prompt_tokens,
                "completion_tokens": cb.completion_tokens,
            }
            # cost = cb.total_cost
            cost = self.llm.calculate_cost(dict_tokens)
        if llm_answers["rag"] != "" and llm_answers["pure"] != "":
            self.chatWindow.addMessage(llm_answers["rag"], "left-rag", tokens, cost)
            self.chatWindow.addMessage(llm_answers["pure"], "left-pure")

        elif llm_answers["pure"] != "":
            self.chatWindow.addMessage(llm_answers["pure"], "left-pure", tokens, cost)

        elif llm_answers["rag"] != "":
            self.chatWindow.addMessage(llm_answers["rag"], "left-rag", tokens, cost)
