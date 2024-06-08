from typing import Optional

from telethon import Button

from message.channel import ChannelMessage
from channel_registry import ChannelRegistry, Channel
from enums import Commands, LogLevel
from setup import logger


class MessageFactory:
    def __init__(self, channels: ChannelRegistry):
        self.grouped_messages = {}
        self.messages = []
        self.channels = channels
        self.commands = {}

    def create_message(self, event) -> Optional[ChannelMessage]:
        if event.message.text.startswith(Commands.Command):
            return self._create_command(event)
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

    def _create_message(self, event, delay='') -> ChannelMessage:
        msg = event.message
        channel = self.channels.get_channel(event.chat.username)
        if channel is None:
            logger.log(LogLevel.Error, f'Target for {event.chat.username} not found.')
            raise Exception(f'Target for {event.chat.username} not found.')

        message = ChannelMessage(msg, channel, delay)
        return message

    def _create_command(self, event) -> ChannelMessage:
        buttons = [
            [Button.inline('Do Nothing', b'')],
            [Button.inline('Restart', b'restart')]
        ]
        channel = Channel(event.chat.username, None, None, None)
        message = ChannelMessage(event.message, channel, buttons=buttons)
        message.output_text = 'Command Menu'
        return message

    def remove_message(self, gid):
        if gid is not None:
            if gid in self.grouped_messages:
                self.grouped_messages.pop(gid)
