import telethon

from message.channel import ChannelMessage
from logger import LogLevel
from setup import logger
from enums import Enum
from telethon.extensions import markdown


class Status(Enum):
    Success = 0
    MediaCaptionTooLong = 1
    Error = 999


class SimpleClient:
    def __init__(self, client: telethon.TelegramClient, parse_mode: str):
        self.client = client
        self.parse_mode = parse_mode

    async def send(self, message: ChannelMessage):
        if message.media:
            status = await self._send_media(message.channel.target, message.media, message.output_text)
            if status == Status.MediaCaptionTooLong:
                status = await self._send_media(message.channel.target, message.media)
                status = await self._send_message(message.channel.target, message.output_text)
        elif message.buttons:
            await self._send_buttons(message.messages[0].chat.username, message.output_text, message.buttons)
        else:
            await self._send_message(message.channel.target, message.output_text)

    @staticmethod
    def callback(current, total):
        print('Uploaded', current, 'out of', total,
              'bytes: {:.2%}'.format(current / total))

    async def _send_media(self, target, media, message="") -> Status:
        try:
            sent = await self.client.send_message(target, message, parse_mode='md', file=media)
            logger.log(LogLevel.Info, f"Message {sent[0].id} with {len(media)} media is sent to {target}")
            return Status.Success
        except telethon.errors.MediaCaptionTooLongError as ex:
            logger.log(LogLevel.Error, f"Media caption too long, sending separate messages")
            return Status.MediaCaptionTooLong
        except Exception as ex:
            logger.log(LogLevel.Error, f"Error sending media to {target}: {ex}")
            return Status.Error

    async def _send_message(self, target, message) -> Status:
        try:
            sent = await self.client.send_message(target, message, parse_mode='md')
            logger.log(LogLevel.Info, f"Message {sent.id} is sent to {target}")
            return Status.Success
        except Exception as e:
            logger.log(LogLevel.Error, f"Error occurred: {e}")
            return Status.Error

    async def _send_buttons(self, target, message, buttons):
        try:
            sent = await self.client.send_message(target, message, parse_mode='md', buttons=buttons)
            logger.log(LogLevel.Info, f"Message {sent.id} is sent to {target}")
            return Status.Success
        except Exception as e:
            logger.log(LogLevel.Error, f"Error occurred: {e}")
            return Status.Error
