# pylint: disable=E0611,W0611,C0103,C0303,R0903
"""
This module provides functinalities for logging.
"""
import datetime
import os
from src.config import load_config


class ChatLogger:
    """
    This class provides functionalities for logging chat messages.
    """

    def __init__(self, log_filepath):
        self.config = load_config()
        self.log_filepath = log_filepath
        self.log_meta = {
            "start_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "message_counts": 0,
            # "base_model": config.get("BASE_MODEL"),
            "knowledge_sources": self.config.get("KNOWLEDGE_SOURCES", []),
            "chat_tokens": 0,
            "cost": 0,
        }
        self.start_log_chat()

    def start_log_chat(self):
        """
        Creates the log directory if it does not exist.
        """
        check_log_directory = os.path.dirname(self.log_filepath)
        if not os.path.isdir(check_log_directory):
            os.makedirs(check_log_directory)
        self.write_initial_meta()

    def write_initial_meta(self):
        """
        Writes the initial metadata to the log file.
        """
        with open(self.log_filepath, "w", encoding="utf-8") as file:
            self.write_meta_info(file)
            file.write("## Chat Log\n")

    def write_meta_info(self, file):
        """
        Writes the initial metadata to the log file.
        """
        for key, value in self.log_meta.items():
            value_str = ", ".join(value) if isinstance(value, list) else str(value)
            file.write(f"- {key.replace('_', ' ').title()}: {value_str}\n")

    def add_chat_to_log(self, message, side, chat_tokens, cost):
        """
        Add a chat message to the log.

        Args:
            message (str): The message to be added to the log.
            side (str): The side of the chat (e.g., 'left' or 'right').
            chat_tokens (int): The number of chat tokens used.
            cost (float): The cost associated with the chat message.
        """
        if message == "Thinking... (Retry if no feedback in 10 seconds due to occasional request error)":
            return

        # 更新元信息
        self.log_meta["message_counts"] += 1
        self.log_meta["chat_tokens"] += chat_tokens
        self.log_meta["cost"] += cost
        self.log_meta["end_time"] = datetime.datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        # 读取文件内容
        with open(self.log_filepath, "r+", encoding="utf-8") as file:
            content = file.readlines()

        # 查找聊天记录开始的位置
        chat_log_index = content.index("## Chat Log\n") + 1

        # 重新写入元信息和聊天记录
        with open(self.log_filepath, "w", encoding="utf-8") as file:
            self.write_meta_info(file)
            file.write("## Chat Log\n")
            for line in content[chat_log_index:]:
                file.write(line)

            # 追加新的聊天消息
            if side == "left":
                prefix = "DST-GPT: "
            elif side == "left-pure":
                prefix = "OpenAI GPT: "
            elif side == "left-rag":
                prefix = "DST-GPT: "
            else:
                prefix = "User:"
            file.write(prefix + message + "\n")
