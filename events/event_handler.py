import asyncio
from logger import LogLevel
from setup import logger
from ai_client.ai_client import AIClient
from tg_client.channel_registry import ChannelRegistry
from tg_client.simple_client import SimpleClient
from events.factory import MessageFactory
from events.command_processor import CommandProcessor
from events.message_processor import MessageProcessor


class EventHandler:
    def __init__(self, client, ai_client: AIClient, channels: ChannelRegistry, config):
        logger.log(LogLevel.Debug, f"Creating Message Handler. Number of monitored channels: {len(channels.channels)}")
        self.client = SimpleClient(client, 'md')
        self.ai_client = ai_client
        self.message_pool = MessageFactory(channels)
        self.forwarded_message = config['forward_message']
        self.channels = channels
        self.command_processor = CommandProcessor(self.client, self.message_pool, self.channels, self.forwarded_message)
        self.message_processor = MessageProcessor(ai_client, self.message_pool, self.forwarded_message)
        self._register_commands()

    def _register_commands(self):
        """Register command handlers."""
        self.register_command('/image', self.command_processor.generate_image_command)
        self.register_command('/log', self.command_processor.get_log_command)
        self.register_command('/role', self.command_processor.role_command)
        self.register_command('/save', self.command_processor.save_command)

    def register_command(self, command, handler):
        self.command_processor.register_command(command, handler)

    async def handle_new_message(self, event):
        """Handle new incoming messages."""
        text = event.message.text.split()[0] if event.message.text.strip() else ''
        if text in self.command_processor.commands:
            await self.command_processor.execute_command(text, event)
        else:
            await self._handle_generic_message(event)

    async def handle_buttons(self, event):
        """Handle button interactions."""
        data = event.data.decode('utf-8')
        if data == 'restart':
            await event.answer('Restarting')
            return data
        return ''

    async def handle_edited_messages(self, event):
        """Handle edited messages."""
        logger.log(LogLevel.Debug, "Handling edited message")
        if not event.message.text.startswith('/role'):
            return

        channel = self.channels.get_channel(event.chat.username)
        logger.log(LogLevel.Debug, f"Editing role {channel.role.name}")
        channel.role.from_text(event.message.text)

    async def _handle_generic_message(self, event):
        """Handle generic messages."""
        message = self.message_pool.create_message(event)
        if message is None:
            return

        if message.is_command():
            logger.log(LogLevel.Info, 'Sending command menu')
            await self.client.send(message)
            return

        await self.message_processor.process_message(message)
        logger.log(LogLevel.Debug, f"Translated text: {message.output_text}")
        await self.client.send(message)
        logger.log(LogLevel.Debug, "Exiting handle_new_message")
