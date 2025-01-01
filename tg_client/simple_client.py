import aiohttp
import telethon
from telethon import TelegramClient, Button

from events.channel_message import ChannelMessage
from logger import LogLevel
from setup import logger
from enums import Enum


class Status(Enum):
    Success = 0
    MediaCaptionTooLong = 1
    Error = 999


class SimpleClient:
    def __init__(self, config, parse_mode: str):
        self.client = TelegramClient(config['session_name'], config['api_id'], config['api_hash'])
        self.parse_mode = parse_mode
        self.token = config['bot_token']
        self.captions = [[("Regenerate", "regenerate:{}"), ("Send", "send:{}")],
                         [("New Image", "image:{}"), ("Delete", "delete:{}")]]

    def set_up_handler(self, event, handler):
        self.client.on(event)(handler)

    def is_connected(self):
        return self.client.is_connected()

    async def disconnect(self):
        await self.client.disconnect()

    async def start(self):
        await self.client.start(bot_token=self.token)

    async def send(self, message: ChannelMessage):
        if message.approved:
            status = await self._send_message(message)
            if status == Status.MediaCaptionTooLong:
                message.send_text = False
                status = await self._send_message(message)
                message.send_media = False
                status = await self._send_message(message)
        else:
            await self._send_process_message(message)

    def generate_buttons(self, captions, data_id=None):
        if isinstance(captions, tuple):
            data = captions[1] if data_id is None else captions[1].format(data_id)
            return Button.inline(captions[0], data)
        elif isinstance(captions, str):
            return Button.inline(captions, captions)
        else:
            buttons = []
            for c in captions:
                buttons.append(self.generate_buttons(c, data_id))
            return buttons

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
            if isinstance(sent, list):
                for s in sent:
                    message.sent_id.append(s.id)
            else:
                message.sent_id.append(sent.id)
            return Status.Success
        except telethon.errors.MediaCaptionTooLongError as ex:
            logger.log(LogLevel.Error, f"Media caption too long")
            return Status.MediaCaptionTooLong
        except Exception as ex:
            logger.log(LogLevel.Error, f"Error sending media to {target}: {ex}")
            return Status.Error

    async def _send_process_message(self, message: ChannelMessage) -> Status:
        target = message.sender_id
        try:
            text = message.get_output()
            mhash = message.get_hash()
            buttons = self.generate_buttons(self.captions, mhash)
            sent = await self.client.send_message(message.sender_id,
                                                  text,
                                                  parse_mode='md',
                                                  buttons=buttons, link_preview=False)
            return Status.Success
        except telethon.errors.MediaCaptionTooLongError as ex:
            logger.log(LogLevel.Error, f"Media caption too long")
            return Status.MediaCaptionTooLong

        except Exception as ex:
            logger.log(LogLevel.Error, f"Error sending media to {target}: {ex}")
            return Status.Error

    async def send_text(self, target, text):
        try:
            sent = await self.client.send_message(target,
                                                  text)
            logger.log(LogLevel.Info, f"Text sent to {target}")
            return Status.Success
        except Exception as ex:
            logger.log(LogLevel.Error, f"Error sending text to {target}: {ex}")
            return Status.Error

    async def get_file_url(self, file_id):
        """Fetches the file path and constructs the URL asynchronously."""
        url = f"https://api.telegram.org/bot{self.token}/getFile?file_id={file_id}"

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                result = await response.json()

                if result['ok']:
                    file_path = result['result']['file_path']
                    file_url = f"https://api.telegram.org/file/bot{self.token}/{file_path}"
                    return file_url
                return None
