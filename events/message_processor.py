import asyncio
from helpers.helpers import Helpers
from events.channel_message import ChannelMessage
from logger import LogLevel
from setup import logger


class MessageProcessor:
    def __init__(self, ai_client, message_pool, configs):
        self.ai_client = ai_client
        self.message_pool = message_pool
        self.configs = configs

    async def process_message(self, message: ChannelMessage):
        """Process message content and media."""
        await self._wait_for_grouped_messages(message)
        message.download_tg_media()

        text = message.get_message_text()
        if text.strip():
            logger.log(LogLevel.Debug, 'Got message with text')
            message.output_text, message.code_blocks = Helpers.extract_code_blocks(text)

        await self.ai_client.run(message)
        message.output_text = Helpers.insert_code_blocks(message.get_text(), message.code_blocks)
        message.output_text = f"\u202B{message.output_text}\u202C"

        message.get_forward_name(self.configs['forward_message'])
        return message

    async def _wait_for_grouped_messages(self, message: ChannelMessage):
        """Wait for all grouped messages to be received."""
        if not await message.all_messages_received():
            if not await message.all_messages_received():
                logger.log(LogLevel.Error, 'Failed to receive all grouped messages.')
        self.message_pool.remove_message(message.grouped_id)
