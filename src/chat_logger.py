# pylint: disable=E0611,W0611,C0103,C0303,R0903
"""
This module provides functinalities for logging.
"""
import datetime
import os
from config import global_variables as GLOBAL


class ChatLogger:
    """
    This class represents a chat logger that logs chat conversations to a file.
    """

    def __init__(self, log_filepath):
        self.time = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        self.log_filepath = log_filepath
        self.log_meta = {
            "start_time": self.time,
            "end_time": self.time,
            "message_counts": 0,
            "base_model": GLOBAL.BASE_MODEL,
            "chat_tokens": 0,
            "cost": 0,
        }
        self.start_log_chat()

    def start_log_chat(self):
        """
        Starts logging the chat conversation.

        This method opens the log file specified by `self.log_filepath`
        and writes the chat log information to it.

        Returns:
            None
        """
        # Check if the directory of log_filepath exists
        check_log_directory = os.path.dirname(self.log_filepath)
        if not os.path.isdir(check_log_directory):
            os.makedirs(check_log_directory)
        with open(self.log_filepath, "w", encoding="utf-8") as file:
            file.write("# Chat Log\n\n")
            file.write("## Chat Info\n")
            file.write(f"- Start Time: {self.log_meta['start_time']}\n")
            file.write(f"- End Time: {self.log_meta['end_time']}\n")
            file.write(f"- Message Counts: {self.log_meta['message_counts']}\n")
            file.write(f"- Base Model: {self.log_meta['base_model']}\n")
            file.write(f"- Chat Tokens: ＄{self.log_meta['chat_tokens']}\n")
            file.write(f"- Cost: ＄{self.log_meta['cost']}\n\n")
            file.write("## Chat Log\n")

    def add_chat_to_log(self, message, side, chat_tokens, cost):
        """
        Adds a message to the chat log.

        Args:
            message (str): The text of the message.
            side (str): The side of the chat window where the message originated.

        Returns:
            None
        """
        if message == "Thinking...":
            return
        with open(self.log_filepath, "a", encoding="utf-8") as file:
            if side == "left":
                file.write("DST-GPT: ")
            elif side == "right":
                file.write("User: ")
            file.write(message + "\n")

        self.log_meta["message_counts"] += 1
        self.log_meta["cost"] += cost
        self.log_meta["chat_tokens"] += chat_tokens
        self.log_meta["end_time"] = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

    def log_meta_update(self):
        """
        Updates the metadata in the log file.

        This method updates the metadata values in the log file
        based on the current state of the chat window.

        Returns:
            None
        """
        with open(self.log_filepath, "r+", encoding="utf-8") as file:
            lines = file.readlines()
            file.seek(0)

            for line in lines:
                if line.startswith("- Message Counts:"):
                    file.write(f"- Message Counts: {self.log_meta['message_counts']}\n")
                elif line.startswith("- Cost:"):
                    file.write(f"- Cost: {self.log_meta['cost']}\n")
                elif line.startswith("- Chat Tokens:"):
                    file.write(f"- Chat Tokens: {self.log_meta['chat_tokens']}\n")
                elif line.startswith("- End Time:"):
                    file.write(f"- End Time: {self.log_meta['end_time']}\n")
                else:
                    file.write(line)

            file.truncate()
