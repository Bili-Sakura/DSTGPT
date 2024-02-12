# pylint: disable=E0611,W0611,C0103,C0303,R0903
"""
This module contains the InputLine class, which represents an input line widget for user input.
It provides functionality for handling key press events and emitting a signal when the return key is pressed.
"""

from PyQt5.QtWidgets import QTextEdit
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont


class InputLine(QTextEdit):
    """
    This class represents an input line widget for user input.
    """

    returnPressed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(1700, 70)
        self.setFont(QFont("Arial", 12))  # 设置固定的字体和字体大小
        self.setLineWrapMode(QTextEdit.WidgetWidth)  # 设置文本换行模式为按宽度换行
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

    def keyPressEvent(self, event):
        """
        Handle the key press event.

        Args:
            event (QKeyEvent): The key event object.

        Returns:
            None
        """
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            if event.modifiers() & Qt.ControlModifier:  # 检查是否同时按下了Ctrl键
                self.insertPlainText("\n")
            else:
                self.returnPressed.emit()  # 发出信号，但不插入新行
                event.accept()  # 阻止事件进一步传播
        else:
            super().keyPressEvent(event)  # 对于其他按键事件，调用基类方法
