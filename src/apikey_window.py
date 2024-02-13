# pylint: disable=E0611,W0611,C0103,C0303,R0903,W0201,C0301
"""
This module 
"""
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton


class ApiKeyDialog(QDialog):
    """
    Represents a dialog for setting an API key.
    """

    def __init__(self):
        """
        Initializes the dialog.
        """
        super().__init__()
        self.setWindowTitle("Set API Key")
        self.setFixedSize(600, 300)
        self.layout = QVBoxLayout(self)

        label_key = QLabel("Enter your API Key:")
        self.api_key_input = QLineEdit()
        self.api_key_input.textChanged.connect(self.validate_api_key)

        label_url = QLabel("Enter your OpenAI Base URL(Optional):")
        self.base_url_input = QLineEdit()

        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.on_ok_button_clicked)

        self.error_label = QLabel()
        self.error_label.setStyleSheet("color: red")

        self.layout.addWidget(label_key)
        self.layout.addWidget(self.api_key_input)
        self.layout.addWidget(label_url)
        self.layout.addWidget(self.base_url_input)
        self.layout.addWidget(ok_button)

    def validate_api_key(self):
        """
        Validates the API key input.
        """
        api_key = self.api_key_input.text()
        if not api_key.startswith("sk-"):
            self.error_label.setText("Invalid API Key. It should start with 'sk-.'")
            if self.error_label not in self.layout.children():
                self.layout.addWidget(self.error_label)
        else:
            self.error_label.setText("")
            self.layout.removeWidget(self.error_label)

    def on_ok_button_clicked(self):
        """
        Handles the OK button click event.
        """
        api_key = self.api_key_input.text()
        base_url = self.base_url_input.text()
        if api_key.startswith("sk-"):
            print("Valid API Key:", api_key)
            self.accept()
        else:
            self.validate_api_key()
        if base_url != "":
            print("Base URL:", base_url)

    def setAPIKey(self):
        """
        Displays the dialog to set the API key.
        """
        dialog = ApiKeyDialog()
        if dialog.exec_() == QDialog.Accepted:
            api_key = dialog.api_key_input.text()
            base_url = dialog.base_url_input.text()
            return api_key, base_url
        else:
            return "", ""
