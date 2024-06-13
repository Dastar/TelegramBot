import asyncio

from enums import Commands
from logger import LogLevel
from setup import logger
from ai_client.ai_client import AIClient
from tg_client.channel_registry import ChannelRegistry
from tg_client.simple_client import SimpleClient
from helpers.helpers import Helpers

from message.factory import MessageFactory
from message.channel import ChannelMessage


class MessageHandler:
    def __init__(self, client, ai_client: AIClient, channels: ChannelRegistry, config):
        logger.log(LogLevel.Debug, f"Creating Message Handler. Number of monitored channels: {len(channels.channels)}")
        self.client = SimpleClient(client, 'md')
        self.ai_client = ai_client
        self.message_pool = MessageFactory(channels)
        self.forwarded_message = config['forward_message']

    async def handle_new_message(self, event):
        """Handle new incoming messages."""
        if event.message.text.startswith(Commands.GenerateImage):
            try:
                self.message_pool.queue.put_nowait(Commands.GenerateImage)
                logger.log(LogLevel.Info, f'Got image generating command. Next post will appear with generated image')
            except asyncio.QueueFull:
                logger.log(LogLevel.Warning, f'Error: command queue is full.')

            return
        elif event.message.text.startswith(Commands.GetLog):
            message = self.message_pool.create_message(event)
            message.output_text = logger.get_log()
            message.set_temp_target(event.chat.username)
            await self.client.send(message)
            return

        message = self.message_pool.create_message(event)
        if message is None:
            return
        if message.is_command():
            logger.log(LogLevel.Info, 'Sending command menu')
            await self.client.send(message)
            return

        await self.process_message(message)

        logger.log(LogLevel.Debug, f"Translated text: {message.output_text}")
        await self.client.send(message)

        logger.log(LogLevel.Debug, "Exiting handle_new_message")

    async def hadle_buttons(self, event):
        data = event.data.decode('utf-8')
        if data == 'restart':
            await event.answer('Restarting')
            return data
        return ''

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

        message.get_forward_name(self.forwarded_message)

        return message

    async def _wait_for_grouped_messages(self, message: ChannelMessage):
        if not await message.all_messages_received():
            if not await message.all_messages_received():
                logger.log(LogLevel.Error, 'Failed to receive all grouped messages.')
        self.message_pool.remove_message(message.grouped_id)

