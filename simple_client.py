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
            status = await self._send_message(message)
            if status == Status.MediaCaptionTooLong:
                message.send_text = False
                status = await self._send_message(message)
                message.send_media = False
                status = await self._send_message(message)
        elif message.buttons:
            await self._send_buttons(message.get_sender(), message.output_text, message.buttons)
        else:
            await self._send_message(message)

    @staticmethod
    def callback(current, total):
        print('Uploaded', current, 'out of', total,
              'bytes: {:.2%}'.format(current / total))

    async def _send_media(self, target, media, delay, message="") -> Status:
        try:
            sent = await self.client.send_message(target,
                                                  message,
                                                  parse_mode='md',
                                                  file=media)

            logger.log(LogLevel.Info, f"Message {sent[0].id} with {len(media)} media is sent to {target}")
            return Status.Success
        except telethon.errors.MediaCaptionTooLongError as ex:
            logger.log(LogLevel.Error, f"Media caption too long, sending separate messages")
            return Status.MediaCaptionTooLong
        except Exception as ex:
            logger.log(LogLevel.Error, f"Error sending media to {target}: {ex}")
            return Status.Error

    async def _send_message(self, message: ChannelMessage) -> Status:
        target = message.get_target()
        try:
            media = message.get_media()
            text = message.get_output()

            sent = await self.client.send_message(target,
                                                  text,
                                                  parse_mode='md',
                                                  file=media)
            logger.log(LogLevel.Info, f"Message sent to {target} with {len(media) if media else 0} media")
            return Status.Success
        except telethon.errors.MediaCaptionTooLongError as ex:
            logger.log(LogLevel.Error, f"Media caption too long")
            return Status.MediaCaptionTooLong
        except Exception as ex:
            logger.log(LogLevel.Error, f"Error sending media to {target}: {ex}")
            return Status.Error

    async def _send_buttons(self, target, message, buttons):
        try:
            sent = await self.client.send_message(target, message, parse_mode='md', buttons=buttons)
            logger.log(LogLevel.Info, f"Message {sent.id} is sent to {target}")
            return Status.Success
        except Exception as e:
            logger.log(LogLevel.Error, f"Error occurred: {e}")
            return Status.Error
