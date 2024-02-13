# pylint: disable=E0611,C0103,C0303
"""
This module provides a PyQt5 application for a chat window.
"""
import sys
import asyncio
from qasync import QEventLoop
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication
from src.main_window import MainWindow


def main():
    """
    This is the main function of the application.
    It initializes the QApplication and sets the window icon.
    """
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("assets/logo.jpg"))
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    mainWindow = MainWindow()
    mainWindow.show()

    with loop:
        loop.run_forever()


if __name__ == "__main__":
    main()
