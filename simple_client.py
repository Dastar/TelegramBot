import telethon
from logger import logger, LogLevel
from enums import Enum


class Status(Enum):
    Success = 0
    MediaCaptionTooLong = 1
    Error = 999


class SimpleClient:
    def __init__(self, client: telethon.TelegramClient, parse_mode: str):
        self.client = client
        self.parse_mode = parse_mode

    async def send(self, target, message, media=None):
        if media:
            status = await self._send_media(target, media, message)
            if status == Status.MediaCaptionTooLong:
                status = await self._send_media(target, media)
                status = await self._send_message(target, message)
        else:
            status = await self._send_message(target, message)

    async def _send_media(self, target, media, message="") -> Status:
        try:
            sent = await self.client.send_file(target, media, caption=message, parse_mode=self.parse_mode)
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
