from logger import LogLevel
from setup import logger
from events.channel_message import ChannelMessage
from wabridge.wabridge import WABridge


class WhatsAppClient:
    def __init__(self, client_id, server, executable='/usr/bin/google-chrome-stable'):
        self.server = WABridge(server)
        self.client_id = client_id
        self.exe = executable

    async def start(self):
        try:
            await self.server.start(self.client_id, self.exe)
            await self.server.check_state()
            await self.server.cache_groups()
        except Exception as e:
            logger.log(LogLevel.Error, e)
            self.server.terminate()

    async def send(self, message: ChannelMessage):
        target = message.get_wa_target()
        if self.server.state != 'Connected':
            logger.log(LogLevel.Error, "WhatsApp client is not connected")
            return
        if target.strip() == "":
            logger.log(LogLevel.Error, "No target to send WhatsApp")
            return
        if not message.approved:
            return

        logger.log(LogLevel.Info, f"Sending WhatsApp message to target: {target}")
        text = message.get_text()
        media = message.get_link_media()
        if media:
            await self.server.send_media(target, media, text)
        elif text.strip():
            await self.server.send_message(target, text)

    def terminate(self):
        self.server.terminate()

