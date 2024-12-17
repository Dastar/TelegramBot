import asyncio
from datetime import timedelta
from typing import Optional

from events.channel_message import ChannelMessage
from tg_client.channel_registry import ChannelRegistry
from enums import Commands, LogLevel
from setup import logger


class MessageFactory:
    def __init__(self, channels: ChannelRegistry):
        self.grouped_messages = {}
        self.messages = []
        self.channels = channels
        self.queue = asyncio.Queue(maxsize=1)

    def create_message(self, event) -> Optional[ChannelMessage]:
        if event.message.grouped_id:
            gid = event.message.grouped_id
            if gid in self.grouped_messages:
                self.grouped_messages[gid].add_message(event.message)
                return None
            else:
                self.grouped_messages[gid] = self._create_message(event)
                logger.log(LogLevel.Debug, f"Got new grouped message for {self.grouped_messages[gid].channel.target}")
                return self.grouped_messages[gid]
        else:
            message = self._create_message(event)
            logger.log(LogLevel.Debug, f"Got new message for {message.channel.target}")
            return message

    def get_command(self):
        if not self.queue.empty():
            try:
                command = self.queue.get_nowait()
                return command
            except asyncio.QueueEmpty:
                return None

    def _create_message(self, event) -> ChannelMessage:
        msg = event.message
        msg_id = event.message.id
        sender_id = event.sender.id
        channel = self.channels.get_channel(event.chat.username)
        if channel is None:
            logger.log(LogLevel.Error, f'Target for {event.chat.username} not found.')
            raise Exception(f'Target for {event.chat.username} not found.')

        command = self.get_command()
        delay = None
        generate_image = False
        if command and command[0] == Commands.Delay:
            logger.log(LogLevel.Info, 'Got delayed message')
            delay = timedelta(minutes=int(command[1]))
        if command == Commands.GenerateImage:
            logger.log(LogLevel.Info, 'Got generating image command')
            generate_image = True

        message = ChannelMessage(msg, msg_id, sender_id, event.chat.username, channel, generate_image)
        return message

    def remove_message(self, gid):
        if gid is not None:
            if gid in self.grouped_messages:
                self.grouped_messages.pop(gid)
