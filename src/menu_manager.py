# pylint: disable=E0611,W0611,C0103,C0303,R0903,W0201,C0301
"""
This module 
"""

from PyQt5.QtWidgets import QActionGroup, QAction


class MenuManager:
    """
    This class manages the menu.
    """

    def __init__(self, menubar, mainWindow):
        self.menubar = menubar
        self.mainWindow = mainWindow

    def createCheckableMenu(self, name, actions):
        """
        Creates a checkable menu with the given name and actions.

        Args:
            name (str): The name of the menu.
            actions (list): List of actions for the menu.

        Returns:
            None
        """
        menu = self.menubar.addMenu(name)
        actionGroup = QActionGroup(self.mainWindow)
        actionGroup.setExclusive(True)
        for actionText, isDefault in actions:
            action = QAction(actionText, self.mainWindow, checkable=True)
            # Set custom property to identify the menu
            action.setProperty("menuName", name)
            action.triggered.connect(self.mainWindow.handleMenuSelection)
            actionGroup.addAction(action)
            menu.addAction(action)
            if isDefault:
                action.setChecked(True)

    def createActionMenu(self, name, actions):
        """
        Create a menu with multiple actions.

        Args:
        name (str): The name of the menu.
        actions (list of tuples): A list where each tuple contains action text and the corresponding method.
        """
        menu = self.menubar.addMenu(name)
        for actionText, method in actions:
            action = QAction(actionText, self.mainWindow)
            action.triggered.connect(method)
            menu.addAction(action)
