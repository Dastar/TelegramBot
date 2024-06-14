import asyncio
from logger import LogLevel
from setup import logger
from events.channel import ChannelMessage


class CommandProcessor:
    def __init__(self, client, message_pool, channels, forwarded_message, role_reader):
        self.client = client
        self.message_pool = message_pool
        self.channels = channels
        self.forwarded_message = forwarded_message
        self.commands = {}
        self.role_reader = role_reader

    def register_command(self, command, handler):
        """Register a new command handler."""
        self.commands[command] = handler

    async def execute_command(self, command, event):
        """Execute a registered command handler."""
        if command in self.commands:
            await self.commands[command](event)
        else:
            logger.log(LogLevel.Warning, f"Unknown command: {command}")

    async def generate_image_command(self, event):
        """Handle the /generate_image command."""
        try:
            self.message_pool.queue.put_nowait("GenerateImage")
            logger.log(LogLevel.Info, 'Got image generating command. Next post will appear with generated image')
        except asyncio.QueueFull:
            logger.log(LogLevel.Warning, 'Error: command queue is full.')

    async def get_log_command(self, event):
        """Handle the /get_log command."""
        message = self.message_pool.create_message(event)
        message.output_text = logger.get_log()
        message.set_temp_target(event.chat.username)
        await self.client.send(message)

    async def role_command(self, event):
        """Handle the /role command."""
        channel = self.channels.get_channel(event.chat.username)
        role = str(channel.role)
        await self.client.send_text(event.chat.username, role)

    async def save_command(self, event):
        """Handle the /save command."""
        channel = self.channels.get_channel(event.chat.username)
        # Implement save logic here
        logger.log(LogLevel.Info, f"Save command received for channel {channel}")