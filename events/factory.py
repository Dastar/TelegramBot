import asyncio
from datetime import timedelta
from typing import Optional

from telethon import events

from events.channel_message import ChannelMessage
from tg_client.channel_registry import ChannelRegistry
from enums import Commands, LogLevel
from setup import logger


class MessageFactory:
    def __init__(self, channels: ChannelRegistry):
        self.grouped_messages = {}
        self.channels = channels
        # Command queue for next incoming message. For now only one command for a message.
        self.message_command = asyncio.Queue(maxsize=1)

    def create_message(self, event) -> Optional[ChannelMessage]:
        if event.message.grouped_id:
            gid = event.message.grouped_id
            if gid in self.grouped_messages:
                self.grouped_messages[gid].add_message(event.message)
                return None
            else:
                self.grouped_messages[gid] = self.generate_message(event)
                logger.log(LogLevel.Debug, f"Got new grouped message for {self.grouped_messages[gid].channel.target}")
                return self.grouped_messages[gid]
        else:
            message = self.generate_message(event)
            logger.log(LogLevel.Debug, f"Got new message for {message.channel.target}")
            return message

    def get_command(self):
        if not self.message_command.empty():
            try:
                command = self.message_command.get_nowait()
                return command
            except asyncio.QueueEmpty:
                return None

    def generate_message(self, event) -> ChannelMessage:
        msg = self.get_event_message(event)
        msg_id = self.get_event_id(event)
        sender_id = event.sender.id
        channel = self.channels.get_channel(event.chat.username)
        if channel is None:
            logger.log(LogLevel.Error, f'Target for {event.chat.username} not found.')
            raise Exception(f'Target for {event.chat.username} not found.')

        command = self.get_command()
        generate_image = False
        if command == Commands.GenerateImage:
            logger.log(LogLevel.Info, 'Got generating image command')
            generate_image = True

        message = ChannelMessage(msg, msg_id, sender_id, event.chat.username, channel, generate_image)
        return message

    @staticmethod
    def get_event_id(event):
        if isinstance(event, events.CallbackQuery.Event):
            return event.message_id
        else:
            return event.message.id

    @staticmethod
    def get_event_message(event):
        if not isinstance(event, events.CallbackQuery.Event):
            return event.message
        else:
            return None

    def remove_message(self, gid):
        if gid is not None:
            if gid in self.grouped_messages:
                self.grouped_messages.pop(gid)
