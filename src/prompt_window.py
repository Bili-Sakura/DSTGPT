# pylint: disable=E0611,W0611,C0103,C0303,R0903,W0201,C0301
"""
This module represents the prompt window GUI using PyQt5.
"""

from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QPushButton


class PromptInputDialog(QDialog):
    """
    Represents a dialog for inputting prompt templates.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Enter Prompt Text")
        self.setFixedSize(800, 600)  # Adjust the size as needed
        layout = QVBoxLayout()

        self.text_edit = QTextEdit()  # Replace QLineEdit with QTextEdit
        self.new_template = None  # Class attribute to store the new template

        # Set a default template in the text edit
        default_template = (
            "Answer the following question based on the provided knowledge: \n"
            "<knowledge>\n"
            "{context}\n"
            "</knowledge>\n"
            "Question: {input}"
        )
        self.text_edit.setText(default_template)
        self.text_edit.setFixedHeight(400)  # You can adjust the height as needed
        layout.addWidget(self.text_edit)

        # Confirm button
        confirm_button = QPushButton("Confirm")
        confirm_button.clicked.connect(self.setPromptTemplate)
        layout.addWidget(confirm_button)
        self.setLayout(layout)

    def setPromptTemplate(self):
        """
        Store the prompt template from the text edit and close the dialog.
        """
        self.new_template = (
            self.text_edit.toPlainText()
        )  # Use toPlainText() to get the text
        self.accept()  # Close the dialog and set the result to QDialog.Accepted

    def getNewTemplate(self):
        """
        Return the new prompt template.
        """
        return self.new_template


# 使用示例：
# dialog = PromptInputDialog()
# if dialog.exec_() == QDialog.Accepted:
#     new_template = dialog.getNewTemplate()
