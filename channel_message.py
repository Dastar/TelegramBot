import asyncio
import os
import time
from datetime import datetime
from typing import List, Optional

from telethon import Button

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
        self.buttons2 = [
            [Button.inline('Button 1', b'callback_data_1')],
            [Button.inline('Button 2', b'callback_data_2')]
        ]
        self.buttons = None

    def add_message(self, message):
        self.messages.append(message)

    def download_tg_media(self):
        for msg in self.messages:
            if msg.media:
                self.media.append(msg.media)

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
        if not self.forward:
            return
        name = 'Unknown'
        if self.forward.sender:
            name = self.forward.sender.username
        elif self.forward.channel_post > 0:
            name = self.forward.chat.title
        self.output_text = forwarded_message.replace('{name}', name).replace('{line}', '\n') + self.output_text
