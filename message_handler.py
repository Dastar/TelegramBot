import os
import asyncio
import time
from collections import defaultdict
from typing import Optional

from telethon.extensions import markdown
from logger import logger, LogLevel as Level
from ai_client.ai_client import AIClient
from channel_registry import ChannelRegistry
from simple_client import SimpleClient
from helpers.helpers import Helpers


class MessageHandler:
    def __init__(self, client, ai_client: AIClient, channels: ChannelRegistry, config):
        logger.log(Level.Debug, f"Creating Message Handler. Number of monitored channels: {len(channels.channels)}")
        self.client = SimpleClient(client, 'md')
        self.ai_client = ai_client
        self.channels = channels
        self.grouped_messages = defaultdict(list)
        self.grouped_files = defaultdict(list)
        self.grouped_timestamp = {}
        self.forwarded_message = config['forward_message']

    async def handle_new_message(self, event):
        """Handle new incoming messages."""
        logger.log(Level.Debug, "handle_new_message running")
        message = event.message
        channel = self.channels.get_channel(event.chat.username)
        if channel is None:
            logger.log(Level.Error, f'Target for {event.chat.username} not found.')
            return

        translated_text, media = await self.process_message(message, channel)

        logger.log(Level.Debug, f"Translated text: {translated_text}")
        await self.client.send(channel.target, translated_text, media)
        for m in media:
            os.remove(m)

        logger.log(Level.Debug, "Exiting handle_new_message")

    async def process_message(self, message, channel):
        """Process message content and media."""
        media = []
        translated_text = ""

        if message.grouped_id:
            logger.log(Level.Debug, 'Got grouped message')
            messages = await self.get_grouped_messages(message, message.grouped_id)
            if not messages:
                return "", []

            if message.text.strip() == '':
                for msg in self.grouped_messages[message.grouped_id]:
                    if msg.text.strip() != '':
                        message = msg

            media = self.grouped_files.pop(message.grouped_id, [])
        elif message.media:
            logger.log(Level.Debug, 'Got message with media')
            downloaded_media = await self.download_media(message)
            if downloaded_media:
                media.append(downloaded_media)

        message_text = markdown.unparse(message.message, message.entities)
        if message_text.startswith('/command:'):
            message_text = message_text[len('/command: '):]
            if message_text.startswith('generate image'):
                img = await self.ai_client.generate_image(message_text)
                if img.strip():
                    media.append(img)
        elif message_text.strip():
            logger.log(Level.Debug, 'Got message with text')
            message_text, code_blocks = Helpers.extract_code_blocks(message_text)
            translated_text = await self.ai_client.run_model(message_text, channel)
            translated_text = Helpers.insert_code_blocks(translated_text, code_blocks)
            translated_text = f"\u202B{translated_text}\u202C"

        if message.forward:
            logger.log(Level.Debug, 'Got forwarded message')
            original_sender = self.get_forward_name(message.forward)
            translated_text = f"{original_sender}{translated_text}"

        return translated_text, media

    def get_forward_name(self, forward):
        """Retrieve the name of the original sender of a forwarded message."""
        name = 'Unknown'
        if forward.sender:
            name = forward.sender.username
        elif forward.channel_post > 0:
            name = forward.chat.title
        return self.forwarded_message.replace('{name}', name).replace('{line}', '\n')

    async def grouped_messages_received(self, group_id):
        await asyncio.sleep(1)
        return time.time() - self.grouped_timestamp.get(group_id, 0) > 1

    @staticmethod
    async def download_media(message) -> Optional[str]:
        """Download media from a message."""
        try:
            file_path = await message.download_media()
            if file_path and os.path.exists(file_path):
                new_file_path = os.path.join("assets/download", file_path)
                logger.log(Level.Debug, f"Got media file: {new_file_path}")
                os.makedirs(os.path.dirname(new_file_path), exist_ok=True)
                os.rename(file_path, new_file_path)
                return new_file_path
            else:
                logger.log(Level.Error, f"File path does not exist: {file_path}")
                return None
        except Exception as e:
            logger.log(Level.Error, f"Error downloading media: {e}")
            return None

    async def get_grouped_messages(self, message, gid) -> list:
        """Retrieve grouped messages based on grouped ID."""
        logger.log(Level.Debug, f'Got message with grouped id {gid}')
        self.grouped_messages[gid].append(message)
        self.grouped_timestamp[gid] = time.time()

        if message.id == self.grouped_messages[gid][0].id:
            received = await self.grouped_messages_received(gid)
            if not received:
                received = await self.grouped_messages_received(gid)
            if not received:
                logger.log(Level.Error, 'Failed to receive all grouped messages.')

            logger.log(Level.Debug, f'Got {len(self.grouped_messages[gid])} messages with the same grouped id')
            messages = self.grouped_messages[gid]
            download_task = [asyncio.create_task(self.download_media(msg)) for msg in messages if msg.media]
            files = await asyncio.gather(*download_task)
            self.grouped_files[gid] = [f for f in files if f is not None]

            self.grouped_timestamp.pop(gid)
            return self.grouped_messages.pop(gid)
        else:
            return []


