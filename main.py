import os
import signal

import telethon
from openai import OpenAI
import asyncio
from read_config import configs
from enums import ConfigProperty
from logger import logger, LogLevel
from message_handler import MessageHandler
from ai_client.ai_client import AIClient

# configs.title = 'ALGO'
os.environ['OPENAI_API_KEY'] = configs.read(ConfigProperty.ApiKey)
openai_client = OpenAI(api_key=configs.read(ConfigProperty.ApiKey))
aiclient = AIClient(openai_client, role_file='ai_client/roles/role.yaml', language='Hebrew', model="gpt-4o")
aiclient.add_role('main')

api_id = configs.read(ConfigProperty.ApiId)
api_hash = configs.read(ConfigProperty.ApiHash)

# Replace with your channel usernames or IDs
monitored_channels = configs.read(ConfigProperty.MonitoredChannels)
target_channel = configs.read(ConfigProperty.TargetChannel)

# Initialize OpenAI API
openai_api_key = configs.read(ConfigProperty.ApiKey)


async def main():
    stop_event = asyncio.Event()

    async with telethon.TelegramClient('session_name', api_id, api_hash) as client:
        logger.log(LogLevel.Info, "Connected to Telegram Client")
        message_handler = MessageHandler(client, aiclient, [target_channel])

        @client.on(telethon.events.NewMessage(chats=monitored_channels))
        async def handle_message(event):
            logger.log(LogLevel.Debug, "Got new message, processing")
            await message_handler.handle_new_message(event)

        # Function to handle termination signals
        def signal_handler():
            logger.log(LogLevel.Info, 'Received termination signal, exiting...')
            stop_event.set()

        loop = asyncio.get_running_loop()

        # Register signal handlers
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
