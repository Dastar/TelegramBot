import asyncio
import os
import time
from telethon.tl.types import MessageMediaWebPage

from enums import LogLevel
from setup import logger


class ChannelMessage:
    def __init__(self, message, sender, channel, generate_image=False):
        self.messages = [message]
        self.media = []
        self.sent_id = []
        self.sender = sender
        self.grouped_id = message.grouped_id
        self.forward = message.forward
        self.channel = channel
        self.time = time.time()
        self.delay = 0
        self.output_text = message.text
        self.buttons = None
        self.send_media = True
        self.send_text = True
        self.generate_image = generate_image
        self.code_blocks = None
        self.temp_target = None

    def __del__(self):
        for m in self.media:
            if isinstance(m, str):
                try:
                    os.remove(m)
                except Exception as ex:
                    logger.log(LogLevel.Error, f"Filed to delete file {m}. Error: {ex}")

    def is_command(self):
        return self.buttons is not None

    def add_message(self, message):
        self.messages.append(message)

    def download_tg_media(self):
        for msg in self.messages:
            if msg.media and not isinstance(msg.media, MessageMediaWebPage):
                self.media.append(msg.media)

    async def all_messages_received(self) -> bool:
        if not self.grouped_id:
            return True
        await asyncio.sleep(1)
        return time.time() - self.time > 1

    def get_message_text(self):
        for msg in self.messages:
            if msg.text.strip():
                return msg.text

        return ''

    def get_text(self):
        if self.output_text:
            return self.output_text
        else:
            return self.get_message_text()

    def get_output(self):
        if not self.send_text and self.send_media:
            return ''
        return self.output_text

    def get_media(self):
        if not self.send_media or len(self.media) == 0:
            return None
        return self.media

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

    def get_target(self):
        if self.temp_target:
            temp = self.temp_target
            self.temp_target = None
            return temp
        return self.channel.target

    def set_temp_target(self, target):
        self.temp_target = target

    def to_sender(self):
        self.set_temp_target(self.sender)

    def get_sender(self):
        return self.messages[0].chat.username
