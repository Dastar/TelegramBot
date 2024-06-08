from typing import Optional

from channel_message import ChannelMessage
from channel_registry import ChannelRegistry
from enums import Commands, LogLevel
from setup import logger


class MessagePool:
    def __init__(self, channels: ChannelRegistry):
        self.grouped_messages = {}
        self.messages = []
        self.channels = channels

    def create_message(self, event) -> Optional[ChannelMessage]:
        if event.message.grouped_id:
            gid = event.message.grouped_id
            if gid in self.grouped_messages:
                self.grouped_messages[gid].add_message(event.message)
                return None
            else:
                self.grouped_messages[gid] = self._create_message(event)
                return self.grouped_messages[gid]
        else:
            message = self._create_message(event)
            return message

    def _create_message(self, event) -> ChannelMessage:
        msg = event.message
        channel = self.channels.get_channel(event.chat.username)
        if channel is None:
            logger.log(LogLevel.Error, f'Target for {event.chat.username} not found.')
            raise Exception(f'Target for {event.chat.username} not found.')

        message = ChannelMessage(msg, channel)
        return message

    def remove_message(self, gid):
        if gid is not None:
            if gid in self.grouped_messages:
                self.grouped_messages.pop(gid)
