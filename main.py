from telethon import TelegramClient, events, types
from openai import OpenAI
import openai
import os
import asyncio
from telethon.extensions import html
from read_config import configs
from enums import ConfigProperty
from logger import logger, LogLevel as Level
from message_handler import handle_new_message


client = OpenAI(api_key=configs.read(ConfigProperty.ApiKey))

api_id = configs.read(ConfigProperty.ApiId)
api_hash = configs.read(ConfigProperty.ApiHash)

# Replace with your channel usernames or IDs
monitored_channels = configs.read(ConfigProperty.MonitoredChannels)
target_channel = configs.read(ConfigProperty.TargetChannel)

# Initialize OpenAI API
openai_api_key = configs.read(ConfigProperty.ApiKey)


async def main():
    async with TelegramClient('session_name', api_id, api_hash) as client:
        logger.log(Level.Info, "Connected to Telegram Client")

        @client.on(events.NewMessage(chats=monitored_channels))
        async def handle_message(event):
            logger.log(Level.Debug, "Got new message, processing")
            await handle_new_message(event, client)

        try:
            # Start the client
            await client.start()
            logger.log(Level.Info, 'Client started successfully')

            # Run until disconnected
            await client.run_until_disconnected()
        except Exception as e:
            logger.log(Level.Error, f'An error occurred: {e}')
        finally:
            if client.is_connected():
                await client.disconnect()
                logger.log(Level.Info, 'Client disconnected successfully')
            else:
                logger.log(Level.Info, 'Client was not connected')

if __name__ == '__main__':
    asyncio.run(main())
