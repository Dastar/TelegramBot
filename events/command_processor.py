import asyncio

from configuration_readers.channel_reader import ChannelReader
from configuration_readers.role_reader import RoleReader
from logger import LogLevel
from setup import logger
from events.channel_message import ChannelMessage


class CommandProcessor:
    def __init__(self, client,
                 message_pool,
                 channels,
                 configs,
                 role_reader: RoleReader,
                 channel_reader: ChannelReader):
        self.client = client
        self.message_pool = message_pool
        self.channels = channels
        self.configs = configs
        self.commands = {}
        self.role_reader = role_reader
        self.channel_reader = channel_reader

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
        logger.log(LogLevel.Info, "Got log command")

        message = self.message_pool.create_message(event)
        message.output_text = logger.get_log()
        message.set_temp_target(event.chat.username)
        await self.client.send(message)

    async def role_command(self, event):
        """Handle the /role command."""
        logger.log(LogLevel.Info, "Got edit role command")

        command = event.message.text.split(' ')
        channel = self.channels.get_channel(event.chat.username)

        if len(command) > 1:
            new_role = self.role_reader.get_role(command[1])
            if new_role is None:
                logger.log(LogLevel.Error, f'Role with name {command[1]} not found')
            else:
                logger.log(LogLevel.Info, f'Registering new role for channel {channel.target}')
                channel.init_role(new_role)
        role = str(channel.role)
        await self.client.send_text(event.chat.username, role)

    async def save_command(self, event):
        """Handle the /save command."""

        channel = self.channels.get_channel(event.chat.username)
        self.channel_reader.save(channel)
        # Implement save logic here
        logger.log(LogLevel.Info, f"Save command received for channel {channel.target}")
        self.role_reader.save(channel.role)
        logger.log(LogLevel.Info, f"Role {channel.role.name} saved")

    async def config_command(self, event):
        command = event.message.text.split(' ')
        if command[1].lower() == "delay":
            self.configs['to_delay'] = not self.configs['to_delay']
            logger.log(LogLevel.Info, f"Delay set to {self.configs['to_delay']}")
        if command[1].lower() == 'forward':
            self.configs['forward_message'] = ' '.join(command[2:])
            logger.log(LogLevel.Info, f"Forwarded message set to {self.configs['forward_message']}")

