import os
import asyncio
import time
from collections import defaultdict
import openai
from telethon.extensions import markdown
from telethon import types, errors
from simple_client import SimpleClient
from logger import logger, LogLevel as Level


class MessageHandler:
    def __init__(self, client, ai_client, target_channels):
        logger.log(Level.Debug, f"Creating Message Handler. Target channels: {target_channels}")
        self.client = SimpleClient(client, 'md')
        self.ai_client = ai_client
        self.target_channels = target_channels
        self.grouped_messages = defaultdict(list)
        self.grouped_files = defaultdict(list)
        self.grouped_timestamp = {}

    async def handle_new_message(self, event):
        logger.log(Level.Debug, "handle_new_message running")
        message = event.message
        media = []
        translated_text = ""

        logger.log(Level.Debug, f'Got message, text is: {message.message}')
        if message.grouped_id:
            logger.log(Level.Debug, f'Got grouped message')
            messages = await self.get_grouped_messages(message, message.grouped_id)
            # No need to continue with all grouped messages
            if len(messages) == 0:
                return

            # If message text is empty, search through all grouped messages for text
            if message.text.strip() == '':
                for msg in self.grouped_messages[message.grouped_id]:
                    if msg.text.strip() != '':
                        message = msg

            media = self.grouped_files.pop(message.grouped_id, [])
        elif message.media:
            logger.log(Level.Debug, f'Got message with media')
            downloaded_media = await self.download_media(message)
            if downloaded_media:
                media.append(downloaded_media)

        message_text = markdown.unparse(message.message, message.entities)
        if message_text.strip() != '':
            logger.log(Level.Debug, f'Got message with text')
            # Extracting code blocks
            message_text, code_blocks = self.extract_code_blocks(message_text)

            # Translate and rewrite text
            translated_text = await self.translate_and_rewrite_text(message_text)

            # Insert code blocks back into the translated text
            translated_text = self.insert_code_blocks(translated_text, code_blocks)

            # Adding right-to-left alignment characters
            translated_text = f"\u202B{translated_text}\u202C"

        if message.forward:
            logger.log(Level.Debug, f'Got forwarded message')
            original_sender = self.get_forward_name(message.forward)
            translated_text = f"Forwarded from {original_sender}: {translated_text}"

        logger.log(Level.Debug, f"Translated text: {translated_text}")

        for target in self.target_channels:
            await self.client.send(target, translated_text, media)

        logger.log(Level.Debug, "Exiting handle_new_message")

    def get_forward_name(self, forward):
        sender = 'Unknown'
        if forward.sender:
            sender = forward.sender.username
        elif forward.channel_post > 0:
            sender = forward.chat.title
        return sender

    async def grouped_messages_received(self, group_id):
        await asyncio.sleep(1)
        if time.time() - self.grouped_timestamp.get(group_id, 0) > 1:
            return True
        return False

    async def download_media(self, message) -> str | None:
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
        logger.log(Level.Debug, f'Got message with grouped id {gid}')
        # Saving grouped message
        self.grouped_messages[gid].append(message)
        self.grouped_timestamp[gid] = time.time()

        # Continue only with the first message
        if message.id == self.grouped_messages[gid][0].id:
            received = await self.grouped_messages_received(gid)
            if not received:
                received = await self.grouped_messages_received(gid)
            if not received:
                logger.log(Level.Error, f'Failed to receive all grouped messages.')

            logger.log(Level.Debug, f'Got {len(self.grouped_messages[gid])} messages with the same grouped id')

            # Download all media
            messages = self.grouped_messages[gid]
            download_task = [asyncio.create_task(self.download_media(msg)) for msg in messages if msg.media]
            files = await asyncio.gather(*download_task)
            self.grouped_files[gid] = [f for f in files if f is not None]

            # Cleaning and returning
            self.grouped_timestamp.pop(gid)
            return self.grouped_messages.pop(gid)
        else:
            return []

    def extract_code_blocks(self, text):
        import re
        code_block_pattern = re.compile(r'```.*?```', re.DOTALL)
        code_blocks = code_block_pattern.findall(text)
        for i, block in enumerate(code_blocks):
            text = text.replace(block, f"[CODE_BLOCK_{i}]")
        return text, code_blocks

    def insert_code_blocks(self, text, code_blocks):
        for i, block in enumerate(code_blocks):
            text = text.replace(f"[CODE_BLOCK_{i}]", block)
        return text

    async def translate_and_rewrite_text(self, text):
        logger.log(Level.Debug, "translate_and_rewrite_text running")
        retry_count = 0
        max_retries = 5
        backoff_factor = 2

        while retry_count < max_retries:
            error_message = '%%TRANSLATING FAILED%%'
            messages = [
                {
                    "role": "system",
                    "content": "You are a translator and rewriter."
                },
                {
                    "role": "user",
                    "content": f"This GPT is a tech writer and Hebrew language professional, tasked with translating "
                               f"every message received into Hebrew and rewriting it to fit the best manner for a tech "
                               f"blog format on Telegram. The GPT translate and rewrite and will return only a final "
                               f"version of the text of the actual message. this GPT will not translate the code blocks:\n\n{text}"
                }
            ]

            try:
                response = self.ai_client.chat.completions.create(model="gpt-3.5-turbo", messages=messages)
                content = response.choices[0].message.content.strip()
                logger.log(Level.Debug, "Got translated message, proceeding")
                return content
            except openai.RateLimitError as e:
                retry_count += 1
                wait_time = backoff_factor ** retry_count
                logger.log(Level.Warning, f"Rate limit exceeded. Retrying in {wait_time} seconds...")
                await asyncio.sleep(wait_time)
            except openai.OpenAIError as e:
                logger.log(Level.Error, f"An OpenAI error occurred: {e}")
                break
            except Exception as e:
                logger.log(Level.Error, f"An unexpected error occurred: {e}")
                break

        raise Exception("Max retries exceeded for OpenAI API request")
