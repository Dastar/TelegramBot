from telethon import TelegramClient, events
import asyncio

from configuration_readers.data_reader import DataReader
from configuration_readers.role_reader import RoleReader
from ai_client.ai_client import AIClient
from events.command_processor import CommandProcessor
from events.factory import MessageFactory
from events.message_processor import MessageProcessor
from tg_client.channel_registry import ChannelRegistry
from configuration_readers.channel_reader import ChannelReader
from events.messages_dict import MessagesDict
from logger import LogLevel
from setup import logger
from setup import setup_signal_handling
from tg_client.simple_client import SimpleClient


class TelegramBot:
    def __init__(self, config):
        self.config = config
        self.aiclient = AIClient(self.config['api_key'], self.config['max_retries'], self.config['base_url'], True)

        reader = DataReader(self.config['bot_config'])
        self.role_reader = RoleReader(reader)
        self.channel_reader = ChannelReader(self.role_reader, reader)

        self.channels = self._setup_channels()
        self.stop_event = asyncio.Event()
        self.restart_event = asyncio.Event()
        self.client = SimpleClient(self.config, 'md')

        self.message_pool = MessageFactory(self.channels)
        self.command_processor = CommandProcessor(self.client,
                                                  self.message_pool,
                                                  self.channels,
                                                  self.config,
                                                  self.role_reader,
                                                  self.channel_reader)
        self.message_processor = MessageProcessor(self.aiclient, self.message_pool, self.config)
        self.is_running = False
        self._register_commands()
        self.process_messages = MessagesDict()

    def _register_commands(self):
        """Register command handlers."""
        # self.register_command('/image', self.command_processor.generate_image_command)
        self.register_command('/log', self.command_processor.get_log_command)
        self.register_command('/role', self.command_processor.role_command)
        self.register_command('/save', self.command_processor.save_command)
        # self.register_command('/config', self.command_processor.config_command)
        self.register_command('/modeloff', self.aiclient.turn_off)
        self.register_command('/modelon', self.aiclient.turn_on)
        self.register_command("/command", self.get_command_list)

    def register_command(self, command, handler):
        self.command_processor.register_command(command, handler)

    async def get_command_list(self, event):
        commands = [[c] for c in self.command_processor.commands.keys()]
        buttons = self.client.generate_buttons(commands)
        await event.respond("Commands: ", buttons=buttons)
        if isinstance(event, events.NewMessage.Event):
            await self.client.client.delete_messages(event.chat.id, event.message.id)

    def _setup_channels(self):
        """Set up channel registry and readers."""
        logger.log(LogLevel.Debug, "Setting up channels")
        channels = ChannelRegistry()
        for channel, sources in self.channel_reader.get_channels():
            channels.add_channels(channel, sources)
        return channels

    async def handle_new_message(self, event):
        """Handle new incoming messages."""
        text = event.message.text.split()[0] if event.message.text.strip() else ''
        if text in self.command_processor.commands:
            await self.command_processor.execute_command(text, event)
        else:
            await self._handle_generic_message(event)

    async def _handle_generic_message(self, event):
        """Handle generic messages."""
        message = self.message_pool.create_message(event)
        if message is None:
            return

        await self.message_processor.process_message(message)
        logger.log(LogLevel.Debug, f"Translated text: {message.output_text}")
        await self.client.send(message)
        if not message.approved:
            h = message.get_hash()
            await self.process_messages.set(h, message)
        logger.log(LogLevel.Debug, "Exiting handle_new_message")

    async def handle_restart_event(self, event):
        # await event.answer('Restarting')
        self.restart_event.set()
        self.stop_event.set()

    async def handle_callback_query(self, event):
        """Handle button interactions."""
        data = event.data.decode('utf-8')
        if data == 'restart':
            await event.answer('Restarting')
            self.restart_event.set()
            self.stop_event.set()

    async def handle_edited_messages(self, event):
        """Handle edited messages."""
        logger.log(LogLevel.Debug, "Handling edited message")
        if event.message.buttons is not None:
            try:
                logger.log(LogLevel.Debug, "Editing generated message")
                message_id = event.message.buttons[0][0].data.decode().split(":")[1]
                message = await self.process_messages.get(int(message_id))
                message.output_text = event.message.text
                return
            except Exception as e:
                logger.log(LogLevel.Error, f'Failed to edit message with buttons: {e}')
        if event.message.text.startswith('/role'):
            channel = self.channels.get_channel(event.chat.username)
            logger.log(LogLevel.Debug, f"Editing role {channel.role.name}")
            channel.role.from_text(event.message.text)

    async def handle_button_events(self, event):
        logger.log(LogLevel.Debug, "Handling button message")
        try:
            data = event.data.decode()

            # Handle direct command execution
            if data in self.command_processor.commands:
                await event.answer(f"Executing {data}")
                await self.command_processor.execute_command(data, event)
                return

            # Validate data format
            if ":" not in data:
                await event.respond("Unknown option selected.")
                return

            # Parse data and key
            action, key = data.split(":")
            message = await self.process_messages.get(int(key))

            # Handle missing messages
            if message is None and action != "delete":
                logger.log(LogLevel.Error, f"Message {key} not found.")
                await event.respond("Message not found.")
                return

            # Perform actions based on parsed data
            action_handlers = {
                "send": self._handle_send_action,
                "regenerate": self._handle_regenerate_action,
                "delete": self._handle_delete_action,
                "image": self._handle_image_action
            }

            handler = action_handlers.get(action, self._handle_unknown_action)
            await handler(event, message, key)
        except Exception as e:
            logger.log(LogLevel.Error, f"Error handling button event: {e}")
            await event.respond("An error occurred while processing the request.")

    async def _handle_send_action(self, event, message, key):
        try:
            message.approved = True
            await self.client.send(message)
        except Exception as e:
            logger.log(LogLevel.Error, f"Error in send action: {e}")

    async def _handle_regenerate_action(self, event, message, key):
        try:
            await self.message_processor.generate_text(message)
            await self.client.send(message)
            await self.client.client.delete_messages(event.chat_id, event.message_id)
        except Exception as e:
            logger.log(LogLevel.Error, f"Error in regenerate action: {e}")

    async def _handle_delete_action(self, event, message, key):
        try:
            await self.client.client.delete_messages(event.chat_id, event.message_id)
            await self.process_messages.delete(key)
        except Exception as e:
            logger.log(LogLevel.Error, f"Error in delete action: {e}")

    async def _handle_image_action(self, event, message, key):
        try:
            if not self.aiclient.is_on:
                await event.respond("The model is off. The image will not be generated.")
                return
            await event.respond("Generating new image. The media will be attached to the message when finished.")
            await self.aiclient.generate_image(message)
            await self.client.client.send_file(message.sender, message.media[0])
        except Exception as e:
            logger.log(LogLevel.Error, f"Error in image action: {e}")

    async def _handle_unknown_action(self, event, message, key):
        await event.respond("Unknown option selected.")

    def setup_event_handlers(self):
        self.client.set_up_handler(events.NewMessage(chats=self.channels.get_monitored()), self.handle_new_message)
        self.client.set_up_handler(events.CallbackQuery(), self.handle_callback_query)
        self.client.set_up_handler(events.MessageEdited(), self.handle_edited_messages)
        self.client.set_up_handler(events.CallbackQuery(), self.handle_button_events)

    # async def async_sender(self):
    #     while not self.stop_event.is_set() or not self.restart_event.is_set():
    #         message = self.delayed.

    async def stop_client(self):
        if self.client.is_connected():
            await self.client.disconnect()
            logger.log(LogLevel.Info, 'Client disconnected successfully')
        else:
            logger.log(LogLevel.Info, 'Client is not connected')

    async def run_client(self):
        """Run the Telegram client and handle messages."""
        logger.log(LogLevel.Info, "Connecting to Telegram Client")
        loop = asyncio.get_running_loop()
        setup_signal_handling(loop, self.stop_event)

        try:
            await self.client.start()
            logger.log(LogLevel.Info, 'Client started successfully')
            self.setup_event_handlers()
            self.is_running = True
            await self.stop_event.wait()
            logger.log(LogLevel.Info, 'Stop event received, shutting down...')
        except Exception as e:
            logger.log(LogLevel.Error, f'An error occurred: {e}')
            return 'fail'
        finally:
            self.is_running = False
            await self.stop_client()

        return 'restart' if self.restart_event.is_set() else 'success'
