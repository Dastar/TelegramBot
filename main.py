import os
import signal
import telethon
import asyncio
import sys
import ctypes

from openai import OpenAI
from ai_client.role_reader import RoleReader
from read_config import configs
from enums import ConfigProperty
from logger import logger, LogLevel
from message_handler import MessageHandler
from ai_client.ai_client import AIClient
from channel_registry import ChannelRegistry
from channel_reader import ChannelReader

# Read configuration values
os.environ['OPENAI_API_KEY'] = configs.read(ConfigProperty.ApiKey)
openai_client = OpenAI(api_key=configs.read(ConfigProperty.ApiKey))
aiclient = AIClient(openai_client, model="gpt-4o")

api_id = configs.read(ConfigProperty.ApiId)
api_hash = configs.read(ConfigProperty.ApiHash)

role_r = RoleReader(configs.read(ConfigProperty.RoleFile))
channel_r = ChannelReader(configs.read(ConfigProperty.ChannelsFile), role_r)
channels = ChannelRegistry()
for m, ch in channel_r.get_channels():
    channels.add_channels(ch, m)

# Initialize OpenAI API
openai_api_key = configs.read(ConfigProperty.ApiKey)

async def main():
    stop_event = asyncio.Event()

    async with telethon.TelegramClient('session_name', api_id, api_hash) as client:
        logger.log(LogLevel.Info, "Connected to Telegram Client")
        message_handler = MessageHandler(client, aiclient, channels)

        @client.on(telethon.events.NewMessage(chats=channels.get_monitored()))
        async def handle_message(event):
            logger.log(LogLevel.Debug, "Got new message, processing")
            await message_handler.handle_new_message(event)

        # Function to handle termination signals
        def signal_handler(sig=None, frame=None):
            logger.log(LogLevel.Info, 'Received termination signal, exiting...')
            stop_event.set()

        loop = asyncio.get_running_loop()

        if os.name == 'nt':
            # Windows-specific signal handling
            def win_signal_handler(dwCtrlType):
                signal_handler()
                return True

            ctypes.WinDLL('kernel32').SetConsoleCtrlHandler(ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_uint)(win_signal_handler), True)
        else:
            # Unix-like signal handling
            for sig in (signal.SIGINT, signal.SIGTERM):
                loop.add_signal_handler(sig, signal_handler)

        try:
            # Start the client
            await client.start()
            logger.log(LogLevel.Info, 'Client started successfully')

            # Wait until the stop event is set
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

if __name__ == '__main__':
    try:
        asyncio.run(main())
    finally:
        logger.log(LogLevel.Info, 'Event loop closed')
