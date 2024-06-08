from logger import LogLevel
from message_pool import MessagePool
from setup import logger
from ai_client.ai_client import AIClient
from channel_registry import ChannelRegistry
from simple_client import SimpleClient
from helpers.helpers import Helpers

from channel_message import ChannelMessage


class MessageHandler:
    def __init__(self, client, ai_client: AIClient, channels: ChannelRegistry, config):
        logger.log(LogLevel.Debug, f"Creating Message Handler. Number of monitored channels: {len(channels.channels)}")
        self.client = SimpleClient(client, 'md')
        self.ai_client = ai_client
        self.message_pool = MessagePool(channels)
        self.forwarded_message = config['forward_message']

    async def handle_new_message(self, event):
        """Handle new incoming messages."""
        logger.log(LogLevel.Debug, "handle_new_message running")
        message = self.message_pool.create_message(event)
        if message is None:
            return

        await self.process_message(message)

        logger.log(LogLevel.Debug, f"Translated text: {message.output_text}")
        await self.client.send(message.channel.target, message.output_text, message.media)

        logger.log(LogLevel.Debug, "Exiting handle_new_message")

    async def process_message(self, message):
        """Process message content and media."""

        await self._wait_for_grouped_messages(message)
        await message.download_tg_media(self.client.client)

        text = message.get_text()
        if text.strip():
            logger.log(LogLevel.Debug, 'Got message with text')
            message.output_text, code_blocks = Helpers.extract_code_blocks(text)
            translated_text = await self.ai_client.run_model(message.output_text, message.channel)
            translated_text = Helpers.insert_code_blocks(translated_text, code_blocks)
            message.output_text = f"\u202B{translated_text}\u202C"

        message.get_forward_name(self.forwarded_message)

        return message

    async def _wait_for_grouped_messages(self, message: ChannelMessage):
        if not await message.all_messages_received():
            if not await message.all_messages_received():
                logger.log(LogLevel.Error, 'Failed to receive all grouped messages.')
        self.message_pool.remove_message(message.grouped_id)

