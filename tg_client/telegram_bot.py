from telethon import TelegramClient, events
import asyncio


from configuration_readers.data_reader import DataReader
from configuration_readers.role_reader import RoleReader
from ai_client.ai_client import AIClient
from tg_client.channel_registry import ChannelRegistry
from configuration_readers.channel_reader import ChannelReader
from logger import LogLevel
from setup import logger
from events.event_handler import EventHandler
from setup import setup_signal_handling


class TelegramBot:
    def __init__(self, config):
        self.config = config
        self.aiclient = AIClient(self.config['api_key'])

        reader = DataReader(self.config['bot_config'])
        self.role_reader = RoleReader(reader)
        self.channel_reader = ChannelReader(self.role_reader, reader)

        self.channels = self._setup_channels()
        self.stop_event = asyncio.Event()
        self.restart_event = asyncio.Event()
        self.client = TelegramClient(self.config['session_name'], self.config['api_id'], self.config['api_hash'])
        self.message_handler = None

    def _setup_channels(self):
        """Set up channel registry and readers."""
        logger.log(LogLevel.Debug, "Setting up channels")
        channels = ChannelRegistry()
        for channel, sources in self.channel_reader.get_channels():
            channels.add_channels(channel, sources)
        return channels

    async def handle_new_message(self, event):
        await self.message_handler.handle_new_message(event)

    async def handle_callback_query(self, event):
        answer = await self.message_handler.handle_buttons(event)
        if answer == 'restart':
            self.restart_event.set()
            self.stop_event.set()

    async def handle_edited_messages(self, event):
        logger.log(LogLevel.Debug, f'Editing message with id {event.message.id} from {event.chat.username}')
        await self.message_handler.handle_edited_messages(event)

    def setup_event_handlers(self):
        self.client.on(events.NewMessage(chats=self.channels.get_monitored()))(self.handle_new_message)
        self.client.on(events.CallbackQuery())(self.handle_callback_query)
        self.client.on(events.MessageEdited())(self.handle_edited_messages)

    async def start_client(self):
        self.message_handler = EventHandler(self.client, self.aiclient, self.channels, self.config)
        await self.client.start()
        logger.log(LogLevel.Info, 'Client started successfully')

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
            await self.start_client()
            self.setup_event_handlers()
            await self.stop_event.wait()
            logger.log(LogLevel.Info, 'Stop event received, shutting down...')
        except Exception as e:
            logger.log(LogLevel.Error, f'An error occurred: {e}')
            return 'fail'
        finally:
            await self.stop_client()

        return 'restart' if self.restart_event.is_set() else 'success'
