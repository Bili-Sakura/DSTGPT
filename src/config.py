# pylint: disable=E0611,W0611,C0103,C0303,R0903,E1101,E1102
"""
This module provides functionality for configurations.
"""

import json
from PyQt5.QtCore import pyqtSignal, QObject


class ConfigUpdater(QObject):
    """
    This class provides functionality for updating configurations.
    """

    configChanged = pyqtSignal()


configUpdater = ConfigUpdater()


def load_config():
    """
    Load the configuration from the configs.json file.

    Returns:
    dict: The loaded configuration.
    """
    with open("./config/configs.json", "r", encoding="utf-8") as file:
        config = json.load(file)
    return config


def update_config(key, value):
    """
    Update the configuration with the given key-value pair.

    Args:
    key (str): The key to be updated.
    value (any): The value to be associated with the key.

    Returns:
    None
    """
    config = load_config()
    config[key] = value
    with open("./config/configs.json", "w", encoding="uft-8") as file:
        json.dump(config, file, indent=4)
    # Emit the signal to indicate config change
    configUpdater.configChanged.emit()
