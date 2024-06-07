import asyncio
import os
import time
from typing import List, Optional

from enums import LogLevel
from helpers.helpers import Helpers
from setup import logger


class ChannelMessage:
    def __init__(self, message, channel, delay=''):
        self.messages = [message]
        self.media = []
        self.grouped_id = message.grouped_id
        self.forward = message.forward
        self.channel = channel
        self.time = time.time()
        self.delay = 0 if not delay else Helpers.time_to_timestamp(delay)
        self.output_text = message.text

    def __del__(self):
        for m in self.media:
            os.remove(m)

    def add_message(self, message):
        self.messages.append(message)

    async def download_media(self):
        for msg in self.messages:
            if msg.media:
                try:
                    file_path = await msg.download_media()
                    if file_path and os.path.exists(file_path):
                        new_file_path = os.path.join("assets/download", file_path)

                        logger.log(LogLevel.Debug, f"Got media file: {new_file_path}")

                        os.makedirs(os.path.dirname(new_file_path), exist_ok=True)
                        os.rename(file_path, new_file_path)
                        self.media.append(new_file_path)
                    else:
                        logger.log(LogLevel.Error, f"File path does not exist: {file_path}")
                except Exception as e:
                    logger.log(LogLevel.Error, f"Error downloading media: {e}")

    async def all_messages_received(self) -> bool:
        if not self.grouped_id:
            return True
        await asyncio.sleep(1)
        return time.time() - self.time > 1

    def get_text(self):
        for msg in self.messages:
            if msg.text.strip():
                return msg.text

        return ''

    def get_forward_name(self, forwarded_message):
        """Retrieve the name of the original sender of a forwarded message."""
        name = 'Unknown'
        if self.forward.sender:
            name = self.forward.sender.username
        elif self.forward.channel_post > 0:
            name = self.forward.chat.title
        self.output_text = forwarded_message.replace('{name}', name).replace('{line}', '\n') + self.output_text
