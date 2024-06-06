from telethon import TelegramClient, events
import asyncio
from openai import OpenAI

from ai_client.role_reader import RoleReader
from ai_client.ai_client import AIClient
from channel_registry import ChannelRegistry
from channel_reader import ChannelReader
from logger import logger, LogLevel
from message_handler import MessageHandler
from setup import setup_signal_handling


def initialize_clients(config):
    """Initialize OpenAI and AI clients."""
    logger.log(LogLevel.Debug, "Initializing OpenAI client")
    openai_client = OpenAI(api_key=config['api_key'])
    aiclient = AIClient(openai_client, model="gpt-4o")
    return aiclient


def setup_channels(config):
    """Set up channel registry and readers."""
    logger.log(LogLevel.Debug, "Setting up channels")
    role_reader = RoleReader(config['role_file'])
    channel_reader = ChannelReader(config['channels_file'], role_reader)
    channels = ChannelRegistry()
    for m, ch in channel_reader.get_channels():
        channels.add_channels(ch, m)
    return channels


async def run_client(config, aiclient, channels):
    """Run the Telegram client and handle messages."""
    logger.log(LogLevel.Info, "Connecting to Telegram Client")
    stop_event = asyncio.Event()

    async with TelegramClient(config['session_name'], config['api_id'], config['api_hash']) as client:
        message_handler = MessageHandler(client, aiclient, channels, config)

        @client.on(events.NewMessage(chats=channels.get_monitored()))
        async def handle_message(event):
            logger.log(LogLevel.Debug, "Got new message, processing")
            await message_handler.handle_new_message(event)

        loop = asyncio.get_running_loop()
        setup_signal_handling(loop, stop_event)

        try:
            await client.start()
            logger.log(LogLevel.Info, 'Client started successfully')
            await stop_event.wait()
            logger.log(LogLevel.Info, 'Stop event received, shutting down...')
        except Exception as e:
            logger.log(LogLevel.Error, f'An error occurred: {e}')
        finally:
            if client.is_connected():
                await client.disconnect()
                logger.log(LogLevel.Info, 'Client disconnected successfully')
            else:
                logger.log(LogLevel.Info, 'Client is not connected')