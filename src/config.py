# pylint: disable=E0611,W0611,C0103,C0303,R0903,E1101,E1102
"""
This module provides functionality for configurations.
"""

import json
import os
from PyQt5.QtCore import pyqtSignal, QObject


class ConfigUpdater(QObject):
    """
    This class provides functionality for updating configurations.
    It emits a signal whenever the configuration is updated.
    """

    configChanged = pyqtSignal()
    llm_configChanged = pyqtSignal()


# Global instance of ConfigUpdater to emit signals from anywhere
configUpdater = ConfigUpdater()


def load_config():
    """
    Load the configuration from the 'configs.json' file within the 'config' directory.

    Returns:
        dict: The loaded configuration, or an empty dictionary if the file does not exist.
    """
    config_path = "./config/configs.json"
    try:
        with open(config_path, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        print(
            f"Configuration file not found at '{config_path}'. Returning empty configuration."
        )
        return {}
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from configuration file: {e}")
        return {}


def update_config(key, value):
    """
    Update the configuration by appending the given key-value pair and save the changes to the file.

    Args:
        key (str): The key to be updated.
        value (any): The value to be appended to the key.

    Returns:
        None
    """
    config = load_config()
    if key in config:
        if isinstance(config[key], list):
            config[key].append(value)
        else:
            config[key] = value
    else:
        config[key] = value
    try:
        with open("./config/configs.json", "w", encoding="utf-8") as file:
            json.dump(config, file, indent=4)
        # Emit the signal to indicate config change
        configUpdater.configChanged.emit()
        if key in [
            "BASE_MODEL",
            "TEMPERATURE",
            "VECTORSTORE_FILEPATH",
            "PROMPT_TEMPLATE",
            "KNOWLEDGE_SOURCES",
        ]:
            configUpdater.llm_configChanged.emit()
    except IOError as e:
        print(f"Failed to write to configuration file: {e}")
